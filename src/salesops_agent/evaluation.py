import argparse
import json
from pathlib import Path
from .agent import run_agent
from .config import load_settings
from .testing import ScriptedModel


def evaluate(offline=False, output=None):
    cfg, root = load_settings()
    output = Path(output or root)
    rows = []
    for case in json.loads((root / "evaluation/scenarios.json").read_text()):
        model = ScriptedModel([(case["tool"], case["args"])]) if offline else None
        result = run_agent(case["question"], output=output, model=model, task_id=case["id"])
        trace = json.loads((output / "traces" / f"{result['run_id']}.json").read_text())
        tool_seen = any(e["kind"] == "tool_result" and e["data"]["name"] == case["tool"] and e["data"]["result"]["status"] == "success" for e in trace["events"])
        passed = result["status"] == "success" and tool_seen and all(t.lower() in result["answer"].lower() for t in case["terms"])
        rows.append({"task_id": case["id"], "run_id": result["run_id"], "mode": "offline-scripted" if offline else "live",
                     "passed": passed, "latency_s": result["record"]["latency_s"],
                     "estimated_cost_usd": result["record"]["estimated_cost_usd"],
                     "failure_reason": None if passed else result["record"]["failure_reason"] or "expectations_not_met"})
    reports = output / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "evaluation_report.json").write_text(json.dumps(rows, indent=2)+"\n")
    lines = ["# Evaluation report", "", "Offline results do not establish live model behavior.", "",
             "| Task | Mode | Passed | Latency s | Estimated USD | Failure |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['task_id']} | {r['mode']} | {r['passed']} | {r['latency_s']:.4f} | {r['estimated_cost_usd']} | {r['failure_reason']} |" for r in rows]
    (reports / "evaluation_report.md").write_text("\n".join(lines)+"\n")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    rows = evaluate(args.offline, args.output)
    print(f"{sum(r['passed'] for r in rows)}/{len(rows)} tasks passed")
    raise SystemExit(0 if all(r["passed"] for r in rows) else 1)
