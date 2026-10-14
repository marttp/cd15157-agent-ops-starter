# Implementation PR history

Every PR uses What / Why / Change with a 100–200 word description. Implementation
branches use `codex/agentops-*` in a dedicated worktree. PRs 1–9 are merged; packaging
and submission documentation are the next PR. Course patterns are mapped in the plan.

| PR | Scope | Verification before merge |
| --- | --- | --- |
| [1](https://github.com/marttp/cd15157-agent-ops-starter/pull/1) | Reproducible uv project | CLI and root structure smoke check |
| [2](https://github.com/marttp/cd15157-agent-ops-starter/pull/2) | Prompts, config, schemas, provider adapter | Strict schema rejection and resource hashes |
| [3](https://github.com/marttp/cd15157-agent-ops-starter/pull/3) | Approved CRM and dispatcher | Dataset totals, ambiguity, unknown arguments and blocked writes |
| [4](https://github.com/marttp/cd15157-agent-ops-starter/pull/4) | LangGraph CLI and evaluation | Five offline graph evaluations, provider error trace |
| [5](https://github.com/marttp/cd15157-agent-ops-starter/pull/5) | Runtime guardrails | Input before model, forbidden call and sensitive output injection |
| [6](https://github.com/marttp/cd15157-agent-ops-starter/pull/6) | Bounded analysis worker | 41 checks including corrected startup deadline and terminated worker |
| [7](https://github.com/marttp/cd15157-agent-ops-starter/pull/7) | Content-bound HITL | Approve/reject/pause, duplicate write and bypass denial |
| [8](https://github.com/marttp/cd15157-agent-ops-starter/pull/8) | Monitoring and expanded evaluation | 48 checks, 32 offline scenarios, metric reconciliation |
| [9](https://github.com/marttp/cd15157-agent-ops-starter/pull/9) | Owned SQLite memory/replay | Password check, same-user resume, cross-user denial |

PR 6 remained unmerged until its timeout test passed. GitHub briefly rejected merging
an updated PR head; the final head was verified and merged before proceeding. Source
and remote status are checked separately. Original course repository changes are
outside this worktree and are not included in the project PRs.
