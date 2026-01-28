from inspect import signature, Parameter
from typing import Callable, Tuple



def bind_args(func: Callable, args: list, kwargs: dict) -> Tuple[list, dict]:
    output = {}
    
    
    for name, value in signature(func).parameters.items():
        if value.kind is Parameter.VAR_POSITIONAL:
            output[name] = args

        elif value.kind is Parameter.VAR_KEYWORD:
            output[name] = kwargs
            
        elif args:
            output[name] = args.pop()
        
        elif name in kwargs:
            output[name] = kwargs.pop(name)
        
    return output 


