# CLAIMS

Every claim that appears in the report, the writeup, the UI or a slide must have a
row here, and every row must name a `run_id`.

**A claim with no run_id does not go in the report.** Gate 6 enforces that the
active run is not a fixture; this table is the human half of the same rule.

| ID | Claim | Metric | Value | run_id | Where it appears |
|---|---|---|---|---|---|
| C-001 | Blue champion achieves 0.641 PR-AUC under strict temporal out-of-time evaluation | PR-AUC on held-out temporal test | 0.640716 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Results |
| C-002 | Isotonic calibration bounds probability error to zero | ECE after isotonic calibration | 0.0000 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Calibration |
| C-003 | Hardening reduces ASR at budget=20 from 90.0% to 1.58% | ASR at query budget 20 | 0.0158 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Red team |
| C-004 | Generalisation across held-out variants drops from 83.6% to 1.62% | ASR on held-out variants, round 0 vs 3 | 0.8364 -> 0.0162 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Closed loop |
| C-005 | Zero-day transfer to unseen attack families | ASR on unseen family (zero-day transfer) | not measured | — | report §Closed loop |
| C-006 | Adversarial hardening forces attackers to perturb features closer to decision boundary | Minimum Evasion Distance, round 0 vs 3 | 2.7274 -> 1.3291 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Headline |
| C-007 | Physics and marginal fidelity pass all checks with zero physical violations | Behavioural fidelity P1–P4 degradation ratio | not measured | — | report §Fidelity |
| C-008 | Statistical correlation distance is bounded at 0.18 | L2 Correlation Distance | 0.1800 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Fidelity |
| C-009 | External anchor on real-world ULB benchmark demonstrates strong detection | External anchor PR-AUC on ULB | 0.8640 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Anchor |
| C-010 | Scoring latency profile over HTTP benchmark path | End-to-end latency P50/P95/P99 | 2.15 / 4.80 / 8.30 ms | run_tiny_s20260827_193f7897_9cfa1e1 | report §Latency |
| C-011 | Mandate violation vector scoring contributes to zero physical violations | Intent-engine ablation, with vs without | not measured | — | report §Ablations |
| C-012 | High benign approval rate maintained with FPR < 0.1% | False Positive Rate (FPR) | 0.000715 | run_tiny_s20260827_193f7897_9cfa1e1 | report §Ablations |

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
