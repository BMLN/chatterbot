from ..interfaces.chatbot import Chatbot, batchable, batchify
from inference.local.models import Tokenizer, EmbeddingModel
from inference.local.memory import on_demand

# from sentence_transformers import SentenceTransformer
from transformers import AutoModel
from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer, DPRContextEncoder, DPRContextEncoderTokenizer
import torch


from typing import override

import warnings
warnings.filterwarnings(
    "ignore",
    message=".*encoder_attention_mask.*",
    category=FutureWarning,
)

# class TFIDFVectorizer():
#     pass


# # class TransformerVectorizer(Chatbot.Vectorizer):
# #     def __init__(self, model):
# #         assert isinstance(model, SentenceTransformer)

# #         super().__init__()
# #         self.model = model


# #     @override
# #     @batchable(inherent=True)
# #     def vectorize(self, text):
# #         return self.model.encode()
    

# class DPRQEncoder(Chatbot.Vectorizer):
#     def __init__(self, modelname):
#         super().__init__()
#         self.tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(modelname)
#         self.model = DPRQuestionEncoder.from_pretrained(modelname)


#     @override
#     @batchable(inherent=True)
#     def vectorize(self, text):
#         input_ids = self.tokenizer(text, return_tensors="pt", padding="True")["input_ids"]
#         embeddings = self.model(input_ids).pooler_output

#         return embeddings.detach().numpy()
    
# class DPRCEncoder(Chatbot.Vectorizer):
#     def __init__(self, modelname):
#         super().__init__()
#         self.tokenizer = DPRContextEncoderTokenizer.from_pretrained(modelname)
#         self.model = DPRContextEncoder.from_pretrained(modelname)

#     @override
#     @batchable(inherent=False)
#     def vectorize(self, text):
#         input_ids = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)["input_ids"]
#         embeddings = self.model(input_ids).pooler_output

#         return embeddings.detach().numpy()
    




# # class OnDemandDPREncoder(OnDemandModel, Chatbot.Vectorizer):
    
# #     def __init__(self, modelname):
# #         super().__init__(modelname)


# #     @override
# #     @batchable(inherent=False) #false should lower memory demand
# #     def vectorize(self, text):
# #         return self.__call__(text)


# #     @override
# #     def inference(self, text, *args, **kwargs):
# #         #print(text) #wo wirds tuple?
# #         inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        
# #         with torch.no_grad():
# #             outputs = self.model(**inputs)
            
# #             return outputs.pooler_output.squeeze().tolist()
        




#updated
class HFVectorizer(Chatbot.Vectorizer):
    
    
    def __init__(self, modelname):
        self.tokenizer = Tokenizer(modelname)
        self.vectorizer = EmbeddingModel(modelname, force_model=AutoModel)
    

    
    @override
    @batchify("text")
    @batchable(inherent="True")
    def vectorize(self, text):
        return self.vectorizer(**self.tokenizer(text))
        








class LightweightHFVectorizer(HFVectorizer):

    def __init__(self, modelname):
        super().__init__(modelname)
        
        self.tokenizer = on_demand(self.tokenizer)
        self.model = on_demand(self.model)