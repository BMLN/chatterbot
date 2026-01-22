from ..interfaces.chatbot import Chatbot, batchable
from ..instances.knowledgebases import WeaviateKB

from typing import override






class WeaviateMatcher(Chatbot.Matcher):
    
    def __init__(self, weaviatekb, distance=-80):
        assert isinstance(weaviatekb, WeaviateKB)

        super().__init__()
        self.kb = weaviatekb
        self.distance = distance


    @override
    @batchable(inherent=True)
    def match(self, data, **args):

        result = self.kb.search(data, **args)
        result = list(map(lambda x: [ xx for xx in x if not self.distance or (xx.get("distance", None) and xx.get("distance") > self.distance) ], result))
        
        return result
    


class WeaviateKeyMatcher(WeaviateMatcher):

    @override
    def __init__(self, weaviatekb, data_key, distance=None):
        super().__init__(weaviatekb, distance)
        self.data_key = data_key


    @override
    @batchable(inherent=True) #TODO: recheck shared decoration here
    def match(self, data, **args):

        results = super().match(data, **args)
        results = [ [ xx.get("data").get(self.data_key) for xx in x ] for x in results ]
        

        return results
        





class WeaviateQueryMatcher(Chatbot.Matcher):

    def __init__(self, weaviatekb, filter=None):
        assert isinstance(weaviatekb, WeaviateKB)

        super().__init__()
        self.kb = weaviatekb
        self.filter = filter

    @override
    @batchable(inherent=True)
    def match(self, data=None, **args):
        return self.kb.query(**({"filter": self.filter} | args))


class WeaviateQueryKeyMatcher(WeaviateQueryMatcher):

    def __init__(self, weaviatekb, data_key, filter=None):
        super().__init__(weaviatekb, filter)
        self.data_key = data_key

    @override
    def match(self, data=None, **args):
        results = super().match(data, **args)
        results = sorted(results, key= lambda x: x.get("data").get(self.data_key))
        results = [ x.get("data").get(self.data_key) for x in results ]

        return results