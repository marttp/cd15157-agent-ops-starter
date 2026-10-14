# Rubric audit

Status: implementation complete for required local features; offline validation verified.
Live model/prototype evidence is pending the author's provider credentials. This is
not a claim that every rubric item is already passed. No external grading outcome
is guaranteed. Verification results and source version are in `reports/evidence/`.

`uv run pytest -q` currently covers 53 checks. `uv run evaluate --offline` covers
32 cases. The default evaluation runs five live SalesOps tasks plus 27 deterministic
fault-injection/control tasks. Expected blocks are evaluation passes, not runtime success.

## Requirement-by-requirement mapping

| Requirement | Implementation | Check/evidence | Status |
| --- | --- | --- | --- |
| Root src/data/logs/traces/reports directories | Tracked source/assets/placeholders | Clean checkout inspection | Verified |
| pyproject.toml, uv.lock, .python-version | Python 3.13+ package and lock | Locked sync and CLI smoke test | Verified locally |
| Separate prompts/tools/schemas/config | prompts/, tools.py, schemas/, config/ | test_contracts.py | Verified |
| At least five authentic milestone commits | Focused PR commits and generated GITLOG.txt | Actual Git history | Verified |
| Documented uv command with question | README Run commands, cli.py | CLI interface tests; live command still needs provider | Implemented, live pending |
| Command prints an agent answer | LangGraph model/tool loop | Five live evaluation tasks | Pending live |
| Invocation produces fresh log/trace | RunContext and error finalization | test_evaluation.py, verify_artifacts.py | Verified offline; live pending |
| README overview/setup/run/eval/report commands | README | Commands run locally where credentials permit | Verified offline |
| Architecture/versioned components/guardrails/limits/hardening | README and plan | Explicit design and residual limits documented | Verified |
| Prototype Review operational gaps | README and preserved notebook | Source inspection; review_prototype.py | Source verified, live execution pending |
| Sandboxed Execution section | README | Limits, supported expressions and residual boundary explained | Verified |
| Human-in-the-Loop Workflow section | README | Actions, approve/reject/pending and simulation explained | Verified |
| Logging and Tracing section | README | Paths, fields, redaction and failure inspection explained | Verified |
| Monitoring Report section | README | Command/output/metrics/denominators explained | Verified |
| Evaluation one-command execution | evaluate entry point | 32/32 offline cases | Verified offline; full live pending |
| Normal SalesOps questions | Safe account case | safe-account graph case and live tool/value assertions | Offline verified, live pending |
| Account risk reasoning | TechStart context, health/reference date prompt | account-risk case includes ID/health assertion | Offline contract verified, live reasoning pending |
| Pipeline/opportunity reasoning | summarize_pipeline/list_open_opportunities | Numeric fixture expectations and cases | Offline verified, live pending |
| Restricted input blocked | input_policy before model | Seven input cases, model invocation count zero | Verified |
| Forbidden call blocked | Dispatcher deny before handler | Denied HR/finance/alternate-action cases | Verified |
| Sensitive output blocked/redacted | output_policy and sanitize | Six output injection cases plus unit matrix | Verified |
| Allowed sandbox analysis | analyze_crm | Grouped stage amounts match fixture-derived totals | Verified |
| Denied sandbox unsafe execution | AST allowlist and worker limits | Six evaluation cases, ten capability unit cases and timeout check | Verified |
| Approved and rejected email cases | ApprovalGate + EmailService | email-approve/reject/None and outbox counts | Verified |
| Per-task status/latency/cost/failure report | evaluation.py | evaluation_report_offline.json/.md | Verified |
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
| CLI exposes approve/reject | argparse approval choices | Documented commands and graph invocation | Verified offline, live CLI pending |
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

## Remaining evidence gate

After credentials are configured, run the isolated prototype utility, execute the
five live tasks and CLI approved/rejected/pending examples, reconcile artifacts,
export sanitized live evidence, and update pending rows based on observed results.
Failures must be fixed and re-evaluated before marking those rows verified. The
provider token must never appear in exports or Git. Offline checks cannot close
these live rows.

## Observed verification snapshot

Clean-clone source commit `b3f96c95f391602ae56d224d09542fb5a7ed01c4` passed locked
installation with uv 0.11.0 and Python 3.13.7, all 53 unit/integration checks, lint and
formatting, all 32 offline evaluation cases, and reconciliation of 32 trace/log pairs.
Selected sanitized artifacts are stored in reports/evidence/. Evidence is from the
committed implementation before the evidence snapshot commit, so its version metadata
remains truthful. Live-provider and container execution status are unchanged.
