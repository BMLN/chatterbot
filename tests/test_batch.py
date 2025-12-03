import unittest








from src.chatbot.interfaces import batch








class IsBatchTest(unittest.TestCase):

    def test1(self):
        to_test = batch.is_batch

        args = [{"a": 1, "b": "text", "c": None}]


        #test
        self.assertFalse(to_test(*args))


    def test2(self):
        to_test = batch.is_batch

        args = [[0, 1, 1, 1, 0, 0, 0, 0.5]]


        #test
        self.assertFalse(to_test(*args))


    def test3(self):
        to_test = batch.is_batch

        args = [[[0, 1, 1, 1, 0, 0, 0, 0.5]]]


        #test
        self.assertTrue(to_test(*args))
        

    def test4(self):
        to_test = batch.is_batch

        args = ["49507ebd-de55-528e-afdc-2258dd040d19"]


        #test
        self.assertFalse(to_test(*args))


    def test5(self):
        to_test = batch.is_batch

        args = [["49507ebd-de55-528e-afdc-2258dd040d19"]]


        #test
        self.assertTrue(to_test(*args))


    def test6(self):
        to_test = batch.is_batch

        args = [["this is", "some sort of text", "which should be a batch"]]


        #test
        self.assertFalse(to_test(*args))


    def test7(self):
        to_test = batch.is_batch

        args = [["uuid1", "uuid2", "uuid3"]]


        #test
        self.assertTrue(to_test(*args))








class BatchifyTest(unittest.TestCase):
    
    def test1(self):
        to_test = batch.batchify


        @to_test("x")
        @to_test("y")
        def f(x, y):
            return(x, y)

        self.assertEqual(([1], [2]), f(1, 2))
        # Output: [1] [2]

    def test2(self):
        to_test = batch.batchify


        @to_test("x")
        @to_test("y")
        def f(x, y):
            return(x, y)

        self.assertEqual((["something"], ["something else"]), f("something", "something else"))


    def test3(self):
        to_test = batch.batchify


        @to_test("x", list[str])
        @to_test("y", list[str])
        def f(x, y):
            return(x, y)

        self.assertEqual((["something", "else"], ["something else"]), f(["something", "else"], ["something else"]))


    def test4(self):
        to_test = batch.batchify


        @to_test("x", list[str])
        @to_test("y", list[list[str]])
        def f(x, y):
            return(x, y)

        self.assertEqual((["something", "else"], [["something else"]]), f(["something", "else"], [["something else"]]))













    