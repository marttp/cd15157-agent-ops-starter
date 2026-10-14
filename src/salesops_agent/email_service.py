import hashlib
import json
import sqlite3
from .schemas import Email


class EmailService:
    def __init__(self, path, crm):
        self.path, self.crm = path, crm
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

    def finalize(self, email, authorization=None):
        # No public tool can write before the approval lifecycle exists.
        self.validate_recipient(email)
        return {"status": "blocked", "reason": "approval_required"}

    def messages(self):
        with sqlite3.connect(self.path) as db:
            return [json.loads(row[0]) for row in db.execute("SELECT message FROM outbox ORDER BY rowid")]
