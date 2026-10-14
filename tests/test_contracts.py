import pytest
from pydantic import ValidationError

from salesops_agent.config import load_settings, metadata
from salesops_agent.schemas import Email


def test_contract_rejects_model_approval():
    with pytest.raises(ValidationError):
        Email(account_id="A001", to="a@example.org", subject="Follow up", body="Hello", approval=True)


def test_versioned_resources():
    cfg, root = load_settings()
    result = metadata(cfg, root)
    assert len(result["prompt_sha256"]) == 64
    assert result["reference_date"] == "2026-03-01"
    assert "api_key" not in str(result)
