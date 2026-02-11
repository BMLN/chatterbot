import unittest






from src.chatbot.interfaces import chatbot






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










class BoundArgsTest(unittest.TestCase):
    
    def test_boundargs(self):
        to_test = chatbot.Chatbot._bound_args
        
        
        #setup

















if __name__ == "__main__":
    unittest.main()