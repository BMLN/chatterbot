import unittest






from src.chatbot.instances import generators










class OllamaTest(unittest.TestCase):
    
    
    def test_GeneratorInit(self):
        to_test = generators.OllamaClient

        args = {
            "url": "localhost:11434",
            "model": "tinyllama"
        }


        #test
        self.assertIsNotNone(to_test(**args))




    def test_GeneratorInference(self):
        to_test = generators.OllamaClient.generate

        args = {
            "self": generators.OllamaClient("localhost:11434", "tinyllama"),
            "prompt": "Hello?"
        }


        #test
        self.assertIsInstance(to_test(**args), str)




class DeepinfraTest(unittest.TestCase):

    def test_GeneratorInit(self):
        to_test = generators.DeepInfraClient

        args = {"model": "openai/gpt-oss-120b"}


        #test
        self.assertIsNotNone(to_test(**args))      



    def test_GeneratorInference(self):
        to_test = generators.DeepInfraClient.generate

        args = {
            "self": generators.DeepInfraClient("openai/gpt-oss-120b"),
            "prompt": "Hello?"
        }


        #test
        self.assertIsInstance(to_test(**args), str)
