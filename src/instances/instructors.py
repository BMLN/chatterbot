from ..interfaces.chatbot import Chatbot


from typing import override







class OllamaContextInstructor(Chatbot.Instructor):

    #text should be the question
    @classmethod
    def create_instructions(cls, text, context=None):
        __context = "\\n".join([f"Context {i+1}: {x}" for i, x in enumerate(context)]) if context else None

        return {
            "system_content": "You are a helpful AI assistant.",
            "text_content": f"Question: {text}\\n{"Context:" + __context if context else ""}Answer:"
        }
    

#TODO: kwargs handling
class OllamaContextInstructor(Chatbot.Instructor):

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs


    #text should be the question
    @override
    def create_instructions(self, text, context=None, *args, **kwargs):
        __context = "\\n".join([f"Context {i+1}: {x}" for i, x in enumerate(context)]) if context else None

        # return {
        #     "prompt": f"Question: {text}\\n{"Context:" + __context if context else ""}Answer:"
        # } 

        return {
            "prompt": f"Given the following context: {context}, answer the following question: {text}"
        } | self.kwargs
    