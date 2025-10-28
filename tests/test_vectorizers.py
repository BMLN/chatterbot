import unittest






from src.instances import vectorizers









class HFVectorizerTest(unittest.TestCase):
    
    def test_DPREncoding(self):
        to_test = vectorizers.HFVectorizer.vectorize


        args = {
            "self": vectorizers.HFVectorizer("facebook/dpr-ctx_encoder-multiset-base"),
            "text": "This is a test sentence."
        }
        result = to_test(**args)


        self.assertEqual(len(result[0]), 768)


    def test_qwenEncoding(self):
        to_test = vectorizers.HFVectorizer.vectorize


        args = {
            "self": vectorizers.HFVectorizer("Qwen/Qwen3-Embedding-4B"),
            "text": "This is a test sentence."
        }
        result = to_test(**args)

        self.assertEqual(len(result[0]), 2560)


    



#TODO
class LightweightHFVectorizerTest(unittest.TestCase):
    def test_lightweightDPREncoding(self):
        to_test = vectorizers.HFVectorizer.vectorize


        args = {
            "self": vectorizers.HFVectorizer("facebook/dpr-ctx_encoder-multiset-base"),
            "text": "This is a test sentence."
        }
        result = to_test(**args)


        self.assertEqual(len(result[0]), 768)

















if __name__ == "__main__":
    unittest.main()