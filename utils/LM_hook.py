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
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field

'''
This file stores the endpoints for several candidate LMs.

Web-based, large parameter size LLM
- ChatGLM @ Tsinghua KEG Group & Zhipu AI

Requires local implementation
- Qwen-1.8B-chat-int4 @ Alibaba / GPU: any GPU w/ more than 4G VRAM
'''

class CookingSteps(BaseModel):
    preparation: str = Field(description="Content under preparation phase")
    cooking: str = Field(description="Content under cooking phase")
    assembly: str = Field(description="Content under assembly phase")

class GLM_langchain:
    def __init__(self, token):
        self.llm = ChatOpenAI(
            model_name="glm-3-turbo",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4",
            openai_api_key=token,
            streaming=False,
            temperature=0.01
        )

    def call(self, transcript):
        cookingStepsProcessor = PromptTemplate(
            input_variables=["transcript"],
            template='''
                You are a helpful assistant. You will be provided with the transcript of a cooking video.
                Your task is to divide the cooking into 3 phases: preparation, cooking, and assembly.\
                
                Preparation is the stage where raw ingredients are prepared, such as mixing, chopping, and grating etc. No heating is allowed during this stage.\
                Cooking is the stage where ingredients are cooked, such as boiling, frying, and baking etc.\
                Assembly is the stage where cooked ingredients are assembled into a finished dish.\
                
                Think step by step. First, Write the subtasks in its unit form, which means no further separtaion can be found in this process.
                Then, after extracting all the subtasks, try to categorize the step into preparation, cooking, and assembly.
                
                Transcript:{transcript}
            ''',
        )
        output_parser = StrOutputParser()
        chain = (
            {"transcript": RunnablePassthrough()} 
            | cookingStepsProcessor
            | self.llm
            | output_parser
        )

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


        ingredientProcessorChain = (
            {"summarySteps": RunnablePassthrough()}
            | ingredientProcessor
            | self.llm
            | listParser
        )

        a = chain.invoke(transcript)
        print(a)

        #b = ingredientProcessorChain.invoke(a)
        #print(b)

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
            partial_variables={"format_instructions": json_parser.get_format_instructions()},
        )

        cookStepOrganizerChain = (
            {"description": RunnablePassthrough()}
            | cookStepOrganizer
            | self.llm
            | json_parser
        )
        
        c = cookStepOrganizerChain.invoke(a)
        print(c)

        # extract


class Qwen1_8:
    def __init__(self, model_directory):
        self.model_directory = model_directory
        self.tokenizer, self.model = self.load_model()

    def load_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.model_directory, trust_remote_code=True)
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
        response, history = self.model.chat(self.tokenizer, context, history=None, system=system_instruction)
        return response