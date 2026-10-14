import pytest
from pydantic import ValidationError

from salesops_agent.config import load_settings, metadata
from salesops_agent.schemas import Email


def test_contract_rejects_model_approval():
    with pytest.raises(ValidationError):
        Email(
            account_id="A001", to="a@example.org", subject="Follow up", body="Hello", approval=True
        )


def test_versioned_resources():
    cfg, root = load_settings()
    result = metadata(cfg, root)
    assert len(result["prompt_sha256"]) == 64
    assert result["reference_date"] == "2026-05-20"
    assert "api_key" not in str(result)


def test_fixture_events_do_not_postdate_reference():
    import json
    from datetime import date

    cfg, root = load_settings()
    reference = date.fromisoformat(cfg.reference_date)
    for name, field in [("activities", "date"), ("support_tickets", "created_at")]:
        rows = json.loads((root / "data" / f"{name}.json").read_text())
        assert all(date.fromisoformat(row[field]) <= reference for row in rows)
