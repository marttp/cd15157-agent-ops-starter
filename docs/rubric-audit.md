# Rubric audit

Status: all required local rubric rows have observed verification evidence. Live
Vocareum evaluation, prototype execution and CLI approval checks passed. This is a
local production candidate; an external grading decision and future model behavior
are not guaranteed. Evidence and source versions are in `reports/evidence/`.

`uv run pytest -q` currently covers 54 checks. `uv run evaluate --offline` covers
32 cases. The default evaluation runs five live SalesOps tasks plus 27 deterministic
fault-injection/control tasks. Expected blocks are evaluation passes, not runtime success.

## Requirement-by-requirement mapping

| Requirement | Implementation | Check/evidence | Status |
| --- | --- | --- | --- |
| Root src/data/logs/traces/reports directories | Tracked source/assets/placeholders | Clean checkout inspection | Verified |
| pyproject.toml, uv.lock, .python-version | Python 3.13+ package and lock | Locked sync and CLI smoke test | Verified locally |
| Separate prompts/tools/schemas/config | prompts/, tools.py, schemas/, config/ | test_contracts.py | Verified |
| At least five authentic milestone commits | Focused PR commits and generated GITLOG.txt | Actual Git history | Verified |
| Documented uv command with question | README Run commands, cli.py | CLI interface plus observed live answers | Verified live |
| Command prints an agent answer | LangGraph model/tool loop | Five live evaluation tasks | Verified live |
| Invocation produces fresh log/trace | RunContext and error finalization | test_evaluation.py, verify_artifacts.py | Verified offline and live |
| README overview/setup/run/eval/report commands | README | Commands run locally where credentials permit | Verified offline |
| Architecture/versioned components/guardrails/limits/hardening | README and plan | Explicit design and residual limits documented | Verified |
| Prototype Review operational gaps | README and preserved notebook | Source inspection; review_prototype.py | Verified; 43 code cells executed without errors |
| Sandboxed Execution section | README | Limits, supported expressions and residual boundary explained | Verified |
| Human-in-the-Loop Workflow section | README | Actions, approve/reject/pending and simulation explained | Verified |
| Logging and Tracing section | README | Paths, fields, redaction and failure inspection explained | Verified |
| Monitoring Report section | README | Command/output/metrics/denominators explained | Verified |
| Evaluation one-command execution | evaluate entry point | 32/32 offline cases | Verified; 32/32 full evaluation cases |
| Normal SalesOps questions | Safe account case | safe-account graph case and live tool/value assertions | Verified offline and live |
| Account risk reasoning | TechStart context, health/reference date prompt | account-risk case includes ID/health assertion | Verified; reviewed live risk facts and renewal timing |
| Pipeline/opportunity reasoning | summarize_pipeline/list_open_opportunities | Numeric fixture expectations and cases | Verified offline and live |
| Restricted input blocked | input_policy before model | Seven input cases, model invocation count zero | Verified |
| Forbidden call blocked | Dispatcher deny before handler | Denied HR/finance/alternate-action cases | Verified |
| Sensitive output blocked/redacted | output_policy and sanitize | Six output injection cases plus unit matrix | Verified |
| Allowed sandbox analysis | analyze_crm | Grouped stage amounts match fixture-derived totals | Verified |
| Denied sandbox unsafe execution | AST allowlist and worker limits | Six evaluation cases, ten capability unit cases and timeout check | Verified |
| Approved and rejected email cases | ApprovalGate + EmailService | email-approve/reject/None and outbox counts | Verified |
| Per-task status/latency/cost/failure report | evaluation.py | evaluation_report_live.json/.md and offline baseline | Verified |
| Input policy covers executive pay | normalized pattern | CEO bonus and equity bonus tests | Verified |
| Input policy covers M&A/layoffs/termination/injection | normalized patterns | Input cases plus unit matrix | Verified |
| Tool/action policy blocks HR/finance before execution | No internal handlers, strict contracts | Forbidden call with no tools_called | Verified |
| Tool/action policy prevents unapproved email | Explicit intent + service approval | Default denial, forged approval, alternate path tests | Verified |
| Output policy covers pay/performance/M&A/layoffs | recursive policy | Generated-output injection matrix | Verified |
| Blocked status has reason and appears in log | Decision/dispatcher/result schemas | Recorded guardrail interventions and failure reason | Verified |
| Controls reside in application code | guardrails.py/tools.py/email_service.py | Direct injected boundary tests | Verified |
| Analysis tool uses approved CRM | projected serialized tables | Correct count/grouping and restricted dataset denial | Verified |
| No unrestricted eval/exec against host | AST interpreter, no arbitrary Python | eval/exec/attribute/file/network denial cases | Verified |
| Runtime constraint enforced | Row/source/node/operation/output/time limits | Size and real worker termination tests | Verified |
| No internal HR/finance read through sandbox | Dataset/field allowlist | Internal dataset and salary field denials | Verified |
| Workflow pauses before email write | LangGraph interrupt | Missing-decision test, outbox unchanged | Verified |
| Approve completes action, reject prevents action | Content-bound decision + transaction | Graph resume tests and outbox counts | Verified |
| CLI exposes approve/reject | argparse approval choices | Documented commands and graph invocation | Verified live; outbox counts 0/1/0 |
| Decision in log and trace | approval_requested/approval_decision/run summary | Equality assertions in approval tests | Verified |
| Alternate path cannot bypass gate | Single write service, unknown tool denial | finalize_email and forged decision tests | Verified |
| Structured JSONL run fields | RunRecord | Pydantic validation and artifact verifier | Verified |
| Per-run trace trajectory fields | TraceEvent + root trace envelope | Tool arguments/results, model usage, decisions, final/error events | Verified |
| Sensitive raw HR/finance trace values redacted | Pre-write recursive sanitizer; no raw internal tools | Output/secret/field checks and evidence validation | Verified for tested policies |
| Monitoring command and report path | generate-monitoring-report | .md/.json generated from observed runs | Verified |
| Aggregate total/success/failure/latency/cost/tools | aggregate() | test_monitoring.py plus source-record reconciliation | Verified |
| Aggregate guardrails/HITL/common failures | aggregate() | Counters reconciled by verify_artifacts.py | Verified |
| Metrics rather than raw log dump | Consolidated counters/rates/means | monitoring_report_offline.json/.md | Verified |

