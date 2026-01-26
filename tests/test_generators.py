import unittest
from os import environ





from src.chatbot.instances import generators










class OllamaTest(unittest.TestCase):
    
    @unittest.skipUnless(environ.get("OLLAMA_URL"), "no env variable set")
    def test_GeneratorInit(self):
        to_test = generators.OllamaClient

        args = {
            "url": environ.get("OLLAMA_URL"),
            "model": "tinyllama"
        }


        #test
        self.assertIsNotNone(to_test(**args))



    @unittest.skipUnless(environ.get("OLLAMA_URL"), "no env variable set")
    def test_GeneratorInference(self):
        to_test = generators.OllamaClient.generate

        args = {
            "self": generators.OllamaClient(environ.get("OLLAMA_URL"), "tinyllama"),
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
