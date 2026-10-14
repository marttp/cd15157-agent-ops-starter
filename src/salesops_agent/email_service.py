import hashlib
import json
import sqlite3

from .guardrails import output_policy
from .schemas import Email


class EmailService:
    def __init__(self, path, crm, gate=None):
        self.path, self.crm, self.gate = path, crm, gate
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS outbox (action_id TEXT PRIMARY KEY, message TEXT NOT NULL)")

    def draft(self, account, purpose):
        ctx = self.crm.context(account)
        contacts = ctx["contacts"]
        contact = next((c for c in contacts if c["is_primary"]), contacts[0] if contacts else None)
        if not contact:
            raise ValueError("contact_not_found")
        return Email(account_id=ctx["account"]["account_id"], to=contact["email"],
                     subject=f"Following up on {ctx['account']['name']}",
                     body=f"Hi {contact['first_name']},\n\nI wanted to follow up regarding {purpose}.\n\nBest,\nUdaCenture SalesOps")

    def validate_recipient(self, email):
        if email.to not in {c["email"] for c in self.crm.context(email.account_id)["contacts"]}:
            raise ValueError("recipient_out_of_scope")

    @staticmethod
    def action_id(email):
        return hashlib.sha256(json.dumps(email.model_dump(), sort_keys=True).encode()).hexdigest()

    def finalize(self, email):
        self.validate_recipient(email)
        policy = output_policy(email.model_dump())
        if policy.status == "blocked":
            return {"status": "blocked", "reason": policy.reason}
        if self.gate is None:
            return {"status": "blocked", "reason": "approval_required"}
        if self.gate.decide(email) != "approve":
            return {"status": "rejected", "reason": "human_rejected"}
        action_id = self.action_id(email)
        with sqlite3.connect(self.path) as db:
            cursor = db.execute("INSERT OR IGNORE INTO outbox VALUES (?, ?)",
                                (action_id, json.dumps(email.model_dump())))
            duplicate = cursor.rowcount == 0
        return {"status": "sent", "reason": "already_sent" if duplicate else "approved",
                "action_id": action_id, "duplicate": duplicate}

    def messages(self):
        with sqlite3.connect(self.path) as db:
            return [json.loads(row[0]) for row in db.execute("SELECT message FROM outbox ORDER BY rowid")]
