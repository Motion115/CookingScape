from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import nltk

# if the nltk packages are not ready, this will download them automatically
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)

class foodNER:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Dizex/FoodBaseBERT")
        self.model = AutoModelForTokenClassification.from_pretrained("Dizex/FoodBaseBERT")

    def extractEntityFromSteps(self, cookingSteps, isLemmantize = True):
        foodEntities = set()
        for key, value in cookingSteps.items():
            for sentence in value:
                foodEntities = set(self.ingredientsNER(sentence)) | foodEntities
        foodEntities = list(foodEntities)
        if isLemmantize:
            foodEntities = self._lemmantizeEntities(foodEntities)
        return foodEntities
    
    def _lemmantizeEntities(self, foodEntities):
        lemmatizer = nltk.stem.WordNetLemmatizer()
        ingreditentsList = set()
        for word in foodEntities:
            tokenized_word = nltk.word_tokenize(word)
            # reduce the word to the raw form
            lemmatized_word = [lemmatizer.lemmatize(word) for word in tokenized_word]
            # tag position of speech
            pos_tagged_word = nltk.pos_tag(lemmatized_word)       
            ingredientName = []
            for token, pos in pos_tagged_word:
                if pos.startswith('N'):
                    ingredientName.append(token)
            if ingredientName:
                ingredientName = ' '.join(ingredientName)
                ingreditentsList.add(ingredientName)
        return list(ingreditentsList)

    def ingredientsNER(self, text):
        pipe = pipeline("ner", model=self.model, tokenizer=self.tokenizer)
        ner_entity_results = pipe(text)
        merged_entities = []
        for result in ner_entity_results:
            entity, word = result["entity"] ,result["word"]
            if entity == "B-FOOD":
                if word.startswith("##"):
                    merged_entities[-1] += word[2:]
                else:
                    merged_entities.append(word)
            elif entity == "I-FOOD":
                if word.startswith("##"):
                    merged_entities[-1] += word[2:]
                else:
                    merged_entities[-1] += " " + word
            else:
                print("Error in NER result")
        
        return merged_entities