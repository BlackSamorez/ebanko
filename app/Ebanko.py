import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
DEVICE = "cpu"

class Ebanko:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sberbank-ai/ruT5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("model").to(DEVICE)
    
    def toxify(self, context, temp=0.5):
        prefix_tokens = self.prepareInput(context).to(DEVICE)
        
        suffix_tokens = self.model.generate(prefix_tokens,
                                            do_sample=True,
                                            top_k=10,
                                            temperature=1.5)[0].cpu()
            
        return self.prepareOutput(suffix_tokens)
    
    def prepareInput(self, context):
        return self.tokenizer.encode(context, return_tensors='pt')
        
    def prepareOutput(self, tokens):
        return self.tokenizer.decode(tokens, skip_special_tokens=True)
