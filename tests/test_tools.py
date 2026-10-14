from pathlib import Path

import pytest

from salesops_agent.data_access import CRM
from salesops_agent.email_service import EmailService
from salesops_agent.tools import Dispatcher


@pytest.fixture
def dispatcher(tmp_path):
    crm = CRM(Path("data"))
    return Dispatcher(crm, EmailService(tmp_path / "outbox.db", crm))


def test_customer_and_approved_data(dispatcher):
    assert len(dispatcher.crm.customer_ids) == 27
    assert "internal_hr_data" not in dispatcher.crm.tables
    assert dispatcher.crm.resolve("acme corp")["account_id"] == "A001"
    with pytest.raises(ValueError, match="ambiguous"):
        dispatcher.crm.resolve("a")


def test_boundary_and_side_effect(dispatcher):
    assert dispatcher.call("lookup_internal_hr_data", {"query": "CEO bonus"})["status"] == "blocked"
    assert dispatcher.call("lookup_account_context", {"account": "Acme", "fields": ["salary_usd"]})["status"] == "blocked"
    email = dispatcher.call("draft_email", {"account": "Acme", "purpose": "next steps"})["data"]
    assert dispatcher.call("send_email", email)["reason"] == "approval_required"
    assert dispatcher.emails.messages() == []


def test_pipeline_independent_total(dispatcher):
    import json
    rows = json.loads(Path("data/opportunities.json").read_text())
    result = dispatcher.call("summarize_pipeline", {})["data"]
    assert sum(r["count"] for r in result.values()) == len(rows)
    assert sum(r["amount_usd"] for r in result.values()) == sum(r["amount_usd"] for r in rows)
