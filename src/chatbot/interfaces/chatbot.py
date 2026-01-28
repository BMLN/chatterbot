#TODO: might need to recheck how functions are wrapped currently, mayheps should handle class/instancemethods 
#TODO: batchable


from abc import abstractmethod, ABC
from typing import override

from collections.abc import Iterable, Sized
from types import FunctionType, MethodType

from functools import wraps

from inspect import signature, ismethod






from .shared_decoration import SharedDecoratorInheritanceType
from .batch import batchify, batchable
from .arghandler import bind_args



# helper
def combine_args_kwargs(func, *args, **kwargs):
    sig = signature(func)
    params = list(sig.parameters.keys())

    combined = {}

    for name, value in zip(params, args):
        combined[name] = value

    combined.update(kwargs)


    return combined



#TODO ?
def is_class_function(obj, func):
    if not isinstance(obj, object):
        return False
    
    if not getattr(func, "__class__", function):
        return False
    
    if (func_class := getattr(func, "__self__", None)) == None:
        return False
    
    if not (func_class is obj.__class__ or isinstance(func_class, obj.__class__)):
        return False
    
    return True


#deprecated - defined batch differently
def _is_batch(x):
    singles = (str, int, float, bool, dict)


    if not isinstance(x, Sized) or isinstance(x, singles):
        return False

    dim = None
    for _x in x:
        if _x is None or isinstance(_x, singles):
            _dim = 1
        elif isinstance(_x, Iterable):
            _dim = len(_x)
        else:
            return False
        
        if _dim != dim:
            if dim == None:
                dim = _dim
                continue
            
            return False

    return True

#DEPR
def _is_batch(x):
    singles = (str, int, float, bool, dict)

    if not isinstance(x, Sized) or isinstance(x, singles):
        return False
    
    # if isinstance(x, Iterable) and not (len(x) > 0 and isinstance(x[0], Iterable) and not isinstance(x[0], str)):
    #     print((len(x) > 0 and isinstance(x[0], Iterable) and not isinstance(x[0], str))
    #     return False
     
    dim = None
    for _x in x:
        if isinstance(_x, type):
            _dim = 1
        
        elif isinstance(_x , Iterable) and isinstance(_x, (str, dict, list)):
            _dim = len(_x)
        
        else:
            return False
        
        
        if _dim != dim:
            if dim == None:
                dim = _dim
                continue
            
            return False

    return True




# decorators

# def batchable(inherent=False):
    
#     if callable(inherent):
#         return batchable()(inherent)
    
#     def decorator(func):
#         def wrapper(*args, **kwargs):
            
#             if inherent: #for single unit TODO
#                 return func(*args, **kwargs)
            
#             else:
#                 args = combine_args_kwargs(func, *args, **kwargs)

#                 item_keys = [ name for name, param in signature(func).parameters.items() if param.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD) ]
#                 items = { key: args[key] for key in item_keys[1:] if key in args } #temp_fix

#                 return list(func(**(args | dict(zip(items.keys(), x)))) for x in zip(*items.values()))
        
#         return wrapper
#     return decorator




# def batchable(inherent=False):

#     if callable(inherent):  
#         return batchable()(inherent)


#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if inherent:
#                 return func(*args, **kwargs)

            
#             arguments = signature(func).bind(*args, **kwargs)
#             arguments.apply_defaults()
#             arguments = arguments.arguments
#             cls = None
#             batch_keys = []
#             w = arguments[batch_keys[0]]
#             print(w, isinstance(func, (classmethod, staticmethod)), isinstance(type(func), (classmethod, staticmethod)))
#             exit()
            
#             if (isclass(arguments[batch_keys[0]]) or isclass(type(arguments[batch_keys[0]]))) and True:    
#                 batch_keys = batch_keys[1:]

#             first_arg = next((x for x in arguments.values() if x is not None), None)

#             if not (first_arg is not None and is_batch(first_arg)):
#                 return func(*args, **kwargs)
            
