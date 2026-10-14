import pytest

from salesops_agent.agent import run_agent
from salesops_agent.monitoring import aggregate, generate, load_records
from salesops_agent.testing import ScriptedModel


def test_aggregation_reconciles_outcomes(tmp_path):
    run_agent("Show pipeline", output=tmp_path, model=ScriptedModel(final="Safe response"))
    run_agent("CEO bonus", output=tmp_path, model=ScriptedModel())
    metrics = generate(tmp_path)
    assert metrics["total_runs"] == 2
    assert metrics["success_rate"] == .5 and metrics["failure_rate"] == 0
    assert metrics["status_counts"]["blocked"] == 1 and metrics["guardrail_blocks"] == 1
    assert metrics["unknown_cost_runs"] == 1 and metrics["known_cost_runs"] == 1
    assert metrics["estimated_total_known_cost_usd"] == 0
    assert len(load_records(tmp_path / "logs/runs.jsonl")) == 2


def test_empty_and_corrupt_report(tmp_path):
    assert aggregate([])["total_runs"] == 0
    path = tmp_path / "runs.jsonl"
    path.write_text('{"broken":true}\n')
    with pytest.raises(ValueError, match="invalid_run_record_line_1"):
        load_records(path)
