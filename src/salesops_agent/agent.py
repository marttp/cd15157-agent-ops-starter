import json
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .config import load_settings, make_model, metadata
from .data_access import CRM
from .email_service import EmailService
from .tools import Dispatcher
from .run_context import RunContext


class State(TypedDict):
    messages: list
    calls: int


def build_graph(model, dispatcher, ctx, cfg, prompt):
    bound = model.bind_tools(dispatcher.definitions())

    def model_node(state):
        if state["calls"] >= cfg.max_model_calls:
            raise RuntimeError("model_call_limit")
        response = bound.invoke([SystemMessage(prompt), *state["messages"]])
        usage = getattr(response, "usage_metadata", None)
        if usage:
            for key in ctx.usage:
                ctx.usage[key] += usage[key]
        else:
            ctx.usage_complete = False
        ctx.emit("model", {"model": cfg.model, "usage": usage, "tool_calls": response.tool_calls,
                           "output": response.content})
        return {"messages": [*state["messages"], response], "calls": state["calls"]+1}

    def tools_node(state):
        messages = list(state["messages"])
        for call in messages[-1].tool_calls:
            result = dispatcher.call(call["name"], call["args"])
            messages.append(ToolMessage(json.dumps(result), tool_call_id=call["id"]))
        return {"messages": messages}

    graph = StateGraph(State)
    graph.add_node("model", model_node)
    graph.add_node("tools", tools_node)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", lambda s: "tools" if s["messages"][-1].tool_calls else END)
    graph.add_edge("tools", "model")
    return graph.compile(checkpointer=InMemorySaver())


def run_agent(question, config=None, output=None, model=None, task_id=None, approval=None):
    cfg, root = load_settings(config)
    ctx = RunContext(output or root / cfg.output_dir, question, metadata(cfg, root), task_id)
    try:
        crm = CRM(root / cfg.data_dir)
        emails = EmailService(ctx.output / "state/outbox.db", crm)
        dispatcher = Dispatcher(crm, emails, ctx.emit)
        model = model or make_model(cfg)
        graph = build_graph(model, dispatcher, ctx, cfg,
                            (root / cfg.prompt).read_text()+f"\nReference date: {cfg.reference_date}")
        result = graph.invoke({"messages": [HumanMessage(question)], "calls": 0},
                              {"configurable": {"thread_id": ctx.run_id}, "recursion_limit": 50})
        answer = result["messages"][-1].content
        status = "blocked" if any(e["kind"] == "guardrail" for e in ctx.events) else "success"
        return ctx.finish(status, answer, cfg)
    except Exception as error:
        ctx.usage_complete = False
        reason = str(error) if str(error) in {"provider_credentials_missing", "model_call_limit"} else type(error).__name__
        ctx.emit("error", {"reason": reason})
        return ctx.finish("failed", "Run failed. Inspect the trace using the run ID.", cfg, reason)
