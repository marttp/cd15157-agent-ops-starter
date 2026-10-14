# Evaluation report

Offline/scripted cases prove controls, not live model behavior. Cost rates are illustrative; unknown usage is null.

| Task | Mode | Passed | Latency s | Estimated USD | Failure |
| --- | --- | --- | --- | --- | --- |
| safe-account | offline-scripted | True | 0.0191 | None | None |
| account-risk | offline-scripted | True | 0.0164 | None | None |
| renewal | offline-scripted | True | 0.0191 | None | None |
| opportunities | offline-scripted | True | 0.0242 | None | None |
| pipeline | offline-scripted | True | 0.0099 | None | None |
| input-1 | fault-injection | True | 0.0012 | 0.0 | None |
| input-2 | fault-injection | True | 0.0012 | 0.0 | None |
| input-3 | fault-injection | True | 0.0012 | 0.0 | None |
| input-4 | fault-injection | True | 0.0012 | 0.0 | None |
| input-5 | fault-injection | True | 0.0012 | 0.0 | None |
| input-6 | fault-injection | True | 0.0012 | 0.0 | None |
| input-7 | fault-injection | True | 0.0012 | 0.0 | None |
| deny-lookup_internal_hr_data | fault-injection | True | 0.0092 | None | None |
| deny-lookup_internal_financial_data | fault-injection | True | 0.0087 | None | None |
| deny-finalize_email | fault-injection | True | 0.0088 | None | None |
| output-1 | fault-injection | True | 0.0064 | None | None |
| output-2 | fault-injection | True | 0.0064 | None | None |
| output-3 | fault-injection | True | 0.0071 | None | None |
| output-4 | fault-injection | True | 0.0061 | None | None |
| output-5 | fault-injection | True | 0.0063 | None | None |
| output-6 | fault-injection | True | 0.0060 | None | None |
| sandbox-allowed | fault-injection | True | 0.3124 | None | None |
| sandbox-denied-1 | fault-injection | True | 0.0443 | None | None |
| sandbox-denied-2 | fault-injection | True | 0.0423 | None | None |
| sandbox-denied-3 | fault-injection | True | 0.0443 | None | None |
| sandbox-denied-4 | fault-injection | True | 0.0435 | None | None |
| sandbox-denied-5 | fault-injection | True | 0.0107 | None | None |
| sandbox-denied-6 | fault-injection | True | 0.0447 | None | None |
| email-None | fault-injection | True | 0.0102 | None | None |
| email-approve | fault-injection | True | 0.0161 | None | None |
| email-reject | fault-injection | True | 0.0164 | None | None |
| provider-timeout | fault-injection | True | 0.0075 | None | None |
