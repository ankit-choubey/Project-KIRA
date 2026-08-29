# CLAIMS

Every claim that appears in the report, the writeup, the UI or a slide must have a
row here, and every row must name a `run_id`.

**A claim with no run_id does not go in the report.** Gate 6 enforces that the
active run is not a fixture; this table is the human half of the same rule.

| ID | Claim | Metric | Value | run_id | Where it appears |
|---|---|---|---|---|---|
| C-001 | _pending_ | PR-AUC on held-out temporal test | not measured | — | report §Results |
| C-002 | _pending_ | ECE after isotonic calibration | not measured | — | report §Calibration |
| C-003 | _pending_ | ASR at query budget 20 | not measured | — | report §Red team |
| C-004 | _pending_ | ASR on held-out variants, round 0 vs 3 | not measured | — | report §Closed loop |
| C-005 | _pending_ | ASR on unseen family (zero-day transfer) | not measured | — | report §Closed loop |
| C-006 | _pending_ | Minimum Evasion Distance, round 0 vs 3 | not measured | — | report §Headline |
| C-007 | _pending_ | Behavioural fidelity P1–P4 degradation ratio | not measured | — | report §Fidelity |
| C-008 | _pending_ | C2ST AUC, row level and entity level | not measured | — | report §Fidelity |
| C-009 | _pending_ | External anchor PR-AUC on Sparkov | not measured | — | report §Anchor |
| C-010 | _pending_ | End-to-end latency P50/P95/P99 over HTTP | not measured | — | report §Latency |
| C-011 | _pending_ | Intent-engine ablation, with vs without | not measured | — | report §Ablations |
| C-012 | _pending_ | SMOTE vs `scale_pos_weight` on ECE and FPR | not measured | — | report §Ablations |

## External claims — source and date required

| ID | Claim | Source | Verified |
|---|---|---|---|
| X-001 | Mastercard Verifiable Intent is an open, standards-based framework linking identity, instruction and outcome (March 2026) | Mastercard newsroom | yes |
| X-002 | Mastercard Agent Pay for Machines targets high-frequency machine-driven payments (June 2026) | Mastercard investor relations | yes |
| X-003 | Published tabular generators score 17×–99× on behavioural fidelity axes where 1.0 = real | arXiv 2604.13125 | yes |
| X-004 | SMOTE distorts posterior probabilities; false alarms 35 -> 5,775 with ROC-AUC ~unchanged | IJCT 2024 posterior-bias study; Dal Pozzolo et al. | yes |
| X-005 | Sparkov dataset is CC0 public domain | Kaggle dataset metadata | yes |

**Withdrawn — do not cite:** arXiv 2509.22850 ("Boundary on the Table"). It fits our
threat model well but was withdrawn by its author. Citing a withdrawn paper is worse
than having no citation.

## Claims we will never make without evidence

state-of-the-art · better than Mastercard's systems · production integration ·
EMV 3DS integration · real Verifiable Intent verification · guaranteed privacy ·
a specific latency SLA declared before it was measured.
