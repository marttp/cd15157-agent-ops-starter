"""Validate observed logs/traces and reconcile the generated metrics."""

import json
import re
import sys
from pathlib import Path

from salesops_agent.monitoring import aggregate, load_records
from salesops_agent.schemas import TraceEvent


def verify(output):
    output = Path(output)
    records = load_records(output / "logs/runs.jsonl")
    assert records, "no_observed_runs"
    for record in records:
        trace = json.loads((output / "traces" / f"{record['run_id']}.json").read_text())
        assert trace["run_id"] == record["run_id"]
        assert trace["final_status"] == record["final_status"]
        assert trace["hitl_decision"] == record["hitl_decision"]
        for event in trace["events"]:
            TraceEvent.model_validate(event)
        raw = json.dumps(trace)
        assert not re.search(r"(?:voc-|sk-)[A-Za-z0-9._-]{8,}", raw), "credential_leak"
        assert '"salary_usd": 200000' not in raw
        assert "$2M equity bonus" not in raw
    saved = json.loads((output / "reports/monitoring_report.json").read_text())
    expected = aggregate(records)
    for key in expected:
        assert saved[key] == expected[key], f"metric_mismatch_{key}"
    print(f"Verified {len(records)} log/trace pairs and monitoring aggregates.")


if __name__ == "__main__":
    verify(sys.argv[1])
