import unittest
from os import environ





from src.chatbot.instances import matchers










class WeaviateMatcherTest(unittest.TestCase):
    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    def test_match(self):
        to_test = matchers.WeaviateMatcher.match
        
        args = {
            "self": matchers.WeaviateMatcher(-80),
            "data": [[0,1,1,1,0,0,0,0.5]],
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), "test")
        }

        
        #test
        self.assertIsNotNone(to_test(**args))


    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    def test_keymatch(self):
        to_test = matchers.WeaviateKeyMatcher.match
        
        args = {
            "self": matchers.WeaviateKeyMatcher("solution"),
            "data": [[0,1,1,1,0,0,0,0.5]],
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), "test")
        }

        
        #test
        self.assertIsNotNone(to_test(**args))    





class WeaviateQueryMatcherTest(unittest.TestCase):

    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_match_integration(self):
        to_test = matchers.WeaviateQueryMatcher.match

        args = {
            "self": matchers.WeaviateQueryMatcher(),
            "data": None,
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION"))
        }


        #test
        self.assertIsNotNone(to_test(**args))
        
    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_keymatch_integration(self):
        to_test = matchers.WeaviateQueryKeyMatcher.match

        args = {
            "self": matchers.WeaviateQueryKeyMatcher("solution"),
            "data": None,
            "knowledgebase": matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION"))
        }


        #test
        print(to_test(**args))