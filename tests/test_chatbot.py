import unittest
from functools import wraps
from abc import ABC, abstractmethod
from typing import override







from src.interfaces import chatbot










class IsBatchTest(unittest.TestCase):

    def test1(self):
        to_test = chatbot.is_batch

        args = [{"a": 1, "b": "text", "c": None}]


        #test
        self.assertFalse(to_test(*args))


    def test2(self):
        to_test = chatbot.is_batch

        args = [[0, 1, 1, 1, 0, 0, 0, 0.5]]


        #test
        self.assertFalse(to_test(*args))


    def test3(self):
        to_test = chatbot.is_batch

        args = [[[0, 1, 1, 1, 0, 0, 0, 0.5]]]


        #test
        self.assertTrue(to_test(*args))
        

    def test4(self):
        to_test = chatbot.is_batch

        args = ["49507ebd-de55-528e-afdc-2258dd040d19"]


        #test
        self.assertFalse(to_test(*args))

    def test5(self):
        to_test = chatbot.is_batch

        args = [["49507ebd-de55-528e-afdc-2258dd040d19"]]


        #test
        self.assertTrue(to_test(*args))




class BatchifyTest(unittest.TestCase):
    
    def test1(self):
        to_test = chatbot.batchify

        def is_batch(x): return isinstance(x, list)

        @to_test("x")
        @to_test("y")
        def f(x, y):
            return(x, y)

        self.assertEqual(([1], [2]), f(1, 2))
        # Output: [1] [2]


#gened
class CheckFuncArgsTest(unittest.TestCase):
    
    
    def test_plain_function(self):
        def foo(a, b=2):
            return a + b
        self.assertTrue(chatbot.check_func_args(foo, 1))
        self.assertFalse(chatbot.check_func_args(foo))

    def test_bound_instance_method(self):
        class A:
            def inst(self, x, y=0):
                return x + y
        a = A()
        self.assertTrue(chatbot.check_func_args(a.inst, 5))
        self.assertFalse(chatbot.check_func_args(a.inst))

    def test_unbound_instance_method(self):
        class B:
            def inst(self, x):
                return x
        b = B()
        self.assertTrue(chatbot.check_func_args(B.inst, b, 10))  # self provided manually
        self.assertFalse(chatbot.check_func_args(B.inst, 10))    # self missing

    def test_static_method(self):
        class C:
            @staticmethod
            def st(a, b):
                return a + b
        self.assertTrue(chatbot.check_func_args(C.st, 1, 2))
        self.assertFalse(chatbot.check_func_args(C.st, 1))  # missing second arg

    ####

    def test_decorator_without_arguments(self):
        """check_func_args should succeed when passing the wrapped function to a simple decorator."""

        # A simple decorator that takes the function as its only argument
        def my_decorator(func):
            def wrapper(*a, **kw):
                return func(*a, **kw)
            return wrapper

        # Check with correct arg (the function to decorate)
        def dummy(): pass
        self.assertTrue(chatbot.check_func_args(my_decorator, dummy))

        # Check with no args — should fail (since my_decorator requires 1)
        self.assertFalse(chatbot.check_func_args(my_decorator))

    def test_decorator_with_arguments(self):
        """check_func_args should succeed when providing the correct decorator arguments."""

        # A decorator factory
        def decorator_factory(x, y):
            def actual_decorator(func):
                def wrapper(*a, **kw):
                    return func(*a, **kw)
                return wrapper
            return actual_decorator

        # Check with no args — should fail (since factory requires x and y)
        self.assertFalse(chatbot.check_func_args(decorator_factory))

        # Check with correct args — should succeed
        self.assertTrue(chatbot.check_func_args(decorator_factory, 1, 2))

        # Check with missing one arg — should fail
        self.assertFalse(chatbot.check_func_args(decorator_factory, 1))





























#gened
class TestSharedDecoratorInheritanceType(unittest.TestCase):
    
    def test_get_abstractmethods_returns_abstract_methods(self):
        """Test that get_abstractmethods correctly identifies abstract methods"""
        class TestBase(ABC, metaclass=chatbot.SharedDecoratorInheritanceType):
            @abstractmethod
            def abstract_method(self):
                pass
            
            def concrete_method(self):
                pass
        
        abstract_methods = chatbot.SharedDecoratorInheritanceType.get_abstractmethods(TestBase)
        method_names = [name for name, _ in abstract_methods]
        
        self.assertIn('abstract_method', method_names)
        self.assertNotIn('concrete_method', method_names)
    
    def test_get_abstractmethods_returns_empty_for_no_abstract(self):
        """Test that get_abstractmethods returns empty list when no abstract methods"""
        class TestBase(ABC, metaclass=chatbot.SharedDecoratorInheritanceType):
            def concrete_method(self):
                pass
        
        abstract_methods = chatbot.SharedDecoratorInheritanceType.get_abstractmethods(TestBase)
        self.assertEqual(len(abstract_methods), 0)
    

    
    def test_concrete_class_inherits_from_abstract_base(self):
        """Test that concrete classes can be created from abstract base and is not transferred"""
        class AbstractBase(ABC, metaclass=chatbot.SharedDecoratorInheritanceType):
            @override
            @abstractmethod
            def my_method(self):
                pass
        
        class ConcreteClass(AbstractBase):
            def my_method(self):
                return "implemented"
        
        instance = ConcreteClass()
        self.assertEqual(instance.my_method(), "implemented")
        self.assertFalse(getattr(ConcreteClass.my_method, "__isabstractmethod__", False))
        self.assertTrue(getattr(ConcreteClass.my_method, "__override__", False))

def test_decorator_inheritance(self):
        """Test that decorators are inherited from abstract base to concrete class"""
        # Define a decorator that marks the function
        def sample_decorator(func):
            func._decorated = True
            func._decorator_name = "sample_decorator"
            return func
        
        # Create abstract base with decorated abstract method
        class AbstractBase(ABC, metaclass=chatbot.SharedDecoratorInheritanceType):
            @abstractmethod
            @sample_decorator
            def my_method(self):
                pass
        
        # Create concrete implementation
        class ConcreteClass(AbstractBase):
            def my_method(self):
                return "implemented"
        
        # Verify the decorator has been applied
        found_decorator = chatbot.SharedDecoratorInheritanceType.get_from_class_module(
            ConcreteClass, 'sample_decorator'
        )
        self.assertIsNotNone(found_decorator)
        self.assertEqual(found_decorator, sample_decorator)
        











































if __name__ == "__main__":
    unittest.main()