from abc import ABC, abstractmethod
from typing import override
from functools import wraps




class ToolBox(ABC):
    
    class ToolError(Exception):
        pass


    def __init__(self, toolset):
        assert all(isinstance(x, Tool) for x in toolset)
        
        self.toolset = toolset


    def __enter__(self):
        self.in_use = []
        return self

    def __exit__(self, exc_type, exc, tb):
        self.in_use = []


    @abstractmethod
    def get_tool(self):
        raise NotImplementedError


    
    # def respond(self, text):
    #     response = None
        
    #     with self.toolbox as tools:
    #         while (tool := tools.set_tool()) is None:
    #             try:
    #                 response = tool.apply(text)

    #                 if not self.evaluator:
    #                     return response
                    
    #                 elif self.evaluator(response):
    #                     return response

    #             except:
    #                 pass
        
    #     raise Exception("<todo>")
        


class Tool(ABC):

    @abstractmethod
    def apply(self, data, *args, **kwargs):
        raise NotImplementedError




def as_tool(apply_impl):
    def decorator(cls):        
        @wraps(cls, updated=())
        class Toolified(cls, Tool):
            @override
            def apply(self, data, *args, **kwargs):
                return apply_impl(self, data, *args, **kwargs)
        return Toolified

    return decorator