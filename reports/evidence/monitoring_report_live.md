# Monitoring report

Rates use all recorded runs as denominator. Failed means runtime error; blocked, rejected and pending approval are separate outcomes. A correct block can pass evaluation.

Costs use observed token usage and illustrative versioned rates. Unknown-cost runs are excluded from cost averages; totals are known-cost subtotals. Inspect metrics_by_execution_mode before comparing live and scripted runs.

| Metric | Value |
| --- | --- |
| total_runs | 37 |
| status_counts | {"success": 9, "blocked": 23, "pending_approval": 2, "rejected": 2, "failed": 1} |
| success_rate | 0.24324324324324326 |
| failure_rate | 0.02702702702702703 |
| average_latency_s | 1.8394173941058987 |
| p95_latency_s | 7.016605457989499 |
| estimated_total_known_cost_usd | 0.00502575 |
| estimated_average_known_cost_usd | 0.00029563235294117644 |
| known_cost_runs | 17 |
| unknown_cost_runs | 20 |
| tool_call_counts | {"lookup_account_context": 3, "list_open_opportunities": 1, "summarize_pipeline": 1, "analyze_crm": 2, "send_email": 2, "draft_email": 3} |
| tool_attempt_counts | {"lookup_account_context": 3, "list_open_opportunities": 1, "summarize_pipeline": 1, "lookup_internal_hr_data": 1, "lookup_internal_financial_data": 1, "finalize_email": 1, "analyze_crm": 8, "send_email": 10, "draft_email": 3} |
| guardrail_blocks | 23 |
| hitl_approvals | 2 |
| hitl_rejections | 2 |
| common_failure_reasons | {"executive_compensation": 3, "restricted_hr": 4, "confidential_ma": 2, "confidential_layoffs": 2, "confidential_strategy": 2, "prompt_injection": 1, "restricted_internal_data": 2, "unknown_tool": 1, "unsafe_commitment": 1, "unsafe_analysis_request": 5, "human_rejected": 2, "TimeoutError": 1} |
| execution_modes | {"live": 10, "scripted": 27} |
| metrics_by_execution_mode | {"live": {"total_runs": 10, "status_counts": {"success": 7, "pending_approval": 1, "rejected": 1, "blocked": 1}, "success_rate": 0.7, "failure_rate": 0.0, "average_latency_s": 6.738380083200172, "p95_latency_s": 26.33938770799432, "estimated_total_known_cost_usd": 0.00502575, "estimated_average_known_cost_usd": 0.000502575, "known_cost_runs": 10, "unknown_cost_runs": 0, "tool_call_counts": {"lookup_account_context": 3, "list_open_opportunities": 1, "summarize_pipeline": 1, "draft_email": 3, "send_email": 1, "analyze_crm": 1}, "tool_attempt_counts": {"lookup_account_context": 3, "list_open_opportunities": 1, "summarize_pipeline": 1, "draft_email": 3, "send_email": 5, "analyze_crm": 1}, "guardrail_blocks": 1, "hitl_approvals": 1, "hitl_rejections": 1, "common_failure_reasons": {"human_rejected": 1, "executive_compensation": 1}, "execution_modes": {"live": 10}}, "scripted": {"total_runs": 27, "status_counts": {"blocked": 22, "success": 2, "pending_approval": 1, "rejected": 1, "failed": 1}, "success_rate": 0.07407407407407407, "failure_rate": 0.037037037037037035, "average_latency_s": 0.02498676851542701, "p95_latency_s": 0.06109337499947287, "estimated_total_known_cost_usd": 0.0, "estimated_average_known_cost_usd": 0.0, "known_cost_runs": 7, "unknown_cost_runs": 20, "tool_call_counts": {"analyze_crm": 1, "send_email": 1}, "tool_attempt_counts": {"lookup_internal_hr_data": 1, "lookup_internal_financial_data": 1, "finalize_email": 1, "analyze_crm": 7, "send_email": 5}, "guardrail_blocks": 22, "hitl_approvals": 1, "hitl_rejections": 1, "common_failure_reasons": {"executive_compensation": 2, "restricted_hr": 4, "confidential_ma": 2, "confidential_layoffs": 2, "confidential_strategy": 2, "prompt_injection": 1, "restricted_internal_data": 2, "unknown_tool": 1, "unsafe_commitment": 1, "unsafe_analysis_request": 5, "human_rejected": 1, "TimeoutError": 1}, "execution_modes": {"scripted": 27}}} |
