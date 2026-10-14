# AgentOps final project implementation plan

Status: required local implementation and optional authenticated SQLite memory are implemented through focused PRs. Offline and live verification pass; all required rubric rows have observed evidence. See docs/rubric-audit.md for current status.

Fork: https://github.com/marttp/cd15157-agent-ops-starter

Upstream: https://github.com/udacity/cd15157-agent-ops-starter

Baseline inspected: `640790c2d2de6187a34f69154d2060916918a2fc`.

## Scope and completion rule

Operationalize the supplied SalesOps prototype as a Python 3.13+ local application using uv, LangChain and LangGraph. Follow the supplied instructions and screenshot rubric. Preserve the original notebook and datasets as reference artifacts. The final application will live at repository root, with its own `data/`, so reviewers can run every documented command there.

Every required rubric statement must map to implementation, an executable verification, and an observed artifact. A planned test or a passing mocked model test does not prove live agent behavior. Completion requires a clean installation, deterministic control tests, live model evaluation, generated evidence, and an audit with no required item pending. An external grader's decision cannot be guaranteed.

Prioritize the required local lifecycle. Add GitHub Actions and a Dockerfile after the required checks pass. SQLite persistence and multi-user memory isolation are a separate optional phase. A frontend, MCP service and external observability backend are outside the initial scope.

## Findings from the actual starter

`starter/project_starter.ipynb` contains the prototype, not a completed operational application. Its stored cells have no execution outputs. The supplied narrative mentions skeleton infrastructure, but this checkout contains the notebook, data, READMEs and licence rather than logging/state/reporting skeleton modules.

- Cell 20 embeds the prompt and permits internal tools.
- Cells 15 and 16 load restricted HR and financial data into the same process as CRM data.
- Cells 36 and 37 return entire internal datasets regardless of query.
- Cell 33 returns full CRM records, including unstructured notes, without field projection or redaction.
- Cell 24 uses `difflib` without an import. Its first partial/fuzzy match can select the wrong account when a query is ambiguous.
- Cell 39 writes to a JSON outbox without approval, schema checks, idempotency or concurrent-write protection.
- Cell 42 hardcodes the model; dependencies, configuration and prompts are not pinned together.
- There is no runtime input/tool/output policy, constrained analysis, evaluation, structured run record, trace, monitoring report or CLI.

Observed data includes 109 accounts, 280 contacts, 182 opportunities, 188 activities, 33 support tickets and 27 usage records. The supplied outbox already contains one message, so approval tests must compare before/after state rather than assume an empty outbox.

Prototype execution remains a phase-one task. Run in an isolated copy, with a temporary outbox and sanitized evidence. Record provider/dependency errors honestly. Do not claim the notebook ran based on this source inspection.

## Course reference map

References are relative to the sibling `../cd15157-agent-ops-exercises/` checkout. Record its commit when implementation begins. These are learning patterns to adapt, not files to copy wholesale.

| Project concern | Course reference | Application to SalesOps |
| --- | --- | --- |
| Reproducibility and versioning | `module-01-reproducibility/starter/INSTRUCTIONS.md` | uv project, external prompt, meaningful Git milestones. Project requires Python 3.13+, overriding the exercise's 3.12 example. |
| Evaluation and regression gate | `module-02-evals/starter/INSTRUCTIONS.md` | Golden expectations, baseline/candidate comparison and per-scenario regressions. Do not import the unrelated property-domain thresholds or 10pp target as a project requirement. |
| Deployment structure and CLI | `module-03-deploy/starter/INSTRUCTIONS.md` and `solution/realthor/src/realthor/config.py` | `src/` package, entry points, config-relative paths and provider adapter. |
| Runtime guardrails | `module-04-guardrails/starter/INSTRUCTIONS.md` and `solution/realthor/src/realthor/guardrails.py` | Input, tool-call and output middleware; explicit blocked results. Replace property rules with SalesOps rules. |
| Constrained analysis | `module-05-sandbox/starter/INSTRUCTIONS.md` and `solution/realthor/src/realthor/sandbox.py` | Separate validator and runner, controlled CRM input and structured output. Strengthen the execution boundary described below. |
| Human approval | `module-06-HITL/starter/INSTRUCTIONS.md`, `solution/realthor/src/realthor/policies.py`, `guardrails.py`, `app.py` | Policy-triggered interrupt, approve/reject resume, checkpointer and CLI approval option. |
| Monitoring | `module-07-monitoring/starter/INSTRUCTIONS.md` | Typed run records, aggregation, metric definitions, failure reasons and generated reports. |
| Debugging | `module-08-debugging/starter/INSTRUCTIONS.md` | Reconstruct run inputs, versions and tool trajectory. Durable graph state is optional. |
| Tracing | `module-09-tracing/starter/INSTRUCTIONS.md` | Model/tool spans, token usage and correlation. Required local JSON traces replace the optional Langfuse backend. |
| Optional identity isolation | `module-10-context/starter/INSTRUCTIONS.md` | Owned sessions, user/session state keys and cross-user denial tests. CLI identity alone is not authentication. |

