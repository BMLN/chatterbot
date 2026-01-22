from ..interfaces.chatbot import Chatbot
from ..interfaces.batch import batchable
from inference.local.models import Tokenizer, Model, EmbeddingModel
from inference.local.memory import on_demand

# from sentence_transformers import SentenceTransformer
from transformers import AutoModel
from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer, DPRContextEncoder, DPRContextEncoderTokenizer
import torch
from numpy import array as np_array

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
        

class NoVectorizer(Chatbot.Vectorizer):

    @override
    @batchable(inherent=True)
    def vectorize(self, text):
        return text




#updated
class HFVectorizer(Chatbot.Vectorizer):
    
    
    def __init__(self, modelname):
        self.tokenizer = Tokenizer(modelname)
        self.vectorizer = EmbeddingModel(modelname, force_model=AutoModel)
    

    #!!!vectorizes into tensors!!! - Tensors could demand additional resources
    #!!!not anymore, since it shouldnt be needed in any way, right?
    @override
    @batchable(inherent="True")
    def vectorize(self, text):
        return self.vectorizer(**self.tokenizer(text, padding=True)).tolist()
        


class HFTokenPredictor(Chatbot.Vectorizer):
    
    @override
    def __init__(self, modelname):
        self.tokenizer = Tokenizer(modelname)
        self.model = Model(modelname)


    @override
    @batchable(inherent="True")
    def vectorize(self, text):
        return self.model(**self.tokenizer(text, padding=True)).logits[:, -1, :].tolist()
        


class HFTargetPredictor(HFTokenPredictor):
    """
        wraps the HFTokenPredictor output to only return the targeted tokens
    """

    @override
    def __init__(self, modelname, targets):
        assert isinstance(targets, (str, int)) or (isinstance(targets, list) and all(isinstance(x, (str, int)) for x in targets))

        super().__init__(modelname)

        if not isinstance(targets, list):
            self.targets = [ targets ]
        else:
            self.targets = targets
            
        #kinda unclean force loading to set
        if any(isinstance(x, str) for x in self.targets):
            self.tokenizer("")

        self.targets = [ self.tokenizer.model.convert_tokens_to_ids(x) if not isinstance(x, int) else x for x in self.targets ]


    @override
    @batchable(inherent=True)
    def vectorize(self, text):
        inference = super().vectorize(text) #or dont even as we lose direct indexing?
        inference = np_array(inference)[:, self.targets]

        return inference
        

    

    @classmethod
    def logsoftmax_prob(cls, token_scores):
        __tensor = torch.tensor(token_scores)
        __tensor = torch.log_softmax(__tensor, dim=1)
        output = __tensor.exp().tolist()
        del __tensor

        return output





class LightweightHFVectorizer(HFVectorizer):

    def __init__(self, modelname):
        super().__init__(modelname)
        
        self.tokenizer = on_demand(self.tokenizer)
        self.model = on_demand(self.model)