import unittest
from os import environ





from src.chatbot.instances import matchers










class WeaviateMatcherTest(unittest.TestCase):
    
    def test_match(self):
        to_test = matchers.WeaviateMatcher.match
        
        args = {
            "self": matchers.WeaviateMatcher(-80),
            "vector": [[0,1,1,1,0,0,0,0.5]],
            "knowledgebase": matchers.WeaviateKB("localhost", "711", "test_collection")
        }

        
        #test
        self.assertIsNotNone(to_test(**args))



class WeaviateQueryMatcherTest(unittest.TestCase):

    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_integration(self):
        to_test = matchers.WeaviateQueryMatcher.match

        args = {
            "self": matchers.WeaviateQueryMatcher(),
            "vector": None,
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION"))
        }

        
        self.assertIsNotNone(to_test(**args))
        

class WeaviateQueryKeyMatcherTest(unittest.TestCase):

    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_integration(self):
        to_test = matchers.WeaviateQueryKeyMatcher.match

        args = {
            "self": matchers.WeaviateQueryKeyMatcher("data"),
            "vector": None,
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION"))
        }

        
        self.assertIsNotNone(to_test(**args))