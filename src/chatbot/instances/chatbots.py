from ..interfaces.chatbot import Chatbot
from ..interfaces.toolbox import ToolBox


from typing import override







class KnowledgeBot(Chatbot):
    
    class NoContextError(Exception):
        pass


    @override
    def __init__(self, knowledgebase, vectorizer, matcher, instructor, generator):
        assert isinstance(knowledgebase, Chatbot.KnowledgeBase)
        assert isinstance(matcher, Chatbot.Matcher)
        
        super().__init__(knowledgebase, vectorizer, matcher, instructor, generator)


    @override
    def respond(self, text, context=None, instructions=None):
        if instructions:
            pass

        else:
            if context is None and self.knowledgebase and self.vectorizer and self.matcher:
                if not(context := self.matcher.match(self.vectorizer.vectorize(text), self.knowledgebase)):
                    raise KnowledgeBot.NoContextError

            if self.instructor:
                instructions = self.instructor.create_instructions(text, context)

        return self.generator.generate(**instructions)
    





class ToolBot(Chatbot):
    
    @override
    def __init__(self, toolbox: ToolBox, text_modifier=None, evaluator=None):
        assert isinstance(toolbox, ToolBox)

        super().__init__(None, None, None, None, None)
        self.toolbox = toolbox
        self.text_modifier = text_modifier
        self.evaluator = evaluator


    @override
    def respond(self, text):
        response = None
        
        with self.toolbox as toolbox:
            while (tool := toolbox.get_tool()) is not None:
                try:
                    potential_response = tool.apply(text)

                    if self.text_modifier:
                        text = self.text_modifier(potential_response)


                    if not self.evaluator:
                        return potential_response
                    
                    elif self.evaluator(response):
                        return potential_response

                except:
                    pass
        
        raise ToolBox.ToolError()
        

