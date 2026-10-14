"""Explicit scripted model double, only for offline boundary verification."""
import json
from langchain_core.messages import AIMessage, ToolMessage


class ScriptedModel:
    def __init__(self, calls=None, final=None):
        self.calls, self.final, self.invocations = calls or [], final, 0

    def bind_tools(self, definitions):
        return self

    def invoke(self, messages):
        self.invocations += 1
        if self.invocations == 1 and self.calls:
            return AIMessage(content="", tool_calls=[{"id": f"call_{i}", "name": name,
                                                      "args": args} for i, (name, args) in enumerate(self.calls)])
        outputs = [m.content for m in messages if isinstance(m, ToolMessage)]
        return AIMessage(content=self.final if self.final is not None else json.dumps(outputs))