#             else:
#                 batch_size = len(first_arg)
#                 arguments = { key: value for key, value in arguments.items() if value is not None and is_batch(value) and len(value) == batch_size }

#                 batch_keys, batch_items = zip(*{ key: value for key, value in arguments.items() if (value is not None and is_batch(value) and len(value) == batch_size) }.items())

#                 return list(func(**(arguments | dict(zip(batch_keys, x)))) for x in zip(*batch_items))
                

#         return wrapper
#     return decorator



#deprecated
# def batchify(kwarg):
#     def decorator(func):
#         while hasattr(func, "__wrapped__"): func = func.__wrapped__
#         assert kwarg in signature(func).parameters.keys(), f"{kwarg} isn't a valid arguments for {str(func)}"
        
#         #batcher
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             params = signature(func).bind(*args, **kwargs)
#             params.apply_defaults()

#             if not (params.arguments[kwarg] is None) and not is_batch(params.arguments[kwarg]):
#                 print("called")
#                 params.arguments[kwarg] = [ params.arguments[kwarg] ]
#             print(params)   
#             return func(*params.args, **params.kwargs)
        

#         return wrapper
#     return decorator






def inject_arg(arg_key, fill_with, only_if_none=False):
    def decorator(func):
        sig = signature(func)
        if isinstance(fill_with, classmethod):
            fill_args = [ x for x in signature(fill_with.__func__).parameters if x in sig.parameters ]
        elif isinstance(fill_with, (FunctionType, MethodType)):
            fill_args = [ x for x in signature(fill_with).parameters if x in sig.parameters ]
        else:
            fill_args = [] 
        #TODO:no classmethod assertion
        assert not isinstance(fill_with, (FunctionType, MethodType)) or len(fill_args) == len(signature(fill_with).parameters), f"can't use {fill_with} to fill {func}-function"

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if (not only_if_none) or (only_if_none and bound.arguments.get(arg_key) is None):
                if isinstance(fill_with, classmethod):
                    bound.arguments[arg_key] = fill_with.__func__(next(iter(bound.arguments.values())), **{k: v for k, v in bound.arguments.items() if k in fill_args})
                elif isinstance(fill_with, (FunctionType, MethodType)):
                    bound.arguments[arg_key] = fill_with(**{k: v for k, v in bound.arguments.items() if k in fill_args})
                else:
                    bound.arguments[arg_key] = fill_with

            return func(*bound.args, **bound.kwargs)

        return wrapper
    return decorator




#gened #TODO: recheck
def check_func_args(func, *args, **kwargs):
    # print(args, kwargs)
# Bound method: signature already excludes 'self'
    if isinstance(func, MethodType) and func.__self__ is not None:
        sig = signature(func)
        try:
            sig.bind(*args, **kwargs)
            return True
        except TypeError:
            return False

    # Unwrap classmethod / staticmethod
    if isinstance(func, (classmethod, staticmethod)):
        func = func.__func__
    elif isinstance(func, MethodType):
        func = func.__func__

    sig = signature(func)
    try:
        # print(args, kwargs)
        sig.bind(*args, **kwargs)
        return True
    except TypeError:
        return False

# def check_func_args(func, *args, **kwargs):
#     sig = signature(func)
#     try:
#         # if the function requires at least one parameter but we pass none,
#         # don't fail — it's probably a decorator check.
#         if len(sig.parameters) > 0 and len(args) == 0 and len(kwargs) == 0:
#             return True
#         sig.bind(*args, **kwargs)
#         return True
#     except TypeError:
#         return False






# #TODO: assertions for config items
# #TODO: could add *arg passing as well
# def dec_injection(config={}):
#     config = { key.__name__: value for key, value in config.items() }


#     def class_decorator(cls):
#         for key, value in list(filter(lambda x: x[0] in config.keys(), cls.__dict__.items())):
#             if isinstance((__decorated := value), (classmethod, staticmethod)):
#                 __decorated = __decorated.__func__
                    
