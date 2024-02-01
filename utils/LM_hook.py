import zhipuai
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

'''
This file stores the endpoints for several candidate LMs.

Web-based, large parameter size LLML
- ChatGLM @ Tsinghua KEG Group & Zhipu AI

Requires local implementation
- Qwen-1.8B-chat-int4 @ Alibaba / GPU: any GPU w/ more than 4G VRAM
'''


class GLM:
    def __init__(self, API_key_json):
        zhipuai.api_key = self.enable_API(API_key_json)
        
    def enable_API(self, API_key_json):
        # read json
        with open(API_key_json, 'r') as f:
            API_key = json.load(f)["zhipu_api"]
        return API_key


    def call_once(self, prompt, temperature=0.3, top_p=0.8):
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_std",
            prompt = [{
                "role": "user",
                "content": prompt
                }],
            temperature= temperature,
            top_p= top_p,
            incremental=True
        )
        response_from_llm = ""
        for event in response.events():
            if event.event == "add":
                response_from_llm += event.data
                # print(event.data, end="")
            elif event.event == "error" or event.event == "interrupted":
                response_from_llm += event.data
                print(event.data, end="")
            elif event.event == "finish":
                response_from_llm += event.data
                # print(event.data)
                # print(event.meta, end="")
            else:
                response_from_llm += event.data
                # print(event.data, end="")
        # print(response_from_llm)
        return response_from_llm
    
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