## Backend design

Keep one primary agent. Its proposed tool calls cross an application-owned dispatcher that validates the schema, data scope, policy and approval before calling a handler. The model cannot supply its own approval or expand its access rights.

Execution path:

```text
CLI -> run context -> input policy -> LangGraph agent
    -> validated tool dispatcher -> projected CRM / constrained analysis / email service
    -> output policy -> terminal

Every boundary -> sanitized events -> JSONL run summary + per-run JSON trace
Run summaries -> monitoring report
Evaluation cases -> same run path -> evaluation report
```

Suggested root layout:

```text
src/salesops_agent/
  cli.py, agent.py, config.py, schemas.py, run_context.py
  data_access.py, tools.py, policies.py, guardrails.py
  sandbox.py, approvals.py, email_service.py
  logging.py, tracing.py, evaluation.py, monitoring.py
prompts/system_v2.md
config/agent_v2.yaml
schemas/                         # versioned public JSON contracts
evaluation/scenarios.json        # expectations and assertion types
tests/                          # behavior and boundary tests
data/                           # supplied fixtures, application projects approved fields
logs/, traces/, reports/         # tracked placeholders, ignored raw runtime output
docs/implementation-plan.md, docs/rubric-audit.md
starter/                        # preserved notebook and original data
pyproject.toml, uv.lock, .python-version, .env.example, .gitignore
README.md, GITLOG.txt
```

Decisions to implement:

1. Use Pydantic contracts for configuration, tool arguments, results, guardrail decisions, run summaries and trace events. Unknown tools, unexpected arguments and unknown fields fail closed.
2. Load only an explicit CRM file/field allowlist. Internal HR and finance fixtures remain reference data and never enter normal model context or analysis input. Treat notes and tool results as untrusted data. Resolve ambiguous account names explicitly. Preserve the definition that customers have a Closed Won opportunity.
3. Use a pinned dataset reference date for renewal/risk evaluation. Record it in config and traces so the same fixture does not change meaning as the calendar advances.
4. Configure the provider using the course's Vocareum/OpenAI adapter pattern. Keep keys in environment variables; record provider/model and sanitized effective config. Pin dependencies with uv. Record Git commit, prompt/config/schema/tool versions and dataset hashes on every run. Temperature zero reduces variability; it does not guarantee identical model output.
5. Enforce request scope and sensitive-topic rules before invoking the model. Deny internal tool names through the dispatcher even when tests deliberately propose them. Apply output checks to final responses and email content before approval or any write. Input matching alone cannot establish safety.
6. Implement an allowlisted analysis expression language with AST validation and interpretation. Permit bounded filtering, grouping, counts, sums and averages on projected CRM data. Reject arbitrary Python, imports, file access, network access, reflection, eval and exec. Bound source length, node count, rows, operations and output size. Run in a worker that can be terminated on timeout. The worker receives serialized CRM values, not pandas or host-capable objects. Document that this is constrained analysis, not a general Python sandbox or an OS security boundary.
7. Drafting is reversible. Finalizing/fake-sending requires an application-owned decision bound to the exact recipient, subject and body. Missing decision pauses. Reject performs no outbox write. Approve cannot override unsafe output or data policies. All email tool aliases use the same guarded service. Validate recipient against the resolved CRM contact and deduplicate repeated execution using an action identifier and transactional local storage.
8. Record attempted and completed tool calls separately. Persist sanitized events as they occur and finalize telemetry on success, block, rejection, pending approval, timeout and handled error. Redact input, arguments, output and errors before writing either logs or traces. Trace observable execution and evidence, not hidden model chain-of-thought.
9. Derive estimated costs from actual token usage and versioned provider/model price assumptions. Missing usage is unknown, not zero. Offline test calls have explicitly marked simulated usage. Never combine mock costs with live costs without labeling them.
10. Define runtime statuses separately from evaluation pass/fail. A correctly blocked unsafe request is an evaluation pass but remains a blocked runtime outcome. Reports show each status and the denominator for each rate. Tool counts distinguish attempts, executions and blocks; repeated HITL resume does not double-count a run.

## Implementation tasks and commit milestones

These are tasks for the agent to execute, not a checklist delegated to the author. Each milestone gets a real focused commit and verification result. Nine milestones cover the stricter written instructions, even though the screenshot asks for at least five commits.

