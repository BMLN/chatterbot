import unittest
from unittest.mock import MagicMock





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