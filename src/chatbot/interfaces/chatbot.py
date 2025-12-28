#TODO: might need to recheck how functions are wrapped currently, mayheps should handle class/instancemethods 
#TODO: batchable


from abc import abstractmethod, ABC

from collections.abc import Iterable, Sized
from types import FunctionType, MethodType

from functools import wraps

from inspect import signature, ismethod






from .shared_decoration import SharedDecoratorInheritanceType
from .batch import batchify, batchable




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
    















# class SharedDecoratorInheritanceType(ABCMeta):
#     """
#         a type to share decorators to subclasses
#         # - decorators can only be applied once if they already exist
#         # - iterates over each function of its class_dict and tries to find and insert decorators from base class definitions
#     """

#     #hate module func instantiation, __wrapped__ isnt much better however imo, TODO: subsubclasses tests
#     def __new__(mcls, name, bases, class_dict):

#         for key, value in class_dict.items():
#             if isinstance(value, (FunctionType, MethodType)) and not getattr(value, "__isabstractmethod__", False):
#                 w = next(
#                     (base.__dict__.get(key) for base in bases if key in base.__dict__),
#                     None
#                 )
#                 print(w)
#                 base_descriptor = next(
#                     (mcls.get_function_descriptors_for(base.__dict__.get(key)) for base in bases if key in base.__dict__),
#                     None
#                 )
                
#                 print(name, key, value, f"\n{ast.unparse(base_descriptor)}")
#                 exit()
#                 if base_descriptor:
#                     impl_descriptor = mcls.get_function_descriptors_for(value)
#                     shared_decorators = []
#                     print(name, key, value, base_descriptor.decorator_list)
#                     #not so clean looking
#                     for decorator in base_descriptor.decorator_list:

#                         if isinstance(decorator, ast.Name): #singleton
#                             if decorator.id == "abstractmethod":
#                                 continue
#                             match = next(( x for x in impl_descriptor.decorator_list if ast.unparse(decorator) in ast.unparse(x) ), None) #nicht ganz korrekt
#                         else:
#                             match = next(( x for x in impl_descriptor.decorator_list if ast.unparse(decorator) == ast.unparse(x) ), None)
                           
#                         if match: 
#                             # if already applied
#                             if isinstance(match, ast.Name):
#                                 continue

#                             # inplace insert
#                             shared_decorator = impl_descriptor.decorator_list.pop(impl_descriptor.decorator_list.index(match))
                            
#                         shared_decorators.append(shared_decorator)
        

#                     if shared_decorators: #if it should add decorators
#                         # print(impl_descriptor.decorator_list, shared_decorators)
#                         pass


#                         # impl_descriptor.decorator_list = impl_descriptor.decorator_list + shared_decorators

#                         # # print(key, [ ast.unparse(x) for x in impl_descriptor.decorator_list ])
#                         # module = ast.Module(body=[impl_descriptor], type_ignores=[])
#                         # ast.fix_missing_locations(module)
#                         # code = compile(module, filename="<ast>", mode="exec")
#                         # merged_globals = modules[class_dict["__module__"]].__dict__.copy()
#                         # for base in bases:
#                         #     if hasattr(base, "__module__"):
#                         #         base_mod = modules.get(base.__module__)
#                         #         if base_mod:
#                         #             merged_globals.update(base_mod.__dict__)
#                         # exec(code, merged_globals | class_dict, temp_ns := {})
                        
#                         # new_func = temp_ns[key]
#                         # class_dict[key] = new_func

        
#         return super().__new__(mcls, name, bases, class_dict)
            

    
#     @classmethod
#     def resolve(mcls, namespace, expression):
#         if isinstance(expression, ast.Name):
#             if (resolution := mcls.get_from_class_module(namespace, expression.id)):
#                 return resolution
            
#             elif isclass(namespace):
#                 for x in namespace.__bases__:
#                     try:
#                         return mcls.get_from_class_module(x, expression.id)
#                     except:
#                         pass
            
#             raise Exception("<todo>")

#         if isinstance(expression, ast.Call):
#             func = mcls.resolve(namespace, expression.func)
#             args = [ mcls.resolve(namespace, x) for x in expression.args]
#             kwargs = { kw.arg: mcls.resolve(namespace, kw.value) for kw in expression.keywords}

#             return func(*args, **kwargs)

#         return ast.literal_eval(expression)


#     @classmethod
#     def get_abstractmethods(mcls, cls):
#         return [ (func_name, func_value) for func_name, func_value in getmembers(cls, predicate=isfunction) if getattr(func_value, "__isabstractmethod__", False)]
            


#     @classmethod
#     def get_from_class_module(mcls, cls, name):
#         if (obj := getattr(cls, name, None)) is not None:
#             return obj
        
#         return getattr(modules[cls.__module__], name, None)



#     #doesnt work for nested args yet
#     #TODO: better parsing procedure
#     @classmethod
#     def get_function_descriptors_for(mcls, obj):

#         if not hasattr(obj, "__module__"):
#             raise Exception("todo")
        
#         if not hasattr(obj, "__qualname__"):
#             raise Exception("todo")
        


#         file_tree = ast.parse(Path(modules[obj.__module__].__file__).read_text())
#         name_tree = obj.__qualname__.split('.')

#         class_node = None
#         function_node = None
#         i = 0

#         for node in ast.walk(file_tree):
#             if isinstance(node, ast.ClassDef):
#                 print("yes")
#             if isinstance(node, ast.ClassDef) and (node.name == name_tree[i] or (name_tree[i] == "<locals>" and name_tree[i+1] == node.name) ):
#                 class_node = node
#                 i += 1
#                 # break
#         print("node", ast.unparse(node))
#         for node in (class_node.body if class_node else None) or ast.walk(file_tree):
#             if isinstance(node, ast.FunctionDef) and node.name == name_tree[i]:
#                 function_node = node
#                 for decorator in function_node.decorator_list:
#                     if isinstance(decorator, ast.Call):
#                         decorator.keywords.sort(key= lambda x: x.arg or "")
                    
#                 # function_node.decorator_list = [ x if not isinstance(x, ast.Call) else sorted(x.keywords, key=lambda x: x.arg or "") for x in function_node.decorator_list ]
#                 break
            
#         if not function_node:
#             raise ValueError(f"couldn't find a value for {str(obj)}:{str(obj.__qualname__)}")
        


#         return function_node









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
        # print(f"Using: {context}")
        # print(f"Response: {response}")
        
        return response







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
        @batchify("vector", list[list[str]])
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
    