import unittest
from unittest.mock import Mock



from src.chatbot.interfaces import chatbots
from src.chatbot.interfaces.toolbox import as_tool
from src.chatbot.instances.toolboxes import SequentialToolbox





class ToolbotTest(unittest.TestCase):
    
    @unittest.mock.patch("src.chatbot.interfaces.chatbots.Chatbot.respond", return_value="I responded!")
    def test_toolbot(self, mock_response):
        to_test = chatbots.ToolBot.respond

        #args        
        args = {
            "self": chatbots.ToolBot(SequentialToolbox([as_tool(chatbots.Chatbot.respond)(chatbots.Chatbot)()])),
            "text": "Respond to me!"
        }

        #test
        self.assertEqual(to_test(**args), "I responded!")




class MockedbotTest(unittest.TestCase):

    #comp defs
    class MockKB(chatbots.Chatbot.KnowledgeBase):
        def create(self, id, data, **args):
            return super().create(id, data, **args)
        def create_id(self, data):
            return super().create_id(data)
        def delete(self, id, **args):
            return super().delete(id, **args)
        def retrieve(self, id, **args):
            return super().retrieve(id, **args)
        def search(self, **args):
            return super().search(**args)
        def update(self, id, **args):
            return super().update(id, **args)

    class MockVec(chatbots.Chatbot.Vectorizer):
        def vectorize(self, text):
            return [0,1,0,1]
            
    class MockMatcher(chatbots.Chatbot.Matcher):
        def match(self, data, knowledgebase):
            return ["Doc1", "Doc2"]
            
    class ExtendedMockMatcher(MockMatcher):
        def match(self, data, knowledgebase, additional_context=None):
            return super().match(data, knowledgebase) + additional_context if additional_context else []

    class MockInstructor(chatbots.Chatbot.Instructor):
        def create_instructions(self, text, context, **args):
            return {}

    class MockGenerator(chatbots.Chatbot.Generator):
        def generate(self, **args):
            return "I generated!"
    
    
    

    def test_noargs(self):
        to_test = chatbots.Chatbot.respond

        #test
        result = to_test(
            chatbots.Chatbot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!"
        )
        self.assertEqual(result, "I generated!")


    def test_generalnoneargs(self):
        to_test = chatbots.Chatbot.respond

        #test
        result = to_test(
            chatbots.Chatbot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None
        )
        self.assertEqual(result, "I generated!")


    def test_additionalargs(self):
        to_test = chatbots.Chatbot.respond

        #test
        result = to_test(
            chatbots.Chatbot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None,
            data="somemore"
        )
        self.assertEqual(result, "I generated!")

    def test_additionalmatchingargs(self):
        to_test = chatbots.Chatbot.respond

        #test
        check_on = self.ExtendedMockMatcher()
        check_on.match = Mock()
        result = to_test(
            chatbots.Chatbot(
                self.MockKB(), 
                self.MockVec(), 
                self.ExtendedMockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None,
            additional_context=[["somemore"]]
        )
        self.assertEqual(result, "I generated!")





class MockedKnowledgebotTest(unittest.TestCase):

    #comp defs
    class MockKB(chatbots.Chatbot.KnowledgeBase):
        def create(self, id, data, **args):
            return super().create(id, data, **args)
        def create_id(self, data):
            return super().create_id(data)
        def delete(self, id, **args):
            return super().delete(id, **args)
        def retrieve(self, id, **args):
            return super().retrieve(id, **args)
        def search(self, **args):
            return super().search(**args)
        def update(self, id, **args):
            return super().update(id, **args)

    class MockVec(chatbots.Chatbot.Vectorizer):
        def vectorize(self, text):
            return [0,1,0,1]
            
    class MockMatcher(chatbots.Chatbot.Matcher):
        def match(self, data, knowledgebase):
            return ["Doc1", "Doc2"]
            
    class ExtendedMockMatcher(MockMatcher):
        def match(self, data, knowledgebase, additional_context=None):
            return super().match(data, knowledgebase) + additional_context if additional_context else []

    class MockInstructor(chatbots.Chatbot.Instructor):
        def create_instructions(self, text, context, **args):
            return {}

    class MockGenerator(chatbots.Chatbot.Generator):
        def generate(self, **args):
            return "I generated!"
    
    
    

    def test_noargs(self):
        to_test = chatbots.KnowledgeBot.respond

        #test
        result = to_test(
            chatbots.KnowledgeBot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!"
        )
        self.assertEqual(result, "I generated!")


    def test_generalnoneargs(self):
        to_test = chatbots.KnowledgeBot.respond

        #test
        result = to_test(
            chatbots.KnowledgeBot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None
        )
        self.assertEqual(result, "I generated!")


    def test_additionalargs(self):
        to_test = chatbots.KnowledgeBot.respond

        #test
        result = to_test(
            chatbots.KnowledgeBot(
                self.MockKB(), 
                self.MockVec(), 
                self.MockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None,
            data="somemore"
        )
        self.assertEqual(result, "I generated!")

    def test_additionalmatchingargs(self):
        to_test = chatbots.KnowledgeBot.respond

        #test
        check_on = self.ExtendedMockMatcher()
        check_on.match = Mock()
        result = to_test(
            chatbots.KnowledgeBot(
                self.MockKB(), 
                self.MockVec(), 
                self.ExtendedMockMatcher(),
                self.MockInstructor(),
                self.MockGenerator()
            ), 
            "Help me!",
            None, 
            None,
            additional_context=[["somemore"]]
        )
        self.assertEqual(result, "I generated!")