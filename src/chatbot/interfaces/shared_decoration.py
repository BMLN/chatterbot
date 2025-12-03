from abc import ABCMeta
from typing import Any, Callable, List, Dict, Optional
from types import FunctionType, MethodType


from sys import modules
import builtins
from pathlib import Path

from inspect import signature, getsource, getmembers, isclass, ismethod, isfunction, Parameter

from textwrap import dedent
from ast import parse, unparse, literal_eval, FunctionDef, Name, Call, Subscript



from functools import wraps
from inspect import unwrap
from abc import abstractmethod






def singleton(dec):
    """
    wraps a decorator to be only applicable once per function
    """
    
    def outer(func):
        if not dec in getattr(func, "__singletons__", []):
            if not hasattr(func, "__singletons__"):
                func.__singletons__ = []
        
            func.__singletons__.append(dec)
            return dec(func)
        
        else:
            @wraps(func) #noop
            def wrapper(*args, **kwargs): 
                return func(*args, **kwargs)
            return wrapper
        
    return outer




#auf wrapper ebene
#TODO: could add non singleton singleton version to make it rely on singleton on functiontype basis 
#DEPR version
def inplace(dec):
    """
    wraps a decorator to be replacable inplace by other decorators with an inplace decoration
    """
    def outer(func):
        print("wrapping", func)

        unwrapped = unwrap(func)
        # inplacer = getattr(unwrapped, "__inplace_dec__", None)
        inplacer = getattr(unwrapped, "__inplace_caller_", None)

        if not inplacer:
            pass

        elif inplacer != dec:
            pass

        if inplacer:
            unwrapped.__inplace__ = dec
            return func
        
        # elif next():
            
        
        else:
            unwrapped.__inplace__ = dec

            @wraps(func)
            def wrapper(*args, **kwargs):
                # print("wrapp")
                return unwrapped.__inplace__(func)(*args, **kwargs)
            return wrapper
        
    return outer


#TODO: could add non singleton singleton version to make it rely on singleton on functiontype basis 
def inplace(dec):
    """
    wraps a decorator to be replacable inplace by other decorators with an inplace decoration
    """
    def outer(func):
        unwrapped = unwrap(func)
        inplacer = getattr(unwrapped, "__inplace_by__", None)
        wrapper = func
        
        if inplacer:
            while wrapper != inplacer:
                if not hasattr(wrapper, "__wrapped__"):
                    break
                
                wrapper = wrapper.__wrapped__


        if not inplacer or not wrapper == inplacer:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return unwrapped.__inplace_wrapper__(func)(*args, **kwargs)
            
            unwrapped.__inplace_by__ = wrapper
            unwrapped.__inplace_wrapper__ = dec
            
            return wrapper

        else:
            unwrapped.__inplace_wrapper__ = dec

            return func
        
    return outer



class SharedDecoratorInheritanceType(ABCMeta):
    """
    a type to share decorators to subclasses
    
    goes through all inheritances and fetches the decorators applied on each inherited function
    """

    #TODO: subsubclasses tests
    def __new__(mcls, name, bases, class_dict):
        for key, value in class_dict.items():

            #check for inherited function decorators            
            if not (isinstance(value, (FunctionType, MethodType)) and not getattr(value, "__isabstractmethod__", False)):
                continue

            if not (decorators:= [
                mcls.resolve(decorator, base)
                for base in [ x for base in bases for x in base.__mro__[:-1] ]#bases
                for decorator in (
                    reversed(mcls.parse_decorators(base.__dict__.get(key))) if key in base.__dict__ 
                    else []
                )
                if unparse(decorator) != "abstractmethod"
            ]):
                continue

            #rewrap
            rewrapped = unwrap(value)
            decorators += [ 
                mcls.resolve(x, modules[class_dict["__module__"]]) 
                for x in list(reversed(mcls.parse_decorators(value)))
            ]

            for x in decorators:
                rewrapped = x(rewrapped)

            class_dict[key] = rewrapped

        
        return super().__new__(mcls, name, bases, class_dict)


