import zhipuai
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    PromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, JsonOutputParser, NumberedListOutputParser, MarkdownListOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field

'''
This file stores the endpoints for several candidate LMs.

Web-based, large parameter size LLM
- ChatGLM @ Tsinghua KEG Group & Zhipu AI

Requires local implementation
- Qwen-1.8B-chat-int4 @ Alibaba / GPU: any Nvidia GPU w/ more than 4G VRAM
'''


class CookingSteps(BaseModel):
    preparation: str = Field(description="Content under preparation phase")
    cooking: str = Field(description="Content under cooking phase")
    assembly: str = Field(description="Content under assembly phase")

class RatingData(BaseModel):
    rating: int = Field(description="Difficulty rating of the recipe")
    comments: str = Field(description="Reason for the rating")

class ReplacementData(BaseModel):
    isReplacable: bool = Field(description="Whether the ingredient can be replaced")
    explaination: str = Field(description="Explanation")


class GLM_langchain:
    def __init__(self, token):
        self.llm = ChatOpenAI(
            model_name="glm-3-turbo",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4",
            openai_api_key=token,
            streaming=False,
            temperature=0.01,
        )

    def backtraceIngredients(self, ingredientsList, recipeList):
        '''
        Deprecated function. LLMs perform not well with ingredients work.
        '''
        ingredientsStr = ", ".join(ingredientsList)
        recipeStr = " ".join(recipeList)
        # definition of ingredients from collins dictionary
        ingredientProcessor = PromptTemplate(
            input_variables=["ingredientsStr"],
            template='''
                You are a helpful assistant.\
                You will be provided with some food entities extracted from a recipe.\
                Your task is to identify which of them are ingredients using the following definition.\

                Definition: Ingredients are the things that are used to make something, especially all the different foods you use when you are cooking a particular dish.\
                Ingredients should be in its raw form, the outcomes that is made from ingredients should not be classified as ingredients.\
                Additionally, ingredients used to make the sides of a dish should also be included.\

                Think step-by-step:\
                - First, read the recipe script provided to get the context of the recipe.\
                - Then, analyze with consideration of the recipe whether the each food entity align with the definition.\
                Provide your thinking process in the analysis.

                Recipe: {recipeStr}

                Ingredients: {ingredientsStr}
            ''',
            # partial_variables={"format_instructions": format_instructions},
        )
        chain = (
            {"ingredientsStr": RunnablePassthrough(),
             "recipeStr": RunnablePassthrough()}
            | ingredientProcessor
            | self.llm
            | StrOutputParser()
        )
        analysisScript = chain.invoke({
            "ingredientsStr": ingredientsStr,
            "recipeStr": recipeStr})

        # print(analysisScript)

        listParser = MarkdownListOutputParser()
        listParserInstruction = listParser.get_format_instructions()
        ingredientsExtractor = PromptTemplate(
            input_variables=["anaylsisResult"],
            template='''
                You are a helpful assistant.
                Your task is to read the analysis script and extract the ingredients in the recipe.

                You should return the result without the analysis.\
                Meanwhile, correct the name of the ingredients if it is not aligned with the convention.\
                Use bullet points to separate the ingredients.

                Analysis: {analysisResult}
            ''',
            partial_variables={"format_instructions": listParserInstruction},
        )

        ingredientsExtractorChain = (
            {"analysisResult": RunnablePassthrough()}
            | ingredientsExtractor
            | self.llm
            | listParser
        )
        renewedIngredientList = ingredientsExtractorChain.invoke(analysisScript)
        # print(renewedIngredientList)
        return renewedIngredientList
    
    def getCookingSteps(self, transcript):
        cookingStepsProcessor = PromptTemplate(
            input_variables=["transcript"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Your task is to divide the cooking into 3 phases: preparation, cooking, and assembly.\
                
                Think step by step.
                First, Write the subtasks in their unit form (using around 10 words), which means no further separation can be found in this process.
                When writing each subtask, make sure to use the format: verb + ingredient + cooking utensil.
                Examples:
                  1) Fry rice with high heat. 
                  2) Sear steak on a cast iron pan. 
                  3) Dice shallots on chopping board.

                Then, after extracting all the subtasks, try to categorize the steps into preparation, cooking, and assembly.
                The definition of preparation, cooking and assembly are as follows:
                  1) Preparation is the stage where raw ingredients are prepared, such as mixing, chopping, grating, etc. No heating, i.e., using temperature to cook ingredients, is allowed during this stage.\
                  2) Cooking is the stage where ingredients are cooked, such as boiling, frying, baking, etc.\
                  3) Assembly is the stage where cooked ingredients are assembled into a finished dish.\
                Put the definition in mind when grouping the subtasks. You should also maintain the correct sequence of subtasks.
                
                Transcript:{transcript}
            ''',
        )
        chain = (
            {"transcript": RunnablePassthrough()}
            | cookingStepsProcessor
            | self.llm
            | StrOutputParser()
        )

        cookingStepsRaw = chain.invoke(transcript)


        json_parser = JsonOutputParser(pydantic_object=CookingSteps)
        cookStepOrganizer = PromptTemplate(
            input_variables=["description"],
            template='''
                You are a helpful assistant. 
                You are provided with a list of cooking steps, that has already been organized to three stages, including preparation, cooking, and assembly.

                Orgainze the content you are given into three stages, each containing a list of cooking steps.
                The JSON keys are "preparation", "cooking", and "assembly". 
                The JSON content should be a list that include all the step within this stage. Separate the steps in comma, and wrap the steps in string.            
                Content: 
                {description}
            ''',
            partial_variables={
                "format_instructions": json_parser.get_format_instructions()},
        )

        cookStepOrganizerChain = (
            {"description": RunnablePassthrough()}
            | cookStepOrganizer
            | self.llm
            | json_parser
        )

        cookingStepsFormatted = cookStepOrganizerChain.invoke(cookingStepsRaw)
        return cookingStepsFormatted

    def getSequentialCookingSteps(self, transcript):
        numberedListParser = NumberedListOutputParser()
        formatInstruction = numberedListParser.get_format_instructions()
        cookingStepsProcessor = PromptTemplate(
            input_variables=["transcript"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Your task is to provide a step-by-step summary of the recipe.\
                Use approximately 15 words to describe each step.

                Organize the recipe into a numbered list.
                                
                Transcript:{transcript}
            ''',
            partial_variables={"format_instructions": formatInstruction},
        )
        chain = (
            {"transcript": RunnablePassthrough()}
            | cookingStepsProcessor
            | self.llm
            | numberedListParser
        )
        cookingSteps = chain.invoke(transcript)
        return cookingSteps
    
    def getRating(self, transcript):
        json_parser = JsonOutputParser(pydantic_object=RatingData)
        ratingProcessor = PromptTemplate(
            input_variables=["transcript"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Based on the difficulty of this recipe, provide a rating of the recipe from 1 to 5.

                The definition for difficulty is as follows:
                1 - Easy: Requires little, to basic cooking skills and needs common ingredients (or offers easily found substitutions).
                2 - Begineer: Requires some experience, and some prep, but not much cooking time.
                3 - Intermediate: Requires more experience, more prep and cooking time (possibly cooking several things within the time), and maybe some ingredients you don't already have in your kitchen (but should still be able to find at your local grocery store).
                4 - Advanced: Requires a lot of prep, a lot of cooking time, and some special ingredients or equipment.
                5 - Hard: Challenging recipes that require more advanced skills and experience (will almost defiantly require you to make/prep multiple things) and maybe some special equipment and Ingredients.
             
                Transcript:{transcript}
                
                Think step by step. You should provide an overall rating, and why you chose that rating. You should decribe your reasoning in around 100 words.
                Organize your response in a JSON format with the following keys: "rating" and "reason".
            ''',
            partial_variables={
                "format_instructions": json_parser.get_format_instructions()},
        )

        chain = (
            {"transcript": RunnablePassthrough()}
            | ratingProcessor
            | self.llm
            | json_parser
        )
        rating = chain.invoke(transcript)
        return rating

    def explainIngredient(self, transcript, ingredient):
        explanationProcessor = PromptTemplate(
            input_variables=["transcript", "ingredient"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Explain the use of `{ingredient}` in the recipe. At what step does it come into play? What is its purpose?

                Your response should be in around 100 words.

                Transcript:{transcript}
            '''
        )
        chain = (       
            {"transcript": RunnablePassthrough(), "ingredient": RunnablePassthrough()}
            | explanationProcessor
            | self.llm
            | StrOutputParser()
        )
        explanation = chain.invoke({
            "transcript":transcript,
            "ingredient":ingredient
            })
        return explanation
    
    def exploreAlternativeIngredient(self, transcript, usedIngredient, newIngredient):
        json_parser = JsonOutputParser(pydantic_object=ReplacementData)
        explanationProcessor = PromptTemplate(
            input_variables=["transcript", "usedIngredient", "newIngredient"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Use your culinary knowldege. 
                Can `{newIngredient}` be used as an alternative to `{usedIngredient}`?

                An ingredient is considered replacable if it serves the same purpose as the original ingredient without creating unexpected sideeffects.

                Think step by step. 
                First, provide if `{newIngredient}` can be used as an alternative to `{usedIngredient}` with a boolean answer (true or false).
                Then, provide explaination for your decision in around 100 words.
                Organize your response in a JSON format with the following keys: "isReplacable" and "explaination".
                
                Transcript:{transcript}
            ''',
            partial_variables={
                "format_instructions": json_parser.get_format_instructions()},
        )
        chain = (
            {"transcript": RunnablePassthrough(), "usedIngredient": RunnablePassthrough(), "newIngredient": RunnablePassthrough()}
            | explanationProcessor
            | self.llm
            | json_parser
        )
        explanation = chain.invoke({   
            "transcript":transcript,
            "oldIngredient": usedIngredient,
            "newIngredient":newIngredient
        })
        return explanation
    





"""
        listParser = CommaSeparatedListOutputParser()
        format_instructions = listParser.get_format_instructions()

        ingredientProcessor = PromptTemplate(
            input_variables=["summarySteps"],
            template='''
                You are a helpful assistant. You will be provided with the steps of cooking a dish.
                Your task is to extract the ingredients from the steps.

                Steps:{summarySteps}

                Supress any non-ingredient text. Return with ingredients separated by commas, do not return punctuations other than commas.
            ''',
            partial_variables={"format_instructions": format_instructions},
        )
"""


class Qwen1_8:
    def __init__(self, model_directory):
        self.model_directory = model_directory
        self.tokenizer, self.model = self.load_model()

    def load_model(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_directory, trust_remote_code=True)
        # Since transformers 4.35.0, the GPT-Q/AWQ model can be loaded using AutoModelForCausalLM.
        model = AutoModelForCausalLM.from_pretrained(
            self.model_directory,
            device_map="cuda:0",
            torch_dtype='auto',
            # top_p=0.8,
            # temperature=0.1,
            trust_remote_code=True
        ).eval()
        return tokenizer, model

    def call(self, context, system_instruction=""):
        # clear cache with torch
        torch.cuda.empty_cache()
        response, history = self.model.chat(
            self.tokenizer, context, history=None, system=system_instruction)
        return response
