# CloudCostLens Cost Summary Report

_Generated: 2026-07-09 12:04:54_

## Executive Summary

- **Total Spend:** $785,599.93
- **Total Records:** 22,500
- **Date Range:** 2026-04-11 → 2026-07-09
- **Number of Anomalies:** 702

## Top 5 Services by Spend

| service | provider | total_cost |
| --- | --- | --- |
| Azure ML | AWS | $32,931.50 |
| Vertex AI | Azure | $31,479.22 |
| SageMaker | Azure | $29,629.97 |
| SageMaker | AWS | $25,026.19 |
| SageMaker | GCP | $24,961.38 |

## Top 5 Projects by Spend

| project | total_cost |
| --- | --- |
| data-platform | $135,090.05 |
| ml-pipeline | $132,069.12 |
| web-app | $131,376.91 |
| analytics-hub | $130,941.12 |
| mobile-backend | $129,079.93 |

## Budget Status Summary

| budget_status | project_count |
| --- | --- |
| OVER_BUDGET | 6 |

## Top 10 Cost Anomalies

| billing_date | service | project | daily_cost | anomaly_amount | anomaly_pct | anomaly_severity |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-04-25 | SageMaker | analytics-hub | $3,773.83 | $3,285.49 | 672.79% | HIGH |
| 2026-04-19 | Azure ML | data-platform | $3,613.95 | $3,255.70 | 908.77% | HIGH |
| 2026-04-18 | Azure ML | mobile-backend | $2,609.48 | $2,506.65 | 2437.73% | HIGH |
| 2026-06-20 | Vertex AI | web-app | $2,539.48 | $2,416.97 | 1972.89% | HIGH |
| 2026-05-31 | Azure ML | mobile-backend | $2,412.26 | $2,326.61 | 2716.42% | HIGH |
| 2026-06-20 | Azure ML | web-app | $2,471.32 | $2,315.50 | 1485.99% | HIGH |
| 2026-04-18 | SageMaker | mobile-backend | $2,195.00 | $2,072.36 | 1689.75% | HIGH |
| 2026-04-19 | SageMaker | ml-pipeline | $2,297.29 | $2,021.20 | 732.07% | HIGH |
| 2026-04-25 | SageMaker | ml-pipeline | $2,542.59 | $1,978.00 | 350.34% | MEDIUM |
| 2026-04-18 | Vertex AI | web-app | $1,983.75 | $1,778.67 | 867.32% | HIGH |

## Interpretation

Over the reporting window from 2026-04-11 to 2026-07-09, CloudCostLens recorded $785,599.93 in simulated cloud spend. The largest cost drivers are concentrated in **Azure ML** services and the **data-platform** project. 702 cost anomalies were detected using rolling 14-day statistics, suggesting occasional spikes in daily service spend. Budget tracking shows 6 project(s) currently marked as OVER_BUDGET, which indicates spend has exceeded the configured project budget thresholds.