# class SharedDecoratorInheritanceType(ABCMeta):
#     """
#         a type to share decorators to subclasses
#         # - decorators can only be applied once if they already exist
#         # - iterates over each function of its class_dict and tries to find and insert decorators from base class definitions
#     """

#     #TODO: subsubclasses tests
#     def __new__(mcls, name, bases, class_dict):
#         for key, value in class_dict.items():

#             #check for inherited function decorators            
#             if not (isinstance(value, (FunctionType, MethodType)) and not getattr(value, "__isabstractmethod__", False)):
#                 continue

#             if not (shared_decorators:= [
#                 (decorator, mcls.resolve(decorator, base))
#                 for base in reversed(bases)
#                 for decorator in (
#                     mcls.parse_decorators(base.__dict__.get(key)) if key in base.__dict__ 
#                     else []
#                 )
#             ]):
#                 continue

#             #rewrap
#             raw_func = None
#             descriptors = list(reversed(mcls.parse_decorators(value)))
#             decorators = [ mcls.resolve(x, modules[class_dict["__module__"]]) for x in descriptors ]
#             print("b4", [ unparse(x) for x in descriptors])

#             for descriptor, decorator in shared_decorators:
                
#                 if decorator == abstractmethod:
#                     continue

#                 if getattr(decorator, "__singleton__", False):
#                     if decorator in decorators:
#                         continue

#                 descriptors.append(descriptor)
#                 decorators.append(decorator)
#                 continue
#                 if unparse(x) in [ unparse(item) for item in decorators ]:
#                     #check equals 
#                     # if : continue
#                     # 
#                     continue
                
#                 # print(modules[class_dict["__module__"]])
#                 # print(getattr(modules[class_dict["__module__"]], unparse(x)))
#                 #decorators.insert(0, x)

#             print("af", [ unparse(x) for x in descriptors])
#             # print([ unparse(x) for x in decorators] )


#             # shared_decorators = [ x for x in applied_decorators ]

#             # for i, x in enumerate(shared_decorator):
#             #     __decorator = mcls.resolve(class_dict)

#             #     if __decorator in applied_decorators:

#             # for x in base_decorators:

            
#             #         print(name, key, value, base_descriptor.decorator_list)
#             #         #not so clean looking
#             #         for decorator in base_descriptor.decorator_list:

#             #             if isinstance(decorator, ast.Name): #singleton
#             #                 if decorator.id == "abstractmethod":
#             #                     continue
#             #                 match = next(( x for x in impl_descriptor.decorator_list if ast.unparse(decorator) in ast.unparse(x) ), None) #nicht ganz korrekt
#             #             else:
#             #                 match = next(( x for x in impl_descriptor.decorator_list if ast.unparse(decorator) == ast.unparse(x) ), None)
                           
#             #             if match: 
#             #                 # if already applied
#             #                 if isinstance(match, ast.Name):
#             #                     continue

#             #                 # inplace insert
#             #                 shared_decorator = impl_descriptor.decorator_list.pop(impl_descriptor.decorator_list.index(match))
                            
#             #             shared_decorators.append(shared_decorator)
        

#             #         if shared_decorators: #if it should add decorators
#             #             # print(impl_descriptor.decorator_list, shared_decorators)
#             #             pass


#             #             # impl_descriptor.decorator_list = impl_descriptor.decorator_list + shared_decorators

#             #             # # print(key, [ ast.unparse(x) for x in impl_descriptor.decorator_list ])
#             #             # module = ast.Module(body=[impl_descriptor], type_ignores=[])
#             #             # ast.fix_missing_locations(module)
#             #             # code = compile(module, filename="<ast>", mode="exec")
#             #             # merged_globals = modules[class_dict["__module__"]].__dict__.copy()
#             #             # for base in bases:
#             #             #     if hasattr(base, "__module__"):
#             #             #         base_mod = modules.get(base.__module__)
#             #             #         if base_mod:
#             #             #             merged_globals.update(base_mod.__dict__)
#             #             # exec(code, merged_globals | class_dict, temp_ns := {})
                        
