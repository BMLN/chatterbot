from ..interfaces.chatbot import Chatbot, batchable
from ..instances.knowledgebases import WeaviateKB

from typing import override


class WeaviateMatcher(Chatbot.Matcher):
    

    def __init__(self, distance=-80):
        self.distance = distance



    @override
    @batchable(inherent=True)
    def match(self, vector, knowledgebase, **args):
        assert isinstance(knowledgebase, WeaviateKB)
        # return 
        #get only text
        dist = self.distance


        result = knowledgebase.search(vector, **args)
        result = list(map(lambda x: [ xx for xx in x if xx.get("distance", None) and xx.get("distance") > dist ], result))
        
        
        return result