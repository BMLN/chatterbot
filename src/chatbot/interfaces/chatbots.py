from .chatbot import Chatbot
from .toolbox import ToolBox
from .arghandler import bind_args

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
        vec_args, match_args, instr_args, gen_args = self._bound_args(*list(args), **kwargs)


        if instructions:
            pass

        else:
            if context is None and self.matcher and self.knowledgebase:
                if not(context := self.matcher.match(text if not self.vectorizer else self.vectorizer.vectorize(text, *vec_args[0], *vec_args[1], **vec_args[2]), self.knowledgebase, *match_args[0], *match_args[1], **match_args[2])):
                    raise KnowledgeBot.NoContextError

            instructions = self.instructor.create_instructions(text, context, *instr_args[0], *instr_args[1], **instr_args[2])


        return self.generator.generate(*gen_args[0], **({k: v for d in instructions for k, v in d.items()} | gen_args[1] | gen_args[2]))






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
                    tool_args = bind_args(tool.apply, list(args), kwargs, ignore_until=1)
                    potential_response = tool.apply(text, *tool_args[0][1:], *tool_args[1], **tool_args[2])

                    if self.text_modifier:
                        text = self.text_modifier(potential_response)


                    if not self.evaluator:
                        return potential_response
                    
                    elif self.evaluator(response):
                        return potential_response

                except Exception as e:
                    pass
        
        raise ToolBox.ToolError()
        

