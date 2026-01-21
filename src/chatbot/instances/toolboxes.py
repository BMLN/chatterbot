from ..interfaces.toolbox import ToolBox

from typing import override


class SequentialToolbox(ToolBox):

    @override
    def get_tool(self):
        tool = next((x for x in self.toolset if x not in self.in_use), None)
        
        if not tool:
            raise ToolBox.ToolError
        
        self.in_use.append(tool)

        return tool