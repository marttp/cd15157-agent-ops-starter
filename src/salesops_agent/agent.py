import json
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from .approvals import ApprovalGate
from .config import load_settings, make_model, metadata
from .data_access import CRM
from .email_service import EmailService
from .guardrails import input_policy, output_policy, sanitize
from .run_context import RunContext
from .tools import Dispatcher


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


def run_agent(question, config=None, output=None, model=None, task_id=None, approval=None, principal=None, session_id=None):
    cfg, root = load_settings(config)
    ctx = RunContext(output or root / cfg.output_dir, question, metadata(cfg, root), task_id, sanitizer=sanitize)
    ctx.metadata["execution_mode"] = "scripted" if model is not None else "live"
    try:
        decision = input_policy(question)
        if decision.status == "blocked":
            ctx.emit("guardrail", {"layer": "input", **decision.model_dump()})
            return ctx.finish("blocked", "Request blocked by SalesOps policy.", cfg, decision.reason)
        ctx.emit("guardrail_decision", {"layer": "input", **decision.model_dump()})
        prior = []
        if session_id:
            if principal is None:
                raise ValueError("authenticated_principal_required")
            prior = principal.store.messages(principal, session_id)
            ctx.metadata.update({"user_id": principal.user_id, "session_id": session_id,
                                 "thread_id": f"{principal.user_id}:{session_id}"})
        crm = CRM(root / cfg.data_dir)
        emails = EmailService(ctx.output / "state/outbox.db", crm, ApprovalGate(ctx))
        dispatcher = Dispatcher(crm, emails, ctx.emit)
        model = model or make_model(cfg)
        graph = build_graph(model, dispatcher, ctx, cfg,
                            (root / cfg.prompt).read_text()+f"\nReference date: {cfg.reference_date}")
        result = graph.invoke({"messages": [*prior, HumanMessage(question)], "calls": 0},
                              {"configurable": {"thread_id": ctx.metadata.get("thread_id", ctx.run_id)}, "recursion_limit": 50})
        while result.get("__interrupt__"):
            pending = result["__interrupt__"][0].value
            if approval is None:
                return ctx.finish("pending_approval", "Approval required: " + json.dumps(pending), cfg)
            result = graph.invoke(Command(resume={"action_id": pending["action_id"], "decision": approval}),
                                  {"configurable": {"thread_id": ctx.metadata.get("thread_id", ctx.run_id)}, "recursion_limit": 50})
        answer = result["messages"][-1].content
        decision = output_policy(answer)
        if decision.status == "blocked":
            ctx.emit("guardrail", {"layer": "output", **decision.model_dump()})
            return ctx.finish("blocked", "Generated response blocked by SalesOps policy.", cfg, decision.reason)
        ctx.emit("guardrail_decision", {"layer": "output", **decision.model_dump()})
        status = "blocked" if any(e["kind"] == "guardrail" for e in ctx.events) else "success"
        failure = next((e["data"]["reason"] for e in ctx.events if e["kind"] == "guardrail"), None)
        if any(e["kind"] == "tool_result" and e["data"]["result"]["status"] == "failed" for e in ctx.events):
            status, failure = "failed", "tool_failure"
        if ctx.hitl_decision == "reject" and status == "success":
            status, failure = "rejected", "human_rejected"
        if session_id and status == "success":
            ctx.persist(status, answer)
            trace = json.loads((ctx.output / "traces" / f"{ctx.run_id}.json").read_text())
            principal.store.record(principal, session_id, {"run_id": ctx.run_id, "answer": sanitize(answer)}, trace)
        return ctx.finish(status, answer, cfg, failure)
    except Exception as error:
        ctx.usage_complete = False
        reason = str(error) if str(error) in {"provider_credentials_missing", "model_call_limit"} else type(error).__name__
        ctx.emit("error", {"reason": reason})
        return ctx.finish("failed", "Run failed. Inspect the trace using the run ID.", cfg, reason)
