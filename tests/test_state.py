import pytest

from salesops_agent.agent import run_agent
from salesops_agent.state import StateStore
from salesops_agent.testing import ScriptedModel


def test_owned_memory_persistence_and_replay(tmp_path):
    store = StateStore(tmp_path / "state/history.db")
    store.create_user("alice", "alice-password-123")
    store.create_user("bob", "bob-password-456")
    alice = store.authenticate("alice", "alice-password-123")
    bob = store.authenticate("bob", "bob-password-456")
    sid = store.create_session(alice)
    result = run_agent(
        "Remember CRM account A001",
        output=tmp_path,
        model=ScriptedModel(final="Account A001 is Acme Corp"),
        principal=alice,
        session_id=sid,
    )
    assert result["status"] == "success"
    assert len(store.messages(alice, sid)) == 2
    assert store.sessions(bob) == []
    assert store.replay(alice, result["run_id"])["run_id"] == result["run_id"]
    for action in [lambda: store.messages(bob, sid), lambda: store.replay(bob, result["run_id"])]:
        with pytest.raises(ValueError, match="access_denied"):
            action()

    class CaptureModel(ScriptedModel):
        def invoke(self, messages):
            assert any("Account A001 is Acme Corp" in str(m.content) for m in messages)
            return super().invoke(messages)

    resumed = run_agent(
        "What account did we discuss?",
        output=tmp_path,
        model=CaptureModel(final="A001"),
        principal=alice,
        session_id=sid,
    )
    assert resumed["status"] == "success"
    restored = StateStore(tmp_path / "state/history.db")
    alice = restored.authenticate("alice", "alice-password-123")
    assert len(restored.messages(alice, sid)) == 4


def test_password_required_and_context_denied_before_model(tmp_path):
    store = StateStore(tmp_path / "history.db")
    store.create_user("alice", "alice-password-123")
    with pytest.raises(ValueError, match="authentication_failed"):
        store.authenticate("alice", "bad-password")
    alice = store.authenticate("alice", "alice-password-123")
    sid = store.create_session(alice)
    model = ScriptedModel(final="Never execute")
    result = run_agent("Show pipeline", output=tmp_path, model=model, session_id=sid)
    assert result["status"] == "failed" and model.invocations == 0