| Order | Task and intended commit | Completion evidence |
| --- | --- | --- |
| 1 | Inspect/run prototype safely; `AgentOps: scaffold reproducible Python project and preserve starter reference artifacts` | Prototype Review draft, Python 3.13+, locked uv environment, required directories, package imports and clean setup. |
| 2 | Extract prompt/config/contracts; `AgentOps: extract versioned prompts configuration and schemas with validated runtime metadata` | External files loaded by CLI; invalid config fails; version/hash metadata captured. |
| 3 | Refactor approved CRM and email tools; `AgentOps: refactor scoped CRM tools and transactional email service behind validated dispatcher` | Data/field projection, ambiguous lookup, customer semantics, no raw internal access, transactional outbox behavior. |
| 4 | Build evaluation runner early; `AgentOps: add golden evaluation scenarios regression checks and per-task cost reports` | One command, exact numeric CRM expectations, failure exit code, baseline report. Future safety scenarios remain explicit failures until implemented. |
| 5 | Enforce runtime guardrails; `AgentOps: enforce input tool and output policies with explicit sanitized blocked outcomes` | Direct boundary tests and malicious model/tool-result fixtures prove every policy layer executes. |
| 6 | Add constrained analysis; `AgentOps: add bounded CRM analysis interpreter with capability restrictions and execution limits` | Correct pipeline aggregation; eval/exec, imports, file/network access, restricted datasets and over-budget execution rejected. |
| 7 | Add approval lifecycle; `AgentOps: require content-bound approval for every customer-facing email finalization and send` | No-decision pause, approve, reject, alternate-path bypass and duplicate-resume tests; trace decision and unchanged outbox on rejection. |
| 8 | Finish telemetry/reports; `AgentOps: capture redacted run events local traces and consolidated operational monitoring metrics` | Fresh log and trace for all outcomes, report totals match source records, failure reconstruction and redaction checks. |
| 9 | Audit/document/package; `AgentOps: document operational design production limits and verified rubric evidence for submission` | Clean-clone validation, live evaluation, monitoring artifacts, README sections, licence attribution and complete rubric audit. |

Introduce minimal telemetry with the run context early so control/evaluation work can emit evidence. Milestone 8 completes its coverage and aggregation. Do not postpone instrumentation until the end.

Generate `GITLOG.txt` from actual history after the implementation milestones. Commit that generated snapshot in a final evidence commit and explain its generation point. Never invent history or split empty changes to inflate the count.

## Evaluation coverage

Use a single `uv run evaluate` command for the submission suite. It runs deterministic boundary/control cases plus live agent tasks and produces `reports/evaluation_report.json` and `.md`. Missing credentials make live cases explicitly unavailable and the full verification fail; no silent success or model substitution. `uv run pytest` supports offline engineering checks separately.

Each case records its ID, kind, expected behavior, observed behavior, run ID, pass/fail, latency, token usage, estimated cost or unknown value, and failure reason. Assertions inspect structured outputs, actual numeric results, observed tool events and side effects. A refusal string alone is insufficient evidence of enforcement.

Minimum planned coverage exceeds five tasks because the rubric names more than five behaviors:

| Cases | Expected evidence |
| --- | --- |
| Safe account lookup, TechStart risk, GlobalRetail renewal, open opportunities, pipeline totals | Live agent uses the intended CRM tools; answers agree with independent fixture-derived expectations and contain no unsupported commitments. |
| CEO bonus, HR performance/termination, M&A, layoffs, confidential finance and prompt injection | Input guardrail blocks before any model invocation; reason/policy and run artifacts exist. |
| Proposed HR/finance tools, unknown tool, unauthorized field and unrelated CRM scope | Dispatcher blocks before handler execution, regardless of the model's behavior. |
| Injected sensitive model output and sensitive tool/CRM content | Output blocked/redacted; prohibited raw values absent from terminal, logs and traces. Include executive pay, performance, termination, M&A, layoffs and strategy. |
| Invented email discount/legal commitment | Unsafe email cannot proceed even with approve selected. |
| Pipeline grouping, count and average deal size | Analysis results match independent expected values on approved data. |
| eval/exec, imports, host file read, network, restricted dataset, reflective escape and budget/timeout | Capability rejected or worker terminated; no restricted output or side effect. |
| Email without decision, approved email, rejected email | Pending action visible; approve writes exactly once; reject leaves outbox unchanged; log and trace record requested approval and decision. |
| Alternate email path, model-forged approval and repeat execution | Same service refuses bypass; approval binds to exact content; no duplicate message. |
| Provider timeout, tool exception and invalid model output | Explicit failed run with sanitized failure reason, latency, cost availability and debuggable trace. |
| Prompt/config candidate comparison | Per-task regressions identified; no required safety regression accepted. Live uncertainty reported separately from deterministic policy behavior. |

Use isolated temporary output directories for tests. Keep selected sanitized observed evidence under `reports/evidence/`; do not publish runtime secrets or unreviewed raw logs. Reports identify the code/data/config versions they actually evaluated.

