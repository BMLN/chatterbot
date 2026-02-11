from inspect import signature, Parameter
from typing import Callable, Tuple



def bind_args(func: Callable, args: list, kwargs: dict, ignore_until=None) -> Tuple[list, dict]:
    func_args = []
    var_pos_args = []
    var_kw_args = {}
    
    
    for i, param in enumerate(signature(func).parameters.items()):
        name, value = param

        if ignore_until:
            if isinstance(ignore_until, int):
                if i < ignore_until:
                    continue
            elif isinstance(ignore_until, str):
                if not name == ignore_until:
                    continue
                else:
                    ignore_until = i

            else:
                raise ValueError(ignore_until)

        if value.kind is Parameter.VAR_POSITIONAL:
            var_pos_args = args

        elif value.kind is Parameter.VAR_KEYWORD:
            var_kw_args = kwargs
            
        elif args:
            func_args.append(args.pop(0))
        
        elif name in kwargs:
            func_args.append(kwargs.pop(name))
        

        else:
            raise KeyError(f"{name} not provided")


    return (func_args, var_pos_args, var_kw_args) 