## Optional features

SQLite persists sanitized successful runs, owned sessions and replay. Local salted
scrypt authentication and ownership checks demonstrate multi-user memory isolation.
Tests verify another user's session list is empty, direct session/run reads fail,
and the owner resumes memory after reopening SQLite. Full durable LangGraph graph
checkpoints and cross-process pending-approval resume are not claimed.

GitHub Actions is included as an offline gate. Hosted CI passed on the packaging source commit.
See reports/evidence/validation-summary.json for run links and exact source version. Dockerfile packaging is included. The local Docker daemon is not
running, so container build/run has not been verified. Neither Docker execution nor
external observability is a required rubric item.

## Completed live evidence gate

The real course provider passed all five SalesOps questions and the full 32-case
evaluation. Comparison against the first live baseline found no task regressions.
Live CLI commands verified pending approval with zero writes, approval with one
write and rejection with zero writes. A live model-selected analysis call returned
182 opportunities; restricted input blocked before any model invocation. The
monitoring report reconciles all 37 evaluation/CLI run summaries and trace files.

Reviewing the initial live answer exposed inconsistent temporal context: fixtures
include activity through May 19 but the old reference date was March 1. The versioned
v2 configuration uses May 20; a data-consistency test checks observed events do not
postdate it. The v1 files remain unchanged. A new live evaluation passed after this
correction, and the risk answer correctly describes the May 28 renewal as imminent.

The original notebook completed 43 code cells without errors in an isolated data
copy. Only the temporary provider adapter differs; raw notebook outputs are not
exported. Credentials remain outside Git and evidence.

## Observed verification snapshot

Clean-clone source commit `b3f96c95f391602ae56d224d09542fb5a7ed01c4` passed locked
installation with uv 0.11.0 and Python 3.13.7, all 53 unit/integration checks, lint and
formatting, all 32 offline evaluation cases, and reconciliation of 32 trace/log pairs.
Selected sanitized artifacts are stored in reports/evidence/. Evidence is from the
committed implementation before the evidence snapshot commit, so its version metadata
remains truthful. This is the initial offline baseline. Current live verification uses source
`84685b7a4da15cfd286445540c6379eeeb27dbd1`, configuration v2 and reference date May 20.
All 32 evaluation cases and five additional live CLI checks pass; 37 artifact pairs
reconcile. See validation-summary-live.json and evaluation_report_live.json. Container
execution remains unverified because no local Docker daemon is running.

The current v2 source also passed a fresh clone with uv 0.11.0: locked setup,
54 engineering checks, lint/formatting, all 32 offline cases and all 32 corresponding
artifact pairs. Those current offline artifacts use the `_offline_v2` suffix; the
original `_offline` files remain a historical baseline.
