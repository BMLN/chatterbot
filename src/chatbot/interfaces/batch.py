from collections.abc import Iterable, Sized
from typing import get_args, get_origin
from inspect import signature, getsource, getmembers, isclass, ismethod, isfunction, Parameter


from .shared_decoration import inplace
from functools import wraps






def is_batch(x, singles=(int, float, complex, bool, dict)):
    """
    checks if an object is a batch, defined as: 
        - object of type batch
        - an iterable with elements of the same length (str, int, float, bool, dict == length => 1)
    """

    if isinstance(x, Batch):
        return True

    if not isinstance(x, Sized) or isinstance(x, singles + (str,)):
        return False
    

    dim = None
    for _x in x:
        if isinstance(_x, type) or isinstance(_x, singles):
            _dim = 1
            
        elif isinstance(_x , Iterable) and isinstance(_x, Sized):
            _dim = len(_x)
        
        else:
            return False
        

        if _dim != dim:
            if dim == None:
                dim = _dim
                continue
            
            return False

    return True



#gened
def is_iterable_of(obj, typing):
    origin = get_origin(typing)
    args = get_args(typing)

    # Non-parametric types → simple isinstance
    if origin is None:
        return isinstance(obj, typing)

    # Ignore tuples completely
    if origin is tuple:
        raise TypeError("Tuples are not supported in this checker.")

    # Must be an iterable type (list, set, etc.)
    if not (origin and issubclass(origin, Iterable)):
        raise TypeError(f"Unsupported annotation: {typing}")

    # Outer container type must match
    if not isinstance(obj, origin):
        return False

    # Expect exactly one type parameter (list[T], set[T], etc.)
    (inner_type,) = args

    # Recursively check each element
    return all(is_iterable_of(x, inner_type) for x in obj)








def batchify(kwarg, batch_type=None):
    """
    Forces an argument of a function to always be a batch and wraps it as a Batch-Type.

    Having batch_type or a type annotation set will try to wrap into that given type if possible.
    """
    def decorator(func):
        unwrapped = func
        while hasattr(unwrapped, "__wrapped__"): unwrapped = unwrapped.__wrapped__
        assert kwarg in signature(unwrapped).parameters.keys(), f"{kwarg} isn't a valid arguments for {str(unwrapped)}"

        __batch_type = batch_type if batch_type else signature(unwrapped).parameters[kwarg].annotation
        __batch_type = __batch_type if __batch_type != Parameter.empty else None


        #batcher
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind_partial(*args, **kwargs)
            params.apply_defaults()
            # print("b4", params)

            #not clean yet
            checked = False
            if __batch_type:
                if is_iterable_of(params.arguments[kwarg], __batch_type):#params.signature.parameters[kwarg].annotation):
                    if not getattr(unwrapped, "__batchsize__", None):
                        setattr(unwrapped, "__batchsize__", len(params.arguments[kwarg]))
                    checked = True

                elif is_iterable_of([params.arguments[kwarg]], __batch_type):
                    params.arguments[kwarg] = [ params.arguments[kwarg] ]
                    if not getattr(unwrapped, "__batchsize__", None):
                        setattr(unwrapped, "__batchsize__", len(params.arguments[kwarg]))
                    checked = True
                # print("didnt", checked)

            if not checked:
                if not (params.arguments[kwarg] is None):
                    if not is_batch(params.arguments[kwarg]):
                        # print("b", kwarg)
                        params.arguments[kwarg] = [ params.arguments[kwarg] ]

                    func_batch_size = getattr(unwrapped, "__batchsize__", None)
                    arg_batch_size = len(params.arguments[kwarg])

                    if func_batch_size == None:
                        setattr(unwrapped, "__batchsize__", arg_batch_size)
                    
                    elif func_batch_size == 1 and arg_batch_size != 1:
                        # print("b", kwarg)
                        params.arguments[kwarg] = [ params.arguments[kwarg] ]
            
            #TODO: Batch here good code?
            try:
                params.arguments[kwarg] = Batch(params.arguments[kwarg])
            
            except TypeError:
                raise TypeError(f"can't batchify {kwarg} with {params.arguments[kwarg]} for {func}")    


            try:
                # print("aft", params.arguments)
                output = func(*params.args, **params.kwargs)

            finally:
                if hasattr(unwrapped, "__batchsize__"):
                    delattr(unwrapped, "__batchsize__")
           
            return output
        
        return wrapper
    return decorator




#TODO: add to make it single
#TODO: some issues w/ inherent=False? check again
def batchable(inherent=False):
    """
    ### should wrap the function with a wrapper to make it batchable.

    A function that is batchable behaves in a way that the function will work with arguments either be passed as values or also through multiples of values with an Iterable instead.
    Applying it non-inherently means arguments are parsed and split into arguments that are batches and scalars and the function will be called for each element of a batch. 
    Checking for batch-arguments works by:
    - them being the first argument passing the is_batch()
    - them being the same length as previous batch-arguments and passing is_batch()
    """

    if callable(inherent):  
        return batchable()(inherent)

    @inplace
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

                #check if classfunc
                if i == 0:
                    if isclass(value):
                        __class = value
                    elif isclass(type(value)):
                        __class = type(value)
                    else:
                        __class = None

                    if __class and hasattr(__class, func.__name__): #func.__qualname__.startswith(__class.__qualname__ + "."):  # Fix: Methoden werden am Klassennamen erkannt; __qualname__ ist zu lang und existiert als Attribut nicht
                        scalar_arguments[key] = value
                        continue

                #set scalars/batches
                if not (value is not None): #have to "is not None" due to pandas
                    scalar_arguments[key] = value #also: None
                    
                elif is_batch(value) and (batch_len is None or len(value) == batch_len):
                    if not batch_len:
                        batch_len = len(value)

                    batch_arguments[key] = value
                
                else:
                    scalar_arguments[key] = value


            if batch_len is None: # Fix: 0 (leerer Batch) darf nicht wie "kein Batch" behandelt werden
                return func(*args, **kwargs)
            
            else:
                return list(func(**(scalar_arguments | dict(zip(batch_arguments.keys(), x)))) for x in zip(*batch_arguments.values()))
                

        return wrapper
    return decorator










class Batch(list):
    """
    list wrapper to mark a batch for the decorators of this module
    """
    
    pass