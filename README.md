# UdaCenture SalesOps Agent

AgentOps final project. Implementation progresses through focused PRs. See
[the implementation plan](docs/implementation-plan.md) for the course mapping,
backend design, acceptance checks and rubric coverage.

## Setup

Requires Python 3.13+ and uv. Run `uv sync --locked`, then `uv run salesops-agent --version`.
Provider credentials belong in the ignored `.env` file. `.env.example` contains field names only.

## Prototype Review

Source inspection of `starter/project_starter.ipynb` found an inline prompt/model,
unpinned dependencies, raw internal HR/finance access, unprojected CRM fields,
email writes without approval, and no evaluation, sandbox, logs, traces or reports.
The fuzzy lookup references `difflib` without importing it and first-match lookup
can return the wrong account. The source notebook is preserved unchanged.
Its original stored cells contain no outputs. Live execution evidence is pending
provider configuration and will run against temporary data/outbox copies.

## Course references

Learning checkout `cd15157-agent-ops-exercises`, commit
`2cf93ab0771c21148e05b4412e18b0dd25c3cad7`. Module 1 supplies the uv/versioning
pattern; later PRs adapt modules 2–10. Python 3.13 follows this project's requirements.

## Validation

`uv run pytest` checks the current milestone. This scaffold does not yet claim
agent behavior or rubric completion.

Original starter and course materials retain the [Udacity licence](LICENSE.txt).