#             #adding decorators#
#             for decorator, args in config[key]:
#             #for decorator, args in config[key]:
#                 __decorated = decorator(**(args or {}))(__decorated)

#             if isinstance(value, staticmethod):
#                 __decorated = staticmethod(__decorated)
#             elif isinstance(value, classmethod):
#                 __decorated = classmethod(__decorated)

#             setattr(cls, value.__name__, __decorated)


#         return cls
#     return class_decorator


def dec_injection(config={}):
    config = { key.__name__: value for key, value in config.items() }
    
    def class_decorator(cls):
        funcs = list(filter(lambda x: x[0] in config.keys(), cls.__dict__.items()))
        
        for key, value in funcs:
            is_classmethod = isinstance(value, classmethod)
            is_staticmethod = isinstance(value, staticmethod)

            # Extract the actual function from descriptors
            if is_classmethod or is_staticmethod:
                func = value.__func__
            else:
                func = value

            # Apply decorators in correct order
            for decorator, kwargs in reversed(config[key]):
                kwargs = kwargs or {}
                func = decorator(**kwargs)(func)

            # Re-wrap in static/classmethod if needed
            if is_classmethod:
                func = classmethod(func)
            elif is_staticmethod:
                func = staticmethod(func)

            setattr(cls, key, func)
    return class_decorator


def dec_injection(config={}):
    config = { key.__name__: value for key, value in config.items() }
    
    def class_decorator(cls):
        funcs = list(filter(lambda x: x[0] in config.keys(), cls.__dict__.items()))
        
        for key, value in funcs:
            is_classmethod = isinstance(value, classmethod)
            is_staticmethod = isinstance(value, staticmethod)

            # Extract the actual function from descriptors
            if is_classmethod or is_staticmethod:
                func = value.__func__
            else:
                func = value

            # Apply decorators in correct order
            for decorator, kwargs in reversed(config[key]):
                kwargs = kwargs or {}
                func = decorator(**kwargs)(func)

            # Re-wrap in static/classmethod if needed
            if is_classmethod:
                func = classmethod(func)
            elif is_staticmethod:
                func = staticmethod(func)

            setattr(cls, key, func)
    return class_decorator




def apply_decorator(func, decorator, *args, **kwargs):
    
    if not callable(func):
        raise ValueError("todo")
    
    if not callable(decorator):
        raise ValueError("todo")

    if not check_func_args(decorator, args, kwargs):
        raise ValueError(f"wrong args")
    
    
    is_classmethod = isinstance(func, classmethod)
    is_staticmethod = isinstance(func, staticmethod)

        # Extract the actual function from descriptors
    if is_classmethod or is_staticmethod:
        func = func.__func__
    else:
        func = func    

    func = decorator(args, kwargs)(func)



def wrap_function(func, decorator, *args, **kwargs):

    #checks
    if not callable(func):
        raise ValueError("todo")
    
    if not callable(decorator):
        raise ValueError("todo")

    if not check_func_args(decorator, *args, **kwargs ):
        raise ValueError(f"{decorator} got wrong args: {(args, kwargs)}")
    


    # Check if it's a bound method
    if ismethod(func):
        # Get the instance and the unbound function
        instance = func.__self__
        unbound_func = func.__func__
        
        # Apply decorator to the unbound function
        decorated = decorator(*args, **kwargs)(unbound_func)
        
        # Return a new bound method
        return decorated.__get__(instance, type(instance))
    else:
        # For regular functions, just apply the decorator
        return decorator(*args, **kwargs)(func)
    




















