import unittest






from src.chatbot.instances import instructors










class OllamaInstructorTest(unittest.TestCase):

    def test_instructor(self):
        to_test = instructors.OllamaContextInstructor.create_instructions

        args = {
            "self": instructors.OllamaContextInstructor(),
            "text": "This is a sample text.",
            "context": []
        }


        #test
        self.assertIn("prompt", str(to_test(**args)))


