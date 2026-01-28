import unittest








from src.chatbot.interfaces import arghandler






class ArghandlerTest(unittest.TestCase):

    def test1(self):
        to_test = arghandler.bind_args
    

        #test
        def func_a(text: str, extra_arg: str = None):
            return f"A: {text} - {extra_arg}"
    

        args = ["hello", "world"]
        kwargs = {"extra_arg": "test", "other_param": "value", "unused": "data"}
        
        result = to_test(func_a, args, kwargs)
        self.assertEqual(len(result.items()), 2)
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs.values()), 3)
        


    def test2(self):
        to_test = arghandler.bind_args
    

        #test
        def func_a(text: str, extra_arg: str = None):
            return f"A: {text} - {extra_arg}"
    

        args = ["hello"]
        kwargs = {"extra_arg": "test", "other_param": "value", "unused": "data"}
        
        result = to_test(func_a, args, kwargs)
        self.assertEqual(len(result.items()), 2)
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs.values()), 2)


    def test3(self):
        to_test = arghandler.bind_args
    

        #test
        def func_a(text: str, extra_arg: str = None):
            return f"A: {text} - {extra_arg}"
    

        args = []
        kwargs = {"extra_arg": "test", "other_param": "value", "unused": "data"}
        
        result = to_test(func_a, args, kwargs)
        self.assertEqual(len(result.items()), 1)
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs.values()), 2)

    
    def test4(self):
        to_test = arghandler.bind_args
    

        #test
        def func_a(text: str, extra_arg: str = None, *args, **kwargs):
            return f"A: {text} - {extra_arg}"
    

        args = []
        kwargs = {"extra_arg": "test", "other_param": "value", "unused": "data"}
        
        result = to_test(func_a, args, kwargs)
        self.assertEqual(len(args), 0)
        self.assertEqual(len(kwargs), 2)
        self.assertEqual(len(result), 3)
        self.assertIn("kwargs", result)
        self.assertEqual(len(result["kwargs"]), 2)