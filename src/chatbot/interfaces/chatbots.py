from .chatbot import Chatbot
from .toolbox import ToolBox


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
    def respond(self, text, context=None, instructions=None, *args, **kwargs):
        vec_args, match_args, instr_args, gen_args = self._bound_args(*args, **kwargs)


        if instructions:
            pass

        else:
            if context is None and self.knowledgebase and self.matcher:
                if not(context := self.matcher.match(text if not self.vectorizer else self.vectorizer.vectorize(text, **vec_args), self.knowledgebase, **match_args)):
                    raise KnowledgeBot.NoContextError

            if self.instructor:
                instructions = self.instructor.create_instructions(text, context, **instr_args)

        return self.generator.generate(**({k: v for d in instructions for k, v in d.items()} | gen_args))
    





class ToolBot(Chatbot):
    
    @override
    def __init__(self, toolbox: ToolBox, text_modifier=None, evaluator=None):
        assert isinstance(toolbox, ToolBox)

        super().__init__(None, None, None, None, None)
        self.toolbox = toolbox
        self.text_modifier = text_modifier
        self.evaluator = evaluator


    @override
    def respond(self, text, *args, **kwargs):
        response = None
        
        with self.toolbox as toolbox:
            while (tool := toolbox.get_tool()) is not None:
                try:
                    potential_response = tool.apply(text, **self._bound_args(tool.apply, *args, **kwargs))

                    if self.text_modifier:
                        text = self.text_modifier(potential_response)


                    if not self.evaluator:
                        return potential_response
                    
                    elif self.evaluator(response):
                        return potential_response

                except:
                    pass
        
        raise ToolBox.ToolError()
        

