from langgraph.types import interrupt

from .email_service import EmailService


class ApprovalGate:
    def __init__(self, ctx):
        self.ctx, self.decisions, self.requested = ctx, {}, set()

    def decide(self, email):
        action_id = EmailService.action_id(email)
        if action_id in self.decisions:
            return self.decisions[action_id]
        pending = {"action_id": action_id, "email": email.model_dump(), "requires_approval": True}
        if action_id not in self.requested:
            self.ctx.emit("approval_requested", pending)
            self.requested.add(action_id)
        response = interrupt(pending)
        decision = (
            response.get("decision")
            if isinstance(response, dict) and response.get("action_id") == action_id
            else "reject"
        )
        if decision not in {"approve", "reject"}:
            decision = "reject"
        self.decisions[action_id] = decision
        self.ctx.hitl_decision = decision
        self.ctx.emit("approval_decision", {"action_id": action_id, "decision": decision})
        return decision
