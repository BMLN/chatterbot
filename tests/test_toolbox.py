import unittest






from src.chatbot.instances import toolboxes
from src.chatbot.interfaces import toolbox







class ToolificationTest(unittest.TestCase):
    
    def test_toolification(self):
        to_test = toolbox.as_tool


        #test
        class TestClass():
            def double(self, data): 
                return data * 2

        tooled = to_test(TestClass.double)(TestClass)
        self.assertEqual(tooled().apply(2), 4)





class SequentialToolboxTest(unittest.TestCase):

    def test1(self):
        to_test = toolboxes.SequentialToolbox


        #test
        class TestTool(toolbox.Tool):
            def apply(self, data, *args, **kwargs):
                return super().apply(data, *args, **kwargs)
                  
        with to_test([ TestTool(), TestTool() ]) as ctx:
            self.assertEqual(ctx.get_tool(), ctx.toolset[0])
            self.assertEqual(ctx.get_tool(), ctx.toolset[1])

            with self.assertRaises(toolbox.ToolBox.ToolError):
                ctx.get_tool()
        


    def test2(self):
        to_test = toolboxes.SequentialToolbox


        #test
        class TestClass():
            def double(self, data): 
                return data * 2

                  
        with to_test([ toolbox.as_tool(TestClass.double)(TestClass)(), toolbox.as_tool(TestClass.double)(TestClass)() ]) as ctx:
            self.assertEqual(ctx.get_tool(), ctx.toolset[0])
            self.assertEqual(ctx.get_tool(), ctx.toolset[1])

            with self.assertRaises(toolbox.ToolBox.ToolError):
                ctx.get_tool()

