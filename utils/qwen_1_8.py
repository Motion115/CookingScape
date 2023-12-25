
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

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
            trust_remote_code=True
        ).eval()
        return tokenizer, model

    def call(self, context, system_instruction=""):
        # clear cache with torch
        torch.cuda.empty_cache()
        response, history = self.model.chat(self.tokenizer, context, history=None, system=system_instruction)
        return response