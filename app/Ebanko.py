import torch

from transformers import AutoTokenizer, AutoModelForCausalLM

DEVICE = "cpu"

class Bot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sberbank-ai/ruT5-base")
        self.model = AutoModelForCausalLM.from_pretrained("model").to(DEVICE)
        
    def getResponses(self, context, n = 1, temp=0.5):
        return [self.getResponse(context, temp=temp) for _ in range(n)]

    def getResponse(self, context, temp=0.5):
        prefix_tokens = self.prepareInput(context)
        
        suffix_tokens = self.model.generate(prefix_tokens,
                                            do_sample=True,
                                            top_k=10,
                                            temperature=1.5)[0].cpu()
            
        return self.prepareOutput(suffix_tokens)
    
    def prepareInput(self, context):
        return self.tokenizer.encode(context, return_tensors='pt')
        
    def prepareOutput(self, tokens):
        return self.tokenizer.decode(tokens, skip_special_tokens=True)