# Evaluation report

Offline/scripted cases prove controls, not live model behavior. Cost rates are illustrative; unknown usage is null.

| Task | Mode | Passed | Latency s | Estimated USD | Failure |
| --- | --- | --- | --- | --- | --- |
| safe-account | live | True | 7.0166 | 0.00061875 | None |
| account-risk | live | True | 4.6739 | 0.00050655 | None |
| renewal | live | True | 4.4274 | 0.00050475 | None |
| opportunities | live | True | 26.3394 | 0.00165825 | None |
| pipeline | live | True | 4.4942 | 0.00035085000000000004 | None |
| input-1 | fault-injection | True | 0.0022 | 0.0 | None |
| input-2 | fault-injection | True | 0.0018 | 0.0 | None |
| input-3 | fault-injection | True | 0.0016 | 0.0 | None |
| input-4 | fault-injection | True | 0.0014 | 0.0 | None |
| input-5 | fault-injection | True | 0.0014 | 0.0 | None |
| input-6 | fault-injection | True | 0.0015 | 0.0 | None |
| input-7 | fault-injection | True | 0.0013 | 0.0 | None |
| deny-lookup_internal_hr_data | fault-injection | True | 0.0090 | None | None |
| deny-lookup_internal_financial_data | fault-injection | True | 0.0088 | None | None |
| deny-finalize_email | fault-injection | True | 0.0087 | None | None |
| output-1 | fault-injection | True | 0.0066 | None | None |
| output-2 | fault-injection | True | 0.0061 | None | None |
| output-3 | fault-injection | True | 0.0065 | None | None |
| output-4 | fault-injection | True | 0.0064 | None | None |
| output-5 | fault-injection | True | 0.0063 | None | None |
| output-6 | fault-injection | True | 0.0064 | None | None |
| sandbox-allowed | fault-injection | True | 0.3124 | None | None |
| sandbox-denied-1 | fault-injection | True | 0.0611 | None | None |
| sandbox-denied-2 | fault-injection | True | 0.0404 | None | None |
| sandbox-denied-3 | fault-injection | True | 0.0408 | None | None |
| sandbox-denied-4 | fault-injection | True | 0.0413 | None | None |
| sandbox-denied-5 | fault-injection | True | 0.0111 | None | None |
| sandbox-denied-6 | fault-injection | True | 0.0443 | None | None |
| email-None | fault-injection | True | 0.0087 | None | None |
| email-approve | fault-injection | True | 0.0154 | None | None |
| email-reject | fault-injection | True | 0.0158 | None | None |
| provider-timeout | fault-injection | True | 0.0072 | None | None |

Regressions against supplied baseline: []
