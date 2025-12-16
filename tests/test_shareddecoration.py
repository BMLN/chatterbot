import unittest







from src.chatbot.interfaces import shared_decoration


from typing import override
from abc import ABC, abstractmethod
from functools import wraps




def my_decorator(func):
    func.__ay__ = True
    return func

class Test_singletondecorator(unittest.TestCase):

    def test1(self):
        to_test = shared_decoration.singleton

        
        #setup
        @to_test
        def greeter(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return f"greetings {func(*args, **kwargs)}"
            return wrapper

        @greeter
        @greeter
        def toperson1():
            return "Buzz Lightyear"

        @greeter
        def toperson2():
            return "Woody"
        
        
        #test
        result1 = toperson1()
        result2 = toperson2()

        self.assertEqual(result1, "greetings Buzz Lightyear")
        self.assertEqual(result2, "greetings Woody")
        





class Test_inplacedecorator(unittest.TestCase):

    def test1(self):
        to_test = shared_decoration.inplace

        
        #setup
        @to_test
        def greeter1(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return f"greetings {func(*args, **kwargs)}"
            return wrapper
        
        @to_test
        def greeter2(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return f"Hello there {func(*args, **kwargs)}"
            return wrapper

        @greeter2
        @greeter2
        def toperson1():
            return "General Kenobi"

        @greeter1
        @greeter2
        def toperson2():
            return "Obi Wan"
        
        
        #test
        result1 = toperson1()
        result2 = toperson2()

        self.assertEqual(result1, "Hello there General Kenobi")
        self.assertEqual(result2, "greetings Obi Wan")











class Test_SharedDecoration(unittest.TestCase):
    

    def test1(self):
        to_test = shared_decoration.SharedDecoratorInheritanceType.parse_decorators


        #setup
        def my_decorator(func):
            func.decorated = True
            return func
        
        def param_decorator(value):
            def wrapper(func):
                func.param_value = value
                return func
            return wrapper
        
        @my_decorator
        @param_decorator("test")
        def example_function():
            """Example function with decorators."""
            pass
        
        class ExampleClass:
            @my_decorator
            def method(self):
                """Example method with decorator."""
                pass
        
        
        
        #test
        self.assertEqual(len(to_test(example_function)), 2)
        self.assertEqual(len(to_test(ExampleClass.method)), 1)






#gened
class TestSharedDecoratorInheritanceType(unittest.TestCase):
    
    def test_get_abstractmethods_returns_abstract_methods(self):
        """Test that get_abstractmethods correctly identifies abstract methods"""
        class TestBase(ABC, metaclass=shared_decoration.SharedDecoratorInheritanceType):
            @abstractmethod
            def abstract_method(self):
                pass
            
            def concrete_method(self):
                pass
        
        abstract_methods = shared_decoration.SharedDecoratorInheritanceType.get_abstractmethods(TestBase)
        method_names = [name for name, _ in abstract_methods]
        
        self.assertIn('abstract_method', method_names)
        self.assertNotIn('concrete_method', method_names)
    
    def test_get_abstractmethods_returns_empty_for_no_abstract(self):
        """Test that get_abstractmethods returns empty list when no abstract methods"""
        class TestBase(ABC, metaclass=shared_decoration.SharedDecoratorInheritanceType):
            def concrete_method(self):
                pass
        
        abstract_methods = shared_decoration.SharedDecoratorInheritanceType.get_abstractmethods(TestBase)
        self.assertEqual(len(abstract_methods), 0)
    

    
    def test_concrete_class_inherits_from_abstract_base(self):
        """Test that concrete classes can be created from abstract base and is not transferred"""
    
        class AbstractBase(ABC, metaclass=shared_decoration.SharedDecoratorInheritanceType):
            @override
            @abstractmethod
            def my_method(self):
                pass
        
        class ConcreteClass(AbstractBase):
            @override
            def my_method(self):
                return "implemented"

        instance = ConcreteClass()
        self.assertEqual(instance.my_method(), "implemented")
        self.assertFalse(getattr(ConcreteClass.my_method, "__isabstractmethod__", False))
        self.assertTrue(getattr(ConcreteClass.my_method, "__override__", False))



    # def test_decorator_inheritance(self):
    #         """Test that decorators are inherited from abstract base to concrete class"""
    #         # Define a decorator that marks the function
    #         def sample_decorator(func):
    #             func._decorated = True
    #             func._decorator_name = "sample_decorator"
    #             return func
            
    #         # Create abstract base with decorated abstract method
    #         class AbstractBase(ABC, metaclass=shared_decoration.SharedDecoratorInheritanceType):
    #             @abstractmethod
    #             @sample_decorator
    #             def my_method(self):
    #                 pass
            
    #         # Create concrete implementation
    #         class ConcreteClass(AbstractBase):
    #             def my_method(self):
    #                 return "implemented"
            
    #         # Verify the decorator has been applied
    #         found_decorator = shared_decoration.SharedDecoratorInheritanceType.get_from_class_module(
    #             ConcreteClass, 'sample_decorator'
    #         )
    #         self.assertIsNotNone(found_decorator)
    #         self.assertEqual(found_decorator, sample_decorator)