class Chatbot():
    """
       chatbot interface - intended for RAG usage, might be fine for other as well
    """
    
    def __init__(self, knowledgebase=None, vectorizer=None, matcher=None, instructor=None, generator=None):
        assert not knowledgebase or isinstance(knowledgebase, self.KnowledgeBase)
        assert not vectorizer or isinstance(vectorizer, self.Vectorizer)
        assert not matcher or isinstance(matcher, self.Matcher)
        assert not instructor or isinstance(instructor, self.Instructor)
        assert not generator or isinstance(generator, self.Generator)
        
        self.knowledgebase = knowledgebase
        self.vectorizer = vectorizer
        self.matcher = matcher
        self.instructor = instructor
        self.generator = generator


    def _bound_args(self, *args, **kwargs):
        output = []

        for x in [ self.vectorizer, self.matcher, self.instructor, self.generator ]:
            if not x:
                output.append({})
        
            if isinstance(x, Chatbot.Vectorizer):
                output.append({ item[0]: item[1] for i, item in enumerate(bind_args(x.vectorize, list((None,) + args), kwargs).items()) if i > 0 })

            elif isinstance(x, Chatbot.Matcher):
                output.append( { item[0]: item[1] for i, item in enumerate(bind_args(x.match, list((None, None) + args), kwargs).items()) if i > 1 })

            elif isinstance(x, Chatbot.Instructor):
                    output.append({ item[0]: item[1] for i, item in enumerate(bind_args(x.create_instructions, list((None, None) + args), kwargs).items()) if i > 1 })

            elif isinstance(x, Chatbot.Generator):
                output.append({})

        return output


    def respond(self, text, context=None, instructions=None, *args, **kwargs):
        vec_args, match_args, instr_args, gen_args = self._bound_args(*args, **kwargs)
        print("mmmms", vec_args, match_args, instr_args, gen_args)

        if instructions:
            pass

        else:
            if context is None and self.matcher and self.knowledgebase:
                context = self.matcher.match(text if not self.vectorizer else self.vectorizer.vectorize(text, **vec_args), self.knowledgebase, **match_args)

            instructions = self.instructor.create_instructions(text, context, **instr_args)


        return self.generator.generate(**({k: v for d in instructions for k, v in d.items()} | gen_args))







    class KnowledgeBase(ABC, metaclass=SharedDecoratorInheritanceType):
        """
            general object to offer crud interface (underlying object doesn't matter - in principal atleast)
        """

        @abstractmethod
        @batchable
        def create_id(self, data):
            #bandaid fix #TODO
            if hasattr(self, "create_id") and getattr(self, "create_id") != Chatbot.KnowledgeBase.create_id:
                return self.create_id(data)
            
            raise NotImplementedError


        @abstractmethod
        @inject_arg("id", create_id, True)
        @batchify("id")
        @batchify("data")
        @batchable
        def create(self, id, data, **args):
            raise NotImplementedError
        
        @abstractmethod
        @batchify("id")
        @batchable
        def retrieve(self, id, **args):
            raise NotImplementedError

        @abstractmethod
        @batchify("id")
        @batchable
        def update(self, id, **args):
            raise NotImplementedError
        
        @abstractmethod
        @batchify("id")
        @batchable
        def delete(self, id, **args):
            raise NotImplementedError
        
        @abstractmethod
        @batchable
        def search(self, **args):
            raise NotImplementedError



    class Vectorizer(ABC, metaclass=SharedDecoratorInheritanceType):
        """
            defines the desired interaction to the data/knowledgebase
        """

        @abstractmethod
        @batchify("text", list[str])
        @batchable
        def vectorize(self, text):
            raise NotImplementedError


    class Matcher(ABC, metaclass=SharedDecoratorInheritanceType):
        
        @abstractmethod
        @batchify("data")
        @batchable
        def match(self, data, knowledgebase, **args):
           raise NotImplementedError
           
            

    class Instructor(ABC, metaclass=SharedDecoratorInheritanceType):
        """
            module to formulate the input for the generation module in a form it can consume
        """

        @abstractmethod
        @batchify("context")
        @batchify("text")
        @batchable
        def create_instructions(self, text, context, **args):
            raise NotImplementedError



    class Generator(ABC, metaclass=SharedDecoratorInheritanceType):

        @abstractmethod
        @batchable
        def generate(self, **args):
            raise NotImplementedError
    