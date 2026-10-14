import argparse
import json
from pathlib import Path

from .agent import run_agent
from .config import load_settings
from .data_access import CRM
from .email_service import EmailService
from .monitoring import generate
from .testing import ScriptedModel


class FailingModel(ScriptedModel):
    def invoke(self, messages):
        raise TimeoutError("sanitized provider timeout")


def select(value, path):
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def check_case(case, result, trace):
    if result["status"] != case.get("status", "success"):
        return "unexpected_runtime_status"
    if case.get("layer") and not any(e["kind"] == "guardrail" and e["data"]["layer"] == case["layer"] for e in trace["events"]):
        return "missing_guardrail_evidence"
    if case.get("tool") and case.get("status", "success") == "success":
        events = [e for e in trace["events"] if e["kind"] == "tool_result" and e["data"]["name"] == case["tool"] and e["data"]["result"]["status"] in {"success", "sent"}]
        if not events:
            return "expected_tool_not_executed"
        for assertion in case.get("assertions", []):
            try:
                observed = select(events[-1]["data"]["result"], assertion["path"])
                if observed != assertion["equals"]:
                    return "incorrect_crm_value"
            except (KeyError, IndexError, TypeError):
                return "missing_crm_value"
    answer = result["answer"].lower().replace(",", "")
    if not all(t.lower().replace(",", "") in answer for t in case.get("terms", [])):
        return "answer_expectations_not_met"
    return None


def evaluate(offline=False, output=None, baseline=None):
    _, root = load_settings()
    output = Path(output or root)
    rows = []
    cases = json.loads((root / "evaluation/scenarios.json").read_text())
    for case in cases:
        case_output = output / "evaluation-runs" / case["id"]
        kind = case.get("kind", "live")
        mode = "offline-scripted" if kind == "live" and offline else "live" if kind == "live" else "fault-injection"
        args = case.get("args", {})
        if kind == "email":
            crm = CRM(root / "data")
            args = EmailService(case_output / "draft.db", crm).draft("Acme Corp", "next steps").model_dump()
        if kind == "error":
            model = FailingModel()
        elif kind == "live" and not offline:
            model = None
        else:
            model = ScriptedModel([(case["tool"], args)] if case.get("tool") else [], final=case.get("final"))
        result = run_agent(case["question"], output=case_output, model=model, task_id=case["id"], approval=case.get("approval"))
        trace = json.loads((case_output / "traces" / f"{result['run_id']}.json").read_text())
        failure = check_case(case, result, trace)
        if kind == "email":
            crm = CRM(root / "data")
            actual = len(EmailService(case_output / "state/outbox.db", crm).messages())
            if actual != case["outbox_count"]:
                failure = "incorrect_email_side_effect"
            if not any(e["kind"] == "approval_requested" for e in trace["events"]):
                failure = "missing_approval_request"
            if result["record"]["hitl_decision"] != case.get("approval"):
                failure = "incorrect_approval_decision"
        # Copy sanitized observed records/traces to the report's shared run collection.
        (output / "logs").mkdir(parents=True, exist_ok=True)
        (output / "traces").mkdir(parents=True, exist_ok=True)
        with (output / "logs/runs.jsonl").open("a") as f:
            f.write(json.dumps(result["record"])+"\n")
        (output / "traces" / f"{result['run_id']}.json").write_text(json.dumps(trace, indent=2)+"\n")
        rows.append({"task_id": case["id"], "run_id": result["run_id"], "mode": mode,
                     "expected_status": case.get("status", "success"), "observed_status": result["status"],
                     "passed": failure is None, "latency_s": result["record"]["latency_s"],
                     "estimated_cost_usd": result["record"]["estimated_cost_usd"], "usage": result["record"]["usage"],
                     "versions": result["record"]["metadata"],
                     "runtime_failure_reason": result["record"]["failure_reason"], "failure_reason": failure})
    reports = output / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "evaluation_report.json").write_text(json.dumps(rows, indent=2)+"\n")
    lines = ["# Evaluation report", "", "Offline/scripted cases prove controls, not live model behavior. Cost rates are illustrative; unknown usage is null.", "",
             "| Task | Mode | Passed | Latency s | Estimated USD | Failure |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r['task_id']} | {r['mode']} | {r['passed']} | {r['latency_s']:.4f} | {r['estimated_cost_usd']} | {r['failure_reason']} |" for r in rows]
    if baseline:
        previous = {r["task_id"]: r for r in json.loads(Path(baseline).read_text())}
        regressions = [r["task_id"] for r in rows if previous.get(r["task_id"], {}).get("passed") and not r["passed"]]
        (reports / "regression_report.json").write_text(json.dumps({"regressions": regressions}, indent=2)+"\n")
        lines += ["", "Regressions against supplied baseline: " + json.dumps(regressions)]
    (reports / "evaluation_report.md").write_text("\n".join(lines)+"\n")
    generate(output)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--baseline")
    args = parser.parse_args()
    rows = evaluate(args.offline, args.output, args.baseline)
    print(f"{sum(r['passed'] for r in rows)}/{len(rows)} tasks passed")
    raise SystemExit(0 if all(r["passed"] for r in rows) else 1)
