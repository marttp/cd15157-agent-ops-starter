import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .schemas import RunRecord, TraceEvent


def basic_sanitize(value):
    if isinstance(value, dict):
        return {
            k: "[REDACTED]"
            if any(w in k.lower() for w in ["api_key", "password", "secret"])
            else basic_sanitize(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [basic_sanitize(v) for v in value]
    if isinstance(value, str):
        return re.sub(r"(?:voc-|sk-)[A-Za-z0-9._-]+", "[REDACTED]", value)
    return value


class RunContext:
    def __init__(self, output, question, metadata, task_id=None, sanitizer=basic_sanitize):
        self.run_id = str(uuid4())
        self.timestamp = datetime.now(UTC).isoformat()
        self.started = time.perf_counter()
        self.output = Path(output)
        self.question, self.metadata, self.task_id = question, metadata, task_id
        self.events, self.usage, self.usage_complete = (
            [],
            {"input_tokens": 0, "output_tokens": 0},
            True,
        )
        self.sanitize = sanitizer
        self.hitl_decision = None
        for folder in ["logs", "traces"]:
            (self.output / folder).mkdir(parents=True, exist_ok=True)

    def emit(self, kind, data):
        event = TraceEvent(
            sequence=len(self.events),
            timestamp=datetime.now(UTC).isoformat(),
            kind=kind,
            data=self.sanitize(data),
        ).model_dump()
        self.events.append(event)
        self.persist("running", "")

    def persist(self, status, answer):
        trace = self.sanitize(
            {
                "run_id": self.run_id,
                "timestamp": self.timestamp,
                "input": self.question,
                "metadata": self.metadata,
                "events": self.events,
                "final_status": status,
                "final_output": answer,
                "hitl_decision": self.hitl_decision,
            }
        )
        path = self.output / "traces" / f"{self.run_id}.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(trace, indent=2) + "\n")
        temp.replace(path)

    def finish(self, status, answer, cfg, failure=None):
        self.persist(status, answer)
        usage = self.usage if self.usage_complete else None
        cost = (
            (
                self.usage["input_tokens"] * cfg.input_usd_per_million
                + self.usage["output_tokens"] * cfg.output_usd_per_million
            )
            / 1e6
            if usage is not None
            else None
        )
        record = RunRecord(
            run_id=self.run_id,
            timestamp=self.timestamp,
            user_input=self.sanitize(self.question),
            task_id=self.task_id,
            final_status=status,
            tools_called=[
                e["data"]["name"]
                for e in self.events
                if e["kind"] == "tool_result"
                and e["data"]["result"]["status"] in {"success", "sent"}
            ],
            tools_attempted=[e["data"]["name"] for e in self.events if e["kind"] == "tool_attempt"],
            latency_s=time.perf_counter() - self.started,
            estimated_cost_usd=cost,
            usage=usage,
            guardrail_interventions=[e["data"] for e in self.events if e["kind"] == "guardrail"],
            hitl_decision=self.hitl_decision,
            failure_reason=failure,
            metadata=self.metadata,
        )
        with (self.output / "logs/runs.jsonl").open("a") as f:
            f.write(json.dumps(self.sanitize(record.model_dump())) + "\n")
        return {
            "run_id": self.run_id,
            "status": status,
            "answer": self.sanitize(answer),
            "record": record.model_dump(),
        }
