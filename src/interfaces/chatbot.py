from abc import abstractmethod, ABC, ABCMeta

from collections.abc import Iterable, Sized
from types import FunctionType, MethodType

from functools import wraps
from contextvars import ContextVar

from inspect import signature, getsource, getmembers, isclass, ismethod, isfunction, Parameter
from sys import modules
import ast
import textwrap


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



def is_batch(x):
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

def batchable(inherent=False):

    if callable(inherent):  
        return batchable()(inherent)


    def decorator(func):
        assert len(signature(func).parameters), f"{func} can't be made batchable"


        @wraps(func)
        def wrapper(*args, **kwargs):

            if inherent:
                return func(*args, **kwargs)


            arguments = signature(func).bind(*args, **kwargs)
            arguments.apply_defaults()
            
            scalar_arguments = {}
            batch_arguments = {}
            batch_len = None
            
            for i, (key, value) in enumerate(arguments.arguments.items()):

                if i == 0:
                    if isclass(value):
                        __class = value
                    elif isclass(type(value)):
                        __class = type(value)
                    else:
                        __class = None

                    if __class and func.__qualname__.startswith(__class.__qualname__ + "."):
                        scalar_arguments[key] = value
                        continue
                        
                if not (value is not None): #have to is not None due to pandas
                    scalar_arguments[key] = value #also: None
                    
                elif not (is_batch(value) and (not batch_len or len(value) == batch_len)):
                    if not batch_len:   #didnt pass batches, can stop
                        break

                    scalar_arguments[key] = value

                else:
                    if not batch_len:
                        batch_len = len(value)
                            
                    batch_arguments[key] = value


            if not batch_len:
                return func(*args, **kwargs)
            
            else:
                return list(func(**(scalar_arguments | dict(zip(batch_arguments.keys(), x)))) for x in zip(*batch_arguments.values()))
                

        return wrapper
    return decorator




def batchify(kwarg):
    def decorator(func):
        while hasattr(func, "__wrapped__"): func = func.__wrapped__
        assert kwarg in signature(func).parameters.keys(), f"{kwarg} isn't a valid arguments for {str(func)}"
        
        #batcher
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs)
            params.apply_defaults()

            if not (params.arguments[kwarg] is None) and not is_batch(params.arguments[kwarg]):
                print("called")
                params.arguments[kwarg] = [ params.arguments[kwarg] ]
            print(params)   
            return func(*params.args, **params.kwargs)
        

        return wrapper
    return decorator



def batchify(kwarg):
    def decorator(func):
        unwrapped = func
        while hasattr(unwrapped, "__wrapped__"): unwrapped = unwrapped.__wrapped__
        assert kwarg in signature(unwrapped).parameters.keys(), f"{kwarg} isn't a valid arguments for {str(unwrapped)}"
        

        #batcher
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs)
            params.apply_defaults()
            
            if not (params.arguments[kwarg] is None):
                if not is_batch(params.arguments[kwarg]):
                    params.arguments[kwarg] = [ params.arguments[kwarg] ]

                func_batch_size = getattr(unwrapped, "__batchsize__", None)
                arg_batch_size = len(params.arguments[kwarg])

                if func_batch_size == None:
                    print(f"set to {arg_batch_size}")
                    setattr(unwrapped, "__batchsize__", arg_batch_size)
                
                elif func_batch_size == 1 and arg_batch_size != 1:
                    params.arguments[kwarg] = [ params.arguments[kwarg] ]
                    
            try:
                output = func(*params.args, **params.kwargs)

            finally:
                if hasattr(unwrapped, "__batchsize__"):
                    delattr(unwrapped, "__batchsize__")
                
            return output
        
        return wrapper
    return decorator




def inject_arg(arg_key, fill_with, only_if_none=False):
    def decorator(func):
        sig = signature(func)
        fill_args = [] if not isinstance(fill_with, (FunctionType, MethodType)) else [ x for x in signature(fill_with).parameters if x in sig.parameters ]
        assert not isinstance(fill_with, (FunctionType, MethodType)) or len(fill_args) == len(signature(fill_with).parameters), f"can't use {fill_with} to fill {func}-function"

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if (not only_if_none) or (only_if_none and bound.arguments.get(arg_key) is None):
                if isinstance(fill_with, (FunctionType, MethodType)):
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
        print(args, kwargs)
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
    















