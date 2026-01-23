from ..interfaces.chatbot import Chatbot, batchable
from ..instances.knowledgebases import WeaviateKB

from typing import override






class WeaviateMatcher(Chatbot.Matcher):
    
    def __init__(self, distance=-80):

        super().__init__()
        self.distance = distance


    @override
    @batchable(inherent=True)
    def match(self, data, knowledgebase, **args):
        assert isinstance(knowledgebase, WeaviateKB)

        result = knowledgebase.search(data, **args)
        result = list(map(lambda x: [ xx for xx in x if not self.distance or (xx.get("distance", None) and xx.get("distance") > self.distance) ], result))
        
        return result
    


class WeaviateKeyMatcher(WeaviateMatcher):

    @override
    def __init__(self, data_key, distance=None):
        super().__init__(distance)
        self.data_key = data_key


    @override
    @batchable(inherent=True) #TODO: recheck shared decoration here
    def match(self, data, knowledgebase, **args):

        results = super().match(data, knowledgebase, **args)
        results = [ [ xx.get("data").get(self.data_key) for xx in x ] for x in results ]
        

        return results
        





class WeaviateQueryMatcher(Chatbot.Matcher):

    def __init__(self, filter=None):

        super().__init__()
        self.filter = filter

    @override
    @batchable(inherent=True)
    def match(self, data, knowledgebase, **args):
        assert isinstance(knowledgebase, WeaviateKB)

        return knowledgebase.query(**({"filter": self.filter} | args))


class WeaviateQueryKeyMatcher(WeaviateQueryMatcher):

    def __init__(self, data_key, filter=None):
        super().__init__(filter)
        self.data_key = data_key

    @override
    def match(self, data, knowledgebase, **args):
        results = super().match(data, knowledgebase, **args)
        results = sorted(results, key= lambda x: x.get("data").get(self.data_key))
        results = [ x.get("data").get(self.data_key) for x in results ]

        return results