import multiprocessing
from pathlib import Path
import pytest
from salesops_agent.data_access import CRM
from salesops_agent.sandbox import run_sandboxed


@pytest.mark.parametrize("code", ["eval('1')", "exec('1')", "open('/etc/passwd')", "__import__('os')",
                                  "import socket", "requests.get('https://example.org')",
                                  "internal_hr_data", "opportunities.__class__", "while True: pass",
                                  "sum(accounts, 'salary_usd')"])
def test_denied_capabilities(code):
    assert run_sandboxed(code, CRM(Path("data")).tables)["status"] == "blocked"


def test_correct_analysis():
    crm = CRM(Path("data"))
    assert run_sandboxed("count(opportunities)", crm.tables)["data"] == 182
    assert run_sandboxed("group_sum(opportunities, 'stage', 'amount_usd')", crm.tables)["data"] == {k: v["amount_usd"] for k, v in crm.pipeline().items()}
    assert run_sandboxed("count(filter_eq(opportunities, 'stage', 'Negotiation'))", crm.tables)["data"] == len(crm.open_opportunities("Negotiation"))


def test_timeout_stops_worker():
    before = {p.pid for p in multiprocessing.active_children()}
    result = run_sandboxed("count(opportunities)", CRM(Path("data")).tables, timeout=0.00001)
    assert result["reason"] == "execution_timeout"
    assert {p.pid for p in multiprocessing.active_children()} == before


def test_restricted_data_and_size():
    assert run_sandboxed("count(accounts)", {"internal_hr_data": []})["status"] == "blocked"
    assert run_sandboxed("count(accounts)", {"accounts": [{}] * 10001})["status"] == "blocked"
