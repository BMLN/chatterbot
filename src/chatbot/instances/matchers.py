from ..interfaces.chatbot import Chatbot, batchable, batchify
from ..instances.knowledgebases import WeaviateKB
from weaviate.classes.query import Filter 

from typing import override






class WeaviateMatcher(Chatbot.Matcher):
    
    def __init__(self, distance=-80):

        super().__init__()
        self.distance = distance


    @override
    @batchify("data", list[list[float]])
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
        # assert not filter or isinstance(filter, Filter) or callable(filter), type(filter) #weaviate api not stable
        
        super().__init__()
        self.filter = filter

    @override
    @batchable(inherent=True)
    def match(self, data, knowledgebase, *args, **kwargs):
        assert isinstance(knowledgebase, WeaviateKB)

        return knowledgebase.query(filter= None if not self.filter else self.filter(*args, **kwargs) if callable(self.filter) else self.filter)


class WeaviateQueryKeyMatcher(WeaviateQueryMatcher):

    def __init__(self, data_key, filter=None):
        super().__init__(filter)
        self.data_key = data_key

    @override
    @batchable(inherent=True)
    def match(self, data, knowledgebase, *args, **kwargs):
        results = super().match(data, knowledgebase, *args, **kwargs)
        results = sorted(results, key= lambda x: x.get("data").get(self.data_key) or "")
        results = [ x.get("data").get(self.data_key, None) for x in results ]

        return results
    