class SharedDecoratorInheritanceType(ABCMeta):
    """
        a type to share decorators to subclasses
        - decorators can only be applied once if they already exist
    """

    #implementation is kinda alright, TODO: some cleanup however
    def __new__(mcls, name, bases, class_dict):
        cls = super().__new__(mcls, name, bases, class_dict)
        shared_function_descriptors = {}
        shared_function_calls = {}

        for x in bases:
            if issubclass(x, ABC):
                descriptors = { func_name: mcls.get_decorator_descriptors_for(x, func_name) for func_name, _ in mcls.get_abstractmethods(x) } 

                shared_function_descriptors |= descriptors
                shared_function_calls |= { k: [ mcls.resolve(cls, _x) for _x in v ]  for k, v in descriptors.items() }


        for function_name in shared_function_descriptors:
            if not getattr(cls.__dict__.get(function_name), "__isabstractmethod__", False):
                applied_decorator_descriptors = mcls.get_decorator_descriptors_for(cls, function_name)
                applied_decorator_calls = [ mcls.resolve(cls, x) for x in applied_decorator_descriptors ]

                for shared_decorator in zip(shared_function_descriptors[function_name], shared_function_calls[function_name]):

                    if isinstance(shared_decorator[0], ast.Name):
                        if shared_decorator[0].id == "abstractmethod":
                            continue
                        if shared_decorator[1] and any(( str.startswith(x.__qualname__, shared_decorator[1].__qualname__) for x in applied_decorator_calls if x)):
                            continue
                    
                    elif shared_decorator[0] in applied_decorator_descriptors:
                        continue

                    decorator = shared_decorator[1]
                    func = mcls.get_from_class_module(cls, function_name) #not sure yet

                    setattr(cls, function_name, decorator(func))
            
        return cls


    
    @classmethod
    def resolve(mcls, namespace, expression):
        if isinstance(expression, ast.Name):
            return mcls.get_from_class_module(namespace, expression.id)
        
        if isinstance(expression, ast.Call):
            func = mcls.resolve(namespace, expression.func)
            args = [ mcls.resolve(namespace, x) for x in expression.args]
            kwargs = { kw.arg: mcls.resolve(namespace, kw.value) for kw in expression.keywords}
            
            return func(*args, **kwargs)

        return ast.literal_eval(expression)


    @classmethod
    def get_abstractmethods(mcls, cls):
        return [ (func_name, func_value) for func_name, func_value in getmembers(cls, predicate=isfunction) if getattr(func_value, "__isabstractmethod__", False)]
            


    @classmethod
    def get_from_class_module(mcls, cls, name):
        if (obj := getattr(cls, name, None)) is not None:
            return obj
        
        return getattr(modules[cls.__module__], name, None)



    #doesnt work for nested args yet
    #TODO: dont know yet if I like additional namespace argument
    @classmethod
    def get_decorator_descriptors_for(mcls, cls, method_name: str):
        """Extract decorator name and function via AST."""
        decorators = []
        

        # Find class node
        class_node = next(
            n for n in ast.walk(ast.parse(textwrap.dedent(getsource(cls))))
            if isinstance(n, ast.ClassDef) and n.name == cls.__name__
        )

        # Find method node
        func_node = next(
            (n for n in class_node.body
            if isinstance(n, ast.FunctionDef) and n.name == method_name),
            None
        )
        if not func_node:
            raise Exception("todo")


        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                decorator.keywords.sort(key=lambda x: x.arg or "")

            decorators.append(decorator)
            continue


        return list(reversed(decorators))









class Chatbot():
    """
       chatbot interface - intended for RAG usage, might be fine for other as well
    """
    
    def __init__(self, knowledgebase, vectorizer, matcher, instructor, generator):
        assert isinstance(knowledgebase, self.KnowledgeBase)
        assert isinstance(vectorizer, self.Vectorizer)
        assert isinstance(matcher, self.Matcher)
        assert isinstance(instructor, self.Instructor)
        assert isinstance(generator, self.Generator)
        
        self.knowledgebase = knowledgebase
        self.vectorizer = vectorizer
        self.matcher = matcher
        self.instructor = instructor
        self.generator = generator



    def load_context(self, data, keys, ids=None):
        self.knowledgebase.create(keys, data, ids)



    def respond(self, text, context=None, instructions=None):
        
        if instructions:
            pass

        else:
            if context is None and self.knowledgebase and self.vectorizer and self.matcher:
                context = self.matcher.match(self.vectorizer.vectorize(text), self.knowledgebase)

            if self.instructor:
                instructions = self.instructor.create_instructions(text, context)

        response = self.generator.generate(**instructions)

        # print(f"Responding to: {text}")    
        print(f"Using: {context}")
        # print(f"Response: {response}")
        
        return response







    class KnowledgeBase(ABC, metaclass=SharedDecoratorInheritanceType):
        """
            general object to offer crud interface (underlying object doesn't matter - in principal atleast)
        """

        @abstractmethod
        @batchable
        def create_id(self, data):
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
        @batchify("text")
        @batchable
        def vectorize(self, text):
            raise NotImplementedError


    class Matcher(ABC, metaclass=SharedDecoratorInheritanceType):
        
        @abstractmethod
        @batchify("vector")
        @batchable
        def match(self, vector, knowledgebase, **args):
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
    