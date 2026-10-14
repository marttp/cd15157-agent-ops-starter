from pydantic import ValidationError
from .schemas import Contract, Email, ToolResult
from .guardrails import tool_arguments_policy, sanitize
from .sandbox import run_sandboxed


class AccountArgs(Contract):
    account: str


class OpenArgs(Contract):
    stage: str | None = None


class EmptyArgs(Contract):
    pass


class DraftArgs(AccountArgs):
    purpose: str


class AnalysisArgs(Contract):
    code: str


class Dispatcher:
    def __init__(self, crm, emails, emit=lambda *args: None):
        self.crm, self.emails, self.emit = crm, emails, emit
        self.contracts = {"lookup_account_context": AccountArgs, "list_open_opportunities": OpenArgs,
                          "summarize_pipeline": EmptyArgs, "draft_email": DraftArgs, "send_email": Email, "analyze_crm": AnalysisArgs}

    def call(self, name, arguments):
        self.emit("tool_attempt", {"name": name, "arguments": arguments})
        if name not in self.contracts:
            return self.block(name, "restricted_internal_data" if "internal" in name else "unknown_tool")
        try:
            args = self.contracts[name].model_validate(arguments)
        except ValidationError:
            return self.block(name, "invalid_tool_arguments")
        decision = tool_arguments_policy(arguments)
        if decision.status == "blocked":
            return self.block(name, decision.reason)
        try:
            if name == "analyze_crm":
                result = run_sandboxed(args.code, sanitize(self.crm.tables))
                if result["status"] == "blocked":
                    return self.block(name, result["reason"])
                self.emit("tool_result", {"name": name, "result": result})
                return result
            if name == "lookup_account_context":
                data = self.crm.context(args.account)
            elif name == "list_open_opportunities":
                data = self.crm.open_opportunities(args.stage)
            elif name == "summarize_pipeline":
                data = self.crm.pipeline()
            elif name == "draft_email":
                data = self.emails.draft(args.account, args.purpose).model_dump()
            else:
                result = self.emails.finalize(args)
                if result["status"] == "blocked":
                    return self.block(name, result["reason"])
                self.emit("tool_result", {"name": name, "result": result})
                return result
            result = ToolResult(status="success", data=sanitize(data)).model_dump()
            self.emit("tool_result", {"name": name, "result": result})
            return result
        except (ValueError, KeyError):
            result = ToolResult(status="failed", reason="crm_lookup_failed").model_dump()
            self.emit("tool_result", {"name": name, "result": result})
            return result

    def block(self, name, reason):
        result = {"status": "blocked", "reason": reason, "policy": "salesops-data-access-v1"}
        self.emit("guardrail", {"layer": "tool", "name": name, **result})
        return result

    def definitions(self):
        descriptions = {"analyze_crm": "Run a bounded expression using count, sum, average, group_sum or filter_eq on approved CRM tables. No arbitrary Python.", "lookup_account_context": "Get CRM evidence for one named account or ID.",
                        "list_open_opportunities": "List open opportunities, optionally filtered by stage.",
                        "summarize_pipeline": "Count and sum opportunity value by stage.",
                        "draft_email": "Draft a follow-up email using the account's CRM contact.",
                        "send_email": "Finalize and fake-send an email, subject to approval."}
        return [{"type": "function", "function": {"name": name, "description": descriptions[name],
                "parameters": contract.model_json_schema()}} for name, contract in self.contracts.items()]
