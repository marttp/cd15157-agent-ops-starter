import json

from salesops_agent.agent import run_agent
from salesops_agent.evaluation import evaluate
from salesops_agent.testing import ScriptedModel


def test_same_graph_evaluation(tmp_path):
    rows = evaluate(offline=True, output=tmp_path)
    assert len(rows) >= 30 and all(r["passed"] for r in rows)
    assert all(r["estimated_cost_usd"] is None for r in rows if r["mode"] == "offline-scripted")
    assert len(list((tmp_path / "traces").glob("*.json"))) == len(rows)


def test_model_error_is_observable(tmp_path):
    class Broken(ScriptedModel):
        def invoke(self, messages):
            raise TimeoutError("never expose provider body or credentials")

    result = run_agent("pipeline", output=tmp_path, model=Broken())
    assert result["status"] == "failed"
    trace = json.loads((tmp_path / "traces" / f"{result['run_id']}.json").read_text())
    assert trace["events"][-1]["data"]["reason"] == "TimeoutError"
