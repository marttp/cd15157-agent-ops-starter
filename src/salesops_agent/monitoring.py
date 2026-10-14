import argparse
import json
from collections import Counter
from pathlib import Path

from .schemas import RunRecord


def load_records(path):
    if not path.exists():
        return []
    records = []
    for index, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(RunRecord.model_validate_json(line).model_dump())
        except ValueError as error:
            raise ValueError(f"invalid_run_record_line_{index}") from error
    if len({r["run_id"] for r in records}) != len(records):
        raise ValueError("duplicate_run_id")
    return records


def aggregate(records):
    n = len(records)
    statuses = Counter(r["final_status"] for r in records)
    costs = [r["estimated_cost_usd"] for r in records if r["estimated_cost_usd"] is not None]
    latencies = sorted(r["latency_s"] for r in records)
    return {
        "total_runs": n,
        "status_counts": dict(statuses),
        "success_rate": statuses["success"] / n if n else 0,
        "failure_rate": statuses["failed"] / n if n else 0,
        "average_latency_s": sum(latencies) / n if n else 0,
        "p95_latency_s": latencies[min(n - 1, int(n * 0.95))] if n else 0,
        "estimated_total_known_cost_usd": sum(costs),
        "estimated_average_known_cost_usd": sum(costs) / len(costs) if costs else None,
        "known_cost_runs": len(costs),
        "unknown_cost_runs": n - len(costs),
        "tool_call_counts": dict(Counter(t for r in records for t in r["tools_called"])),
        "tool_attempt_counts": dict(Counter(t for r in records for t in r["tools_attempted"])),
        "guardrail_blocks": sum(len(r["guardrail_interventions"]) for r in records),
        "hitl_approvals": sum(r["hitl_decision"] == "approve" for r in records),
        "hitl_rejections": sum(r["hitl_decision"] == "reject" for r in records),
        "common_failure_reasons": dict(
            Counter(r["failure_reason"] for r in records if r["failure_reason"])
        ),
        "execution_modes": dict(
            Counter(r["metadata"].get("execution_mode", "unknown") for r in records)
        ),
    }


def generate(output):
    output = Path(output)
    records = load_records(output / "logs/runs.jsonl")
    metrics = aggregate(records)
    metrics["metrics_by_execution_mode"] = {
        mode: aggregate(
            [r for r in records if r["metadata"].get("execution_mode", "unknown") == mode]
        )
        for mode in metrics["execution_modes"]
    }
    directory = output / "reports"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "monitoring_report.json").write_text(json.dumps(metrics, indent=2) + "\n")
    rows = [
        "# Monitoring report",
        "",
        "Rates use all recorded runs as denominator. Failed means runtime error; blocked, rejected and pending approval are separate outcomes. A correct block can pass evaluation.",
        "",
        "Costs use observed token usage and illustrative versioned rates. Unknown-cost runs are excluded from cost averages; totals are known-cost subtotals. Inspect metrics_by_execution_mode before comparing live and scripted runs.",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    rows += [f"| {key} | {json.dumps(value)} |" for key, value in metrics.items()]
    (directory / "monitoring_report.md").write_text("\n".join(rows) + "\n")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=".")
    args = parser.parse_args()
    print(json.dumps(generate(args.output), indent=2))