#             #             # new_func = temp_ns[key]
#             #             # class_dict[key] = new_func

        
#         return super().__new__(mcls, name, bases, class_dict)
            




    #TODO: better exceptions
    @classmethod
    def parse_decorators(mcls, obj):
        parsed = parse(dedent(getsource(obj)))

        if not parsed.body:
            raise Exception("no function source")
        
        if not isinstance(parsed.body[0], FunctionDef):
            raise Exception("parsed object isnt a function")
        
        return parsed.body[0].decorator_list
  


    #TODO: beautify
    #TODO: subscript only quickfix, not working for actual slices or similar
    @classmethod
    def resolve(mcls, expression, namespace):
        resolution = None

        #resolving:
        if isinstance(expression, Name):
            resolution = getattr(namespace, expression.id, None)

            if not resolution and namespace != builtins:
                try:
                    resolution = mcls.resolve(expression, builtins) 
                except:
                    pass

        elif isinstance(expression, Call):
            func = mcls.resolve(expression.func, namespace)
            args = [ mcls.resolve(x, namespace) for x in expression.args ]
            kwargs = { kw.arg: mcls.resolve(kw.value, namespace) for kw in expression.keywords}

            resolution = func(*args, **kwargs)
        
        elif isinstance(expression, Subscript):
            outer = mcls.resolve(expression.value, namespace)
            inner = mcls.resolve(expression.slice, namespace)
            
            resolution = outer[inner]
            

        #options:
        if not resolution and getattr(namespace, "__module__", None):
            resolution = mcls.resolve(expression, modules[getattr(namespace, "__module__")]) 

        if resolution:
            return resolution

        if isinstance(expression, (Name, Call)):
            raise Exception(f"Couldn't resolve {unparse(expression)} from {namespace}")
        
        return literal_eval(expression)




    @classmethod
    def get_abstractmethods(mcls, cls):
        return [ (func_name, func_value) for func_name, func_value in getmembers(cls, predicate=isfunction) if getattr(func_value, "__isabstractmethod__", False)]
            


    @classmethod
    def get_from_class_module(mcls, cls, name):
        if (obj := getattr(cls, name, None)) is not None:
            return obj
        
        return getattr(modules[cls.__module__], name, None)



    #doesnt work for nested args yet
    #TODO: better parsing procedure
    @classmethod
    def get_function_descriptors_for(mcls, obj):

        if not hasattr(obj, "__module__"):
            raise Exception("todo")
        
        if not hasattr(obj, "__qualname__"):
            raise Exception("todo")
        


        file_tree = parse(Path(modules[obj.__module__].__file__).read_text())
        name_tree = obj.__qualname__.split('.')

        class_node = None
        function_node = None
        i = 0

        for node in ast.walk(file_tree):
            if isinstance(node, ast.ClassDef):
                print("yes")
            if isinstance(node, ast.ClassDef) and (node.name == name_tree[i] or (name_tree[i] == "<locals>" and name_tree[i+1] == node.name) ):
                class_node = node
                i += 1
                # break
        print("node", ast.unparse(node))
        for node in (class_node.body if class_node else None) or ast.walk(file_tree):
            if isinstance(node, ast.FunctionDef) and node.name == name_tree[i]:
                function_node = node
                for decorator in function_node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        decorator.keywords.sort(key= lambda x: x.arg or "")
                    
                # function_node.decorator_list = [ x if not isinstance(x, ast.Call) else sorted(x.keywords, key=lambda x: x.arg or "") for x in function_node.decorator_list ]
                break
            
        if not function_node:
            raise ValueError(f"couldn't find a value for {str(obj)}:{str(obj.__qualname__)}")
        


        return function_node
