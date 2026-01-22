import unittest
from os import environ





from src.chatbot.instances import matchers










class WeaviateMatcherTest(unittest.TestCase):
    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    def test_match(self):
        to_test = matchers.WeaviateMatcher.match
        
        args = {
            "self": matchers.WeaviateMatcher(
                matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), "test_collection"), 
                -80
            ),
            "data": [[0,1,1,1,0,0,0,0.5]],
        }

        
        #test
        self.assertIsNotNone(to_test(**args))


    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    def test_keymatch(self):
        to_test = matchers.WeaviateKeyMatcher.match
        
        args = {
            "self": matchers.WeaviateKeyMatcher(
                matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), "test_collection"),
                "text", 
            ),
            "data": [[0,1,1,1,0,0,0,0.5]],
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
            "self": matchers.WeaviateQueryMatcher(matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION"))),
            "data": None,
        }


        #test
        self.assertIsNotNone(to_test(**args))
        
    
    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_integration(self):
        to_test = matchers.WeaviateQueryKeyMatcher.match

        args = {
            "self": matchers.WeaviateQueryKeyMatcher(matchers.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION")), "data"),
            "data": None
        }


        #test
        print(to_test(**args))