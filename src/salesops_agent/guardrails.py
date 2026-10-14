import re
import unicodedata

from .run_context import basic_sanitize
from .schemas import Decision

PATTERNS = {
    "credential_exposure": r"(?:voc-|sk-)[A-Za-z0-9._-]{8,}",
    "executive_compensation": r"\b(?:ceo|cfo|executive)\b.{0,50}\b(?:bonus|pay|salary|compensation|equity)\b|salary_usd|equity_bonus|\bequity bonus\b|\bsalary\b|\bcompensation\b",
    "restricted_hr": r"internal.hr|\bhr data\b|\b(?:employee|staff)\b.{0,40}\b(?:performance|termination|fired|dismiss|pip)\b|\bperformance plan\b|\btermination\b|\bgetting fired\b",
    "confidential_ma": r"\bm\s*&\s*a\b|confidential_m_and_a|\bacquir(?:ing|e)\b|\bmerger\b|\bacquisition details\b",
    "confidential_layoffs": r"lay.?offs?|layoff_plan|planned_reduction",
    "confidential_strategy": r"internal.financial|confidential.{0,30}(?:strategy|financial|finance|discount)|restricted.{0,30}(?:strategy|financial)|\bfinancial strategy\b|runway_months",
    "prompt_injection": r"ignore.{0,30}(?:instructions|polic|rules)|reveal.{0,30}(?:hidden|system|instructions)|system prompt|developer message|override.{0,20}polic|you are now|forget.{0,20}instructions",
    "unsafe_commitment": r"(?:offer|give|apply|invent|approve).{0,30}discount|\d+\s*%\s*discount|\bguarantee\b|legal commitment|binding agreement|we will indemnify",
}
SENSITIVE_KEYS = {
    "salary_usd",
    "equity_bonus_usd",
    "internal_hr_data",
    "internal_financial_data",
    "confidential_strategy",
    "confidential_m_and_a",
    "confidential_layoff_plan",
    "confidential_discount_policy",
    "performance_plan",
    "termination",
    "api_key",
    "password",
    "secret",
}


def canonical(text):
    return "".join(
        c for c in unicodedata.normalize("NFKC", text).casefold() if unicodedata.category(c) != "Cf"
    )


def inspect_text(text):
    normalized = canonical(text)
    for reason, expression in PATTERNS.items():
        if re.search(expression, normalized):
            return Decision(status="blocked", reason=reason)
    return Decision(status="allowed", reason="salesops_allowed")


def input_policy(text):
    if len(text) > 12000:
        return Decision(status="blocked", reason="input_size_limit")
    return inspect_text(text)


def output_policy(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if canonical(key) in SENSITIVE_KEYS:
                return Decision(status="blocked", reason="sensitive_field")
            decision = output_policy(child)
            if decision.status == "blocked":
                return decision
    elif isinstance(value, list):
        for child in value:
            decision = output_policy(child)
            if decision.status == "blocked":
                return decision
    elif isinstance(value, str):
        return inspect_text(value)
    return Decision(status="allowed", reason="salesops_allowed")


def sanitize(value):
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if canonical(k) in SENSITIVE_KEYS else sanitize(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        if value in {"lookup_internal_hr_data", "lookup_internal_financial_data"}:
            return value
        value = basic_sanitize(value)
        if inspect_text(value).status == "blocked":
            return "[REDACTED: restricted content]"
        return value
    return value


def tool_arguments_policy(arguments):
    # Schema rejects extra fields; this catches restricted content in allowed fields.
    return output_policy(arguments)
