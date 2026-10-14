"""Execute original notebook in a temporary kernel/data copy; export no raw outputs."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

from salesops_agent.config import load_settings


def main():
    _, root = load_settings()
    provider = os.getenv("LLM_PROVIDER", "vocareum")
    key = os.getenv("VOCAREUM_API_KEY" if provider == "vocareum" else "OPENAI_API_KEY")
    if not key:
        print("Provider credentials missing. Prototype live execution has not occurred.")
        return 2
    with tempfile.TemporaryDirectory(prefix="agentops-prototype-") as name:
        directory = Path(name)
        shutil.copytree(root / "starter/data", directory / "data")
        kernel = directory / "kernels/agentops-prototype"
        kernel.mkdir(parents=True)
        (kernel / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                    "display_name": "AgentOps isolated prototype",
                    "language": "python",
                }
            )
        )
        os.environ["JUPYTER_PATH"] = str(directory) + os.pathsep + os.getenv("JUPYTER_PATH", "")
        notebook = nbformat.read(root / "starter/project_starter.ipynb", as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == "code" and "agent = create_agent(" in cell.source:
                cell.source = "from langchain_openai import ChatOpenAI\nimport os\nagent = create_agent(model=ChatOpenAI(model='gpt-4o-mini', api_key=os.environ.get('VOCAREUM_API_KEY') if os.environ.get('LLM_PROVIDER','vocareum') == 'vocareum' else os.environ.get('OPENAI_API_KEY'), base_url='https://openai.vocareum.com/v1' if os.environ.get('LLM_PROVIDER','vocareum') == 'vocareum' else None), tools=tools, system_prompt=SYSTEM_PROMPT)"
        NotebookClient(
            notebook,
            timeout=120,
            kernel_name="agentops-prototype",
            allow_errors=True,
            resources={"metadata": {"path": str(directory)}},
        ).execute()
        failures = [
            {"cell": i, "error_type": out["ename"]}
            for i, cell in enumerate(notebook.cells)
            for out in cell.get("outputs", [])
            if out.get("output_type") == "error"
        ]
        report = {
            "original_notebook_preserved": True,
            "temporary_provider_adapter": True,
            "isolated_outbox": True,
            "executed_code_cells": sum(
                c.cell_type == "code" and c.execution_count is not None for c in notebook.cells
            ),
            "errors": failures,
            "raw_outputs_exported": False,
        }
        (root / "reports/prototype_review.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
