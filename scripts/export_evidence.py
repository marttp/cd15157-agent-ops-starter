"""Copy validated sanitized evidence from a clean committed implementation."""

import json
import shutil
import sys
from pathlib import Path

from verify_artifacts import verify


def export(output, label):
    output = Path(output)
    verify(output)
    target = Path("reports/evidence")
    target.mkdir(parents=True, exist_ok=True)
    for stem in ["evaluation_report", "monitoring_report"]:
        for extension in ["json", "md"]:
            shutil.copyfile(
                output / "reports" / f"{stem}.{extension}", target / f"{stem}_{label}.{extension}"
            )
    rows = json.loads((output / "reports/evaluation_report.json").read_text())
    for task in [
        "safe-account",
        "input-1",
        "deny-lookup_internal_hr_data",
        "sandbox-allowed",
        "email-approve",
        "email-reject",
        "email-None",
        "output-1",
        "provider-timeout",
    ]:
        row = next(r for r in rows if r["task_id"] == task)
        shutil.copyfile(
            output / "traces" / f"{row['run_id']}.json", target / f"trace_{task}_{label}.json"
        )
    print(f"Exported validated {label} evidence.")


if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2])
