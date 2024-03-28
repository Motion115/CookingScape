from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("Dizex/FoodBaseBERT")
model = AutoModelForTokenClassification.from_pretrained("Dizex/FoodBaseBERT")

def ingredientsNER(text):
    pipe = pipeline("ner", model=model, tokenizer=tokenizer)
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