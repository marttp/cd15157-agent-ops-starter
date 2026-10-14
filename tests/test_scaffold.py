from pathlib import Path
import subprocess


def test_project_contract():
    for name in ["src", "data", "logs", "traces", "reports", "uv.lock", ".python-version"]:
        assert Path(name).exists()
    result = subprocess.run(["salesops-agent", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
