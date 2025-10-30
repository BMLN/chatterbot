import unittest






from src.chatbot.instances import matchers











class MatcherTest(unittest.TestCase):
    
    def test_match(self):
        to_test = matchers.WeaviateMatcher.match
        
        args = {
            "self": matchers.WeaviateMatcher(-80),
            "vector": [0,1,1,1,0,0,0,0.5],
            "knowledgebase": matchers.WeaviateKB("localhost", "711", "test_collection")
        }

        
        #test
        self.assertIsNotNone(to_test(**args))


        