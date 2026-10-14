from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Decision(Contract):
    status: Literal["allowed", "blocked"]
    reason: str
    policy: str = "salesops-data-access-v1"


class ToolResult(Contract):
    status: Literal["success", "blocked", "pending_approval", "rejected", "sent", "failed"]
    reason: str = ""
    data: Any = None


class Email(Contract):
    account_id: str
    to: str
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=4000)


class TraceEvent(Contract):
    sequence: int
    timestamp: str
    kind: str
    data: dict[str, Any]


class RunRecord(Contract):
    run_id: str
    timestamp: str
    user_input: str
    task_id: str | None = None
    final_status: str
    tools_called: list[str]
    tools_attempted: list[str]
    latency_s: float
    estimated_cost_usd: float | None
    usage: dict[str, int] | None
    guardrail_interventions: list[dict[str, Any]]
    hitl_decision: str | None = None
    failure_reason: str | None = None
    metadata: dict[str, Any]
