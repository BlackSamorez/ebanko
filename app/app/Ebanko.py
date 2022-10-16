import torch

from transformers import AutoTokenizer, AutoModelForCausalLM
DEVICE = "cpu"

torch.set_num_threads(4)

class Ebanko:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("BlackSamorez/rudialogpt3_medium_based_on_gpt2_2ch")
        self.model = AutoModelForCausalLM.from_pretrained("model").to(DEVICE)

    def toxify(self, context, temp=1.0):
        prefix_tokens = self.prepareInput(context).to(DEVICE)

        suffix_tokens = self.model.generate(prefix_tokens,
                                            max_new_tokens=48,
                                            exponential_decay_length_penalty=(16, -0.02),
                                            bad_words_ids=[[self.tokenizer.pad_token_id]],
                                            repetition_penalty=10.,
                                            do_sample=True).cpu()[:, prefix_tokens.shape[-1]:][0]

        toxified = self.prepareOutput(suffix_tokens) 

        return toxified

    def prepareInput(self, context):
        prompt = ", a?"
        context = context + prompt + self.tokenizer.eos_token +  "|1|2|"
        return self.tokenizer.encode(context, return_tensors='pt')
        
    def prepareOutput(self, tokens):
        return self.tokenizer.decode(tokens, skip_special_tokens=True)
