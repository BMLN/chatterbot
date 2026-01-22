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
    




class WeaviateKeyMatcher(WeaviateMatcher):

    @override
    def __init__(self, data_key, distance=None):
        super().__init__(distance)
        self.data_key = data_key


    @override
    @batchable(inherent=True) #TODO: recheck shared decoration here
    def match(self, vector, knowledgebase, **args):
        assert isinstance(knowledgebase, WeaviateKB)

        dist = self.distance

        result = knowledgebase.search(vector, **args)
        result = list(map(
            lambda x: [ 
                xx.get("data").get(self.data_key) 
                for xx in x 
                if not dist or (xx.get("distance", None) and xx.get("distance") > dist) 
            ],
            result
        ))
        
        
        return result
        

class WeaviateQueryMatcher(Chatbot.Matcher):

    def __init__(self, filter=None):
        super().__init__()
        self.filter = filter

    @override
    def match(self, vector, knowledgebase, **args):
        return knowledgebase.query(**({"filter": self.filter} | args))


class WeaviateQueryKeyMatcher(WeaviateQueryMatcher):

    def __init__(self, data_key, filter=None):
        super().__init__(filter)
        self.data_key = data_key

    @override
    def match(self, vector, knowledgebase, **args):
        results = super().match(vector, knowledgebase, **args)
        results = [ x.get("data").get(self.data_key) for x in results ]

        return results