## Rubric evidence matrix

The detailed audit tracks current verification status. It expands these groups into individual rubric statements with file references, commands and observed artifacts.

| Required criterion | Implementation and verification contract |
| --- | --- |
| Reproducible project | Root `src/`, `data/`, `logs/`, `traces/`, `reports/`; `pyproject.toml`, `uv.lock`, `.python-version`; external prompts/tools/schemas/config. Clean clone + `uv sync --locked` + documented commands. |
| Authentic version history | Real milestones cover scaffolding, prompt/config extraction, tools, eval, guardrails, sandbox, HITL and telemetry; generated root `GITLOG.txt` shows at least five relevant commits. |
| Local agent entry point | `uv run salesops-agent ask "Summarize the current sales pipeline by stage."` prints an answer and creates a fresh JSONL entry plus `traces/<run_id>.json`. |
| README architecture and hardening | Overview, setup, run/eval/report commands, architecture, versioned components, guardrail design, limitations and production recommendations. Exact required sections: `## Prototype Review`, `## Sandboxed Execution`, `## Human-in-the-Loop Workflow`, `## Logging and Tracing`, `## Monitoring Report`. |
| Automated evaluation | One command; normal questions, risk, opportunity reasoning, input/tool/output blocks, allowed/denied sandbox and approved/rejected email; per-task result, latency, estimated cost and failure reason in required report paths. |
| Input/tool/output guardrails | Code enforcement before model/action and before final output; required sensitive categories; explicit status/reason/policy; logged interventions; direct injection tests prove enforcement rather than prompt compliance. |
| Sandboxed execution | Real CRM analysis tool; no unrestricted eval/exec, host/network/internal data access; execution limits; permitted and denied evidence; documented residual limits. |
| HITL | Pause before high-risk side effect; CLI `--approval approve` and `--approval reject`; absent approval pending; approve completes safe fake-send; reject prevents it; requested approval and decision in log/trace; alternate tool paths cannot bypass gate. |
| Structured logs | Each invocation includes run ID, timestamp, sanitized input, optional task ID, final status, attempted/executed tools, latency, estimated cost availability, guardrail interventions, HITL decision and failure reason. |
| Per-run trace | `traces/<run_id>.json` records sanitized input, selected tools, arguments/results, guardrail decisions, approval request/decision, final output and errors; sensitive HR/finance values absent. |
| Consolidated monitoring | `uv run generate-monitoring-report` creates `reports/monitoring_report.md` and `.json`. Aggregate total runs, success/failure rates, mean latency, total/mean estimated cost, tool counts, guardrail blocks, approvals/rejections and common failure reasons. Explain unknown costs and status denominators. |

## Verification and release gates

1. Deterministic gate: tests prove policies, dispatcher, sandbox, approval, redaction and reporting using the same production components. A timeout test checks the worker actually stops; a reject test checks the actual write path remains untouched.
2. Live gate: configured provider runs representative SalesOps tasks through the CLI and full evaluation suite. Collect real usage, latency, selected tools and sanitized traces. Repeat affected live cases when prompt/config changes introduce uncertainty.
3. Report gate: independently reconcile monitoring aggregates with JSONL records. Validate report and trace schemas. Scan every exported artifact for sensitive fixture values and secrets without printing them.
4. Reproducibility gate: clean clone, locked sync, documented CLI/evaluation/report commands, correct paths, version metadata and generated history. Package resources must be included if a wheel/container is produced.
5. Submission gate: one audit row per screenshot/written requirement, each marked verified with evidence. No pending required criterion; known production limitations remain explicit. Publish selected evidence and implementation only after review for secrets and unrelated files.

Implemented command contracts:

```sh
uv sync --locked
uv run salesops-agent ask "Summarize the account risk for TechStart Inc."
uv run salesops-agent ask "Draft and send a follow-up email to Acme Corp" --approval approve
uv run salesops-agent ask "Draft and send a follow-up email to Acme Corp" --approval reject
uv run pytest
uv run evaluate
uv run generate-monitoring-report
```

## Optional phase and production limits

After the mandatory audit passes, add a GitHub Actions offline gate and Dockerfile packaging. Live CI evaluation needs separately configured secrets and an explicit cost budget.

SQLite state, replay and multi-user memory isolation would follow module 8 and module 10. Require authenticated identity or clearly label identity as simulated; persist owned sessions and user-scoped thread keys. Demonstrate same-user resume, another-user denial and no memory leakage. Do not claim a CLI user flag provides production authentication.

The required system remains a local production candidate with fake email delivery. Production hardening includes verified authentication/authorization, managed secrets, stronger isolation for arbitrary code, least-privilege data services, retention/access controls for logs and traces, durable approval/checkpoint storage, transactional delivery, rate limits, bounded retries, external telemetry, CI/CD gates and wider adversarial evaluation.
