import json
import re
from pathlib import Path

FIELDS = {
    "accounts": "account_id name account_status segment industry region account_owner health_score contract_start contract_end arr_usd notes",
    "contacts": "contact_id account_id first_name last_name title email is_primary relationship_status",
    "opportunities": "opportunity_id account_id name type stage amount_usd close_date probability next_step notes",
    "activities": "activity_id account_id date type owner summary sentiment",
    "support_tickets": "ticket_id account_id created_at severity status category summary",
    "product_usage": "usage_id account_id period active_users monthly_logins usage_trend feature_adoption_score",
}


def normalize(text):
    text = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    return " ".join(w for w in text.split() if w not in {"inc", "corp", "ltd", "llc", "corporation"})


class CRM:
    def __init__(self, directory):
        self.tables = {}
        for name, fields in FIELDS.items():
            rows = json.loads((Path(directory) / f"{name}.json").read_text())
            self.tables[name] = [{k: row[k] for k in fields.split() if k in row} for row in rows]
        self.customer_ids = {o["account_id"] for o in self.tables["opportunities"] if o["stage"] == "Closed Won"}
        for account in self.tables["accounts"]:
            account["account_status"] = "customer" if account["account_id"] in self.customer_ids else account["account_status"]

    def resolve(self, query):
        if not query.strip():
            raise ValueError("account_required")
        rows = self.tables["accounts"]
        exact = [a for a in rows if a["account_id"].lower() == query.lower() or normalize(a["name"]) == normalize(query)]
        matches = exact or [a for a in rows if normalize(query) in normalize(a["name"])]
        if len(matches) != 1:
            raise ValueError("account_ambiguous" if matches else "account_not_found")
        return matches[0]

    def context(self, query):
        account = self.resolve(query)
        aid = account["account_id"]
        result = {"account": account}
        for name, rows in self.tables.items():
            if name == "accounts":
                continue
            result[name] = [r for r in rows if r["account_id"] == aid] if name not in {"support_tickets", "product_usage"} or aid in self.customer_ids else []
        return result

    def open_opportunities(self, stage=None):
        return [o for o in self.tables["opportunities"] if o["stage"] not in {"Closed Won", "Closed Lost"} and (not stage or o["stage"].lower() == stage.lower())]

    def pipeline(self):
        result = {}
        for row in self.tables["opportunities"]:
            item = result.setdefault(row["stage"], {"count": 0, "amount_usd": 0})
            item["count"] += 1
            item["amount_usd"] += row["amount_usd"]
        return result
