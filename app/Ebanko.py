import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
DEVICE = "cpu"

class Ebanko:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sberbank-ai/ruT5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("model").to(DEVICE)
    
    def toxify(self, context, temp=1.5):
        prefix_tokens = self.prepareInput(context).to(DEVICE)
        
        suffix_tokens = self.model.generate(prefix_tokens,
                                            min_length=len(prefix_tokens) + 5,
                                            do_sample=True,
                                            top_k=5,
                                            temperature=temp)[0].cpu()
            
        return self.prepareOutput(suffix_tokens)
    
    def prepareInput(self, context):
        return self.tokenizer.encode(context, return_tensors='pt')
        
    def prepareOutput(self, tokens):
        return self.tokenizer.decode(tokens, skip_special_tokens=True)
