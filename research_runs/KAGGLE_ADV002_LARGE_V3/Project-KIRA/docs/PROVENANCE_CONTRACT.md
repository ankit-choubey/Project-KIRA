# KIRA Provenance Drawer Contract

**Objective**: Guarantee end-to-end cryptographic and scientific traceability for every number displayed on the KIRA dashboard.

---

## 1. Provenance Schema Fields

Every displayed figure must bind to a `ProvenanceRecord` containing the following 17 canonical fields:

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `claim_id` | string | Unique identifier for the empirical claim | `CLM_001_BASELINE_PRAUC` |
| `experiment_id` | string | Standard experiment designation | `EXP_BASELINE_BLUE` |
| `dataset_id` | string | Evaluated dataset | `KIRA_SYNTHETIC` |
| `scale` | string | World scale configuration | `full` |
| `run_id` | string | Unique execution run identifier | `run_full_s20260827_...` |
| `world_seed` | integer | Seed used for synthetic world generation | `20260827` |
| `model_seed` | integer / null | Seed used for model fitting | `20260827` |
| `sample_count` | integer / null | Total number of evaluated transactions | `100000` |
| `positive_count` | integer / null | Total fraud transactions in evaluation | `5000` |
| `metric` | string | Formal metric name | `pr_auc` |
| `raw_value` | float / null | Exact unrounded value from artifact | `0.93748192` |
| `confidence_interval_95` | [float, float] / null | 95% bootstrap confidence interval | `[0.9281, 0.9463]` |
| `p_value` | float / null | Statistical hypothesis test p-value | `0.0021` |
| `artifact_path` | string | Relative file path in repository | `artifacts/blue_metrics.json` |
| `json_path` | string | Exact JSONPath inside the artifact | `metrics.pr_auc` |
| `git_sha` | string | Commit SHA producing the artifact | `e7c0615174...` |
| `classification` | enum | Audit classification | `MEASURED` |

---

## 2. Drawer UX Behavior
- **Trigger**: Clicking any metric badge, table cell, or authenticity chip opens the drawer from the right.
- **Header**: Displays `Metric Name` + `Classification Badge` (e.g. `MEASURED`, `MEASURED_WITH_CAVEAT`, `FAILURE_FINDING`).
- **File Link**: Displays the source artifact path and JSON pointer.
- **Copy Provenance Button**: Copies a JSON snippet of the provenance record to the user's clipboard for external verification.
