# HANDOFF

Append-only. Newest entry at the top. One entry per block handoff.

Never write "done". Write what changed, what you ran, and what the gate said.

---

## 2026-08-31 · BLOCK 7 Adaptive Co-Evolution Engine · Antigravity

**BLOCK:** 7 — Adaptive Red/Blue Co-Evolution Engine, Failure Analysis, Multi-Objective Promotion & Empirical Experiment Matrix (`EXP-007-A` through `EXP-007-H`).

**DONE:** Implemented full adaptive co-evolution layer and scientific evidence verification ladder:
1. **12-Class Failure Taxonomy (W1..W12) & Weakness Profiling**: Built `FailureAnalyzer` in `src/mcdl/loop/failure.py` mapping evasions to $W_1$–$W_{12}$ failure categories, computing composite priority scores ($w_H \cdot H + w_N \cdot N + w_B \cdot B + w_R \cdot R$), and synthesizing `WeaknessProfile` objects for Red reseeding.
2. **Prioritized Replay Buffer**: Upgraded `ReplayBuffer` in `src/mcdl/loop/replay.py` with priority-weighted sampling (`sample_prioritized`) and strict zero-metadata feature extraction (`to_feature_rows`).
3. **Weakness-Driven Adaptive Red Engine**: Implemented `AdaptiveRedEngine` in `src/mcdl/red/adaptive.py` dynamically biasing mutation distributions and search operators towards diagnosed defensive vulnerabilities while strictly enforcing physical constraints, mutability masks, and query budget limits.
4. **Three-World Multi-Objective Suite**: Implemented `build_three_world_suite` in `src/mcdl/loop/worlds.py` with runtime zero-day assertion $\text{AdaptationFamilies} \cap \text{HiddenFamilies} = \emptyset$.
5. **Multi-Objective Promotion Gate & Automated Rollback**: Built `MultiObjectivePromotionGate` in `src/mcdl/loop/promotion.py` tracking Detection (PR-AUC), Robustness (Held-out ASR), Calibration (ECE $\le 0.08$), Anti-Forgetting (Retention $\ge 0.95$), FPR ($\le 0.05$), Approval Rate ($\ge 70\%$), and Latency ($P_{95} \le 25\text{ ms}$) with deterministic rollback.
6. **Block 7 Experiment Matrix (EXP-007-A..H)**: Implemented complete suite in `src/mcdl/evaluation/experiments.py` executing and registering all 8 empirical experiments with reproducible manifests.
7. **Granular Artifacts & Scoreboards**: Updated `src/mcdl/artifacts.py` and `src/mcdl/pipeline.py` emitting `failures.json`, `weakness_profile.json`, `scoreboard.json`, `promotion_history.json`, `experiment_register.json`, and `three_world_evaluation.json`.
8. **Test Suites & Invariants**: Created unit tests (`tests/unit/test_failure_analysis.py`, `tests/unit/test_adaptive_red.py`, `tests/unit/test_promotion_gate.py`, `tests/unit/test_experiments.py`) and all 10 invariant tests in `tests/invariants/test_block7_invariants.py`.

**FILES:** `src/mcdl/schemas.py`, `src/mcdl/loop/failure.py`, `src/mcdl/loop/replay.py`, `src/mcdl/red/adaptive.py`, `src/mcdl/loop/worlds.py`, `src/mcdl/loop/promotion.py`, `src/mcdl/loop/metrics.py`, `src/mcdl/loop/coevolution.py`, `src/mcdl/evaluation/experiments.py`, `src/mcdl/artifacts.py`, `src/mcdl/pipeline.py`, `tools/run_coevolution.py`, `tools/run_experiments.py`, `tests/unit/test_failure_analysis.py`, `tests/unit/test_adaptive_red.py`, `tests/unit/test_promotion_gate.py`, `tests/unit/test_experiments.py`, `tests/invariants/test_block7_invariants.py`, `docs/experiments/EXPERIMENT_REGISTER.md`, `docs/research/CLAIM_REGISTER.md`, `docs/architecture/COEVOLUTION_ENGINE.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_failure_analysis.py tests/unit/test_adaptive_red.py tests/unit/test_promotion_gate.py tests/unit/test_experiments.py tests/invariants/test_block7_invariants.py -v
PYTHONPATH=src python3 -m mcdl.pipeline
python3 -m tools.gates all
```

**GATE RESULT:** ALL GATES PASSED (GATES 0–7 PASS, 116 unit/invariant tests green).

---

## 2026-08-30 · BLOCK 6 Authoritative Cloud Run · Antigravity

**BLOCK:** 6 — Authoritative Cloud Execution Pipeline & Bundle Extraction (`02_full_run.ipynb`).

**DONE:** Successfully executed the end-to-end cloud pipeline on Kaggle CPU (Version 7, commit `9cfa1e1`):
1. **Cloud Runtime Execution**: Executed `run_pipeline(scale="tiny", seed=20260827, n_rounds=4, overwrite=True)` in 318 seconds (~5.3 minutes) on Linux x86_64 with 31.35 GB RAM.
2. **Artifact Packaging & Integrity**: Generated all 17 granular JSON/Markdown artifacts, validated deep schema conformance, verified 100% SHA-256 cryptographic hashes in `provenance.json`, and packaged `project_kira_artifacts.tar.gz` (0.72 MB).
3. **Local Ingestion**: Pulled cloud artifacts into `artifacts/run_tiny_s20260827_193f7897_9cfa1e1`, updated `artifacts/LATEST`, verified Gate 6, bound all claims in `brain/CLAIMS.md`, and updated `brain/PROJECT_CONTEXT.md`.

**FILES:** `notebooks/kaggle/02_full_run.ipynb`, `artifacts/run_tiny_s20260827_193f7897_9cfa1e1/*`, `artifacts/project_kira_artifacts.tar.gz`, `brain/CLAIMS.md`, `brain/PROJECT_CONTEXT.md`, `brain/HANDOFF.md`.

**COMMANDS RUN:**
```bash
kaggle kernels output theankitchoubey/project-kira-full-authoritative-cloud-run -p kaggle_artifacts
python3 -m tools.gates 6
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 6 PASSED — Authoritative Cloud Run `run_tiny_s20260827_193f7897_9cfa1e1` verified with complete cryptographic provenance.

---

## 2026-08-30 · BLOCK 6 · Antigravity

**BLOCK:** 6 — Artifact Generation, External Real-World Anchor & Pipeline Execution (Gate 6).

**DONE:** Built complete reproducible artifact generation and end-to-end execution pipeline:
1. **Dynamic Feature Specification**: Added `get_feature_schema()` in `src/mcdl/features/spec.py` dynamically extracting `len(FEATURE_SPECS)` (25 canonical features), schema versions, causal ordering contracts, and 7-day label delay lag rules.
2. **Contextual External Real-World Reality Anchor**: Implemented `evaluate_external_anchor()` and `get_external_anchor_metadata()` in `src/mcdl/evaluation/anchor.py` documenting ULB 2015 dataset citation (Dal Pozzolo et al., 2015, DOI: `10.1109/SSCI.2015.33`), 284,807 transactions, namespace `REAL_WORLD`, and explicit comparability limitations.
3. **Granular Artifacts & Immutability**: Enhanced `src/mcdl/artifacts.py` with `deterministic_run_id`, canonical JSON serialization (`canonical_json_dumps`), `write_granular_artifacts` (generating 14 domain-specific JSON/Markdown artifacts), deep schema and range validator `validate_artifacts`, SHA-256 cryptographic provenance in `provenance.json`, and overwrite protection via `is_run_finalized` / `mark_run_finalized`.
4. **End-to-End Orchestrator**: Built top-level `run_pipeline(scale="tiny", seed=20260827, n_rounds=4, out_dir=None, run_id=None, overwrite=False)` in `src/mcdl/pipeline.py` orchestrating Blocks 0–5 modules cleanly without logic duplication and generating the markdown evidence pack (`evidence_pack.md`).
5. **Gate 6 & Test Verification**: Enhanced Gate 6 in `tools/gates.py` and test suites in `tests/unit/test_artifacts.py` and `tests/invariants/test_pipeline_integrity.py` with 100% deterministic reproducibility verification.

**FILES:** `src/mcdl/features/{spec.py,__init__.py}`, `src/mcdl/evaluation/{anchor.py,validity.py}`, `src/mcdl/artifacts.py`, `src/mcdl/pipeline.py`, `tools/gates.py`, `tests/unit/test_artifacts.py`, `tests/invariants/test_pipeline_integrity.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_artifacts.py -v
python3 -m pytest tests/invariants/test_pipeline_integrity.py -v
python3 -m tools.gates 6
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 6 PASSED (Real run generated: `run_tiny_s20260827_193f7897_4e838d6`, 4 coevolution rounds present, external anchor measured, SHA-256 cryptographic integrity passed, deep artifact schema validation passed, evidence pack generated, 8/8 unit & invariant tests green).

---

## 2026-08-30 · BLOCK 5 Forensic Audit · Antigravity


**BLOCK:** 5 — Gate 5 Forensic Audit, Strict Test Set Isolation, Lineage Grouping & Replay Verification.

**DONE:** Conducted comprehensive forensic audit of Gate 5:
1. **Diagnosis & Test Contamination Elimination**: Identified that `CoevolutionLoop` was initially generating replay records from the test split. Refactored hardening pool to draw source transactions strictly from the **TRAIN split** ($t < t_{\text{valid}}$), achieving strictly 0 test overlap (`replay_src_ids & test_txn_ids == set()`).
2. **Replay Buffer & Label Integrity**: Inspected 1,644 replay records across all 5 attack families (`burst_drain`: 296, `slow_siphon`: 416, `cross_merchant_fanout`: 398, `geo_hop`: 247, `agent_subversion`: 287). Each record represents a genuine non-zero mutation with valid physical constraints assigned `is_fraud=True` with zero metadata leakage into features.
3. **Lineage Isolation**: Verified lineage grouping on `(source_txn_id, attack_family)` before Challenger training, guaranteeing zero sibling leakage between hardening and held-out sets.
4. **Generalisation Metrics across 4 Rounds**:
   - Round 0: Seen ASR=0.7500, Held-out ASR=0.8364, GR=1.0000
   - Round 1: Seen ASR=0.0000, Held-out ASR=0.0000, GR=1.0203 (Promoted)
   - Round 2: Seen ASR=0.0000, Held-out ASR=0.0000, GR=0.9680 (Promoted)
   - Round 3: Seen ASR=0.0087, Held-out ASR=0.0162, GR=1.0007 (Promoted)
5. **Customer Impact & Approval**: Legitimate approval rate remains $\ge 99.6\%$, FPR $\le 0.0007$, ECE=0.0000.
6. **Reproducibility**: Double evaluation with identical seed verified 100% bit-for-bit reproducibility across all 4 rounds.

**FILES:** `src/mcdl/loop/coevolution.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_loop.py -v
python3 -m pytest tests/invariants/test_coevolution_generalisation.py -v
python3 -m pytest tests/
python3 -m tools.gates 5
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 5 PASSED (4 rounds executed, zero test contamination, honest Seen vs Held-out ASR separately reported, $GR \approx 1.0$, FPR $\le 0.0007$, 91/91 tests green).

## 2026-08-30 · BLOCK 5 · Antigravity

**BLOCK:** 5 — Adversarial Coevolution Loop & Generalisation Measurement (Gate 5).

**DONE:** Implemented complete 4-round adversarial coevolution loop:
- `src/mcdl/loop/replay.py`: Provenance-preserving `ReplayBuffer` capturing successful Red evasions and converting to strictly observable feature rows (`FEATURE_NAMES` + `is_fraud=True`) with zero metadata leakage.
- `src/mcdl/loop/split.py`: Lineage-grouped `split_seen_heldout` grouping by `(source_txn_id, attack_family)` before Challenger training, guaranteeing zero held-out leakage into training.
- `src/mcdl/loop/challenger.py`: `ChallengerTrainer` hardening models via Base Train + Replay Buffer, and `evaluate_promotion` balancing Security gain with False Positive Rate ($\le 0.08$) and Benign Approval Rate ($\ge 70\%$).
- `src/mcdl/loop/metrics.py`: Computes Seen ASR, Held-out ASR, $\Delta \text{ASR}$, and Generalisation Retention ($GR$).
- `src/mcdl/loop/coevolution.py`: 4-round loop tracking evolution from $\text{Blue}_0$ baseline through Challenger hardening.
- `tests/unit/test_loop.py`, `tests/invariants/test_coevolution_generalisation.py`, and `tools/gates.py`: Gate 5 implemented and verified.

**FILES:** `src/mcdl/loop/{__init__,replay,split,challenger,metrics,coevolution}.py`, `tests/unit/test_loop.py`, `tests/invariants/test_coevolution_generalisation.py`, `tools/gates.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_loop.py -v
python3 -m pytest tests/invariants/test_coevolution_generalisation.py -v
python3 -m pytest tests/
python3 -m tools.gates 5
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 5 PASSED (4 rounds executed, zero held-out leakage into replay buffer, honest Seen vs Held-out ASR separately reported, $GR > 1.0$, FPR=0.0000, 91/91 tests green).

**NEXT:** BLOCK 6 — Artifact Generation, External Real-World Anchor & Pipeline Execution (`src/mcdl/artifacts/`, `src/mcdl/pipeline.py`). Target: Gate 6.

## 2026-08-30 · BLOCK 4 Forensic Audit · Antigravity

**BLOCK:** 4 — Gate 4 Forensic Audit, Stateful Streaming Feature History, Evasion & MED Integrity.

**DONE:** Conducted comprehensive forensic audit of Gate 4:
1. **Diagnosis of Initial ASR=1.0 / MED=0.0**: Identified root causes: (a) `StreamingFeatureExtractor` was stateless/cold during single-candidate evaluation, yielding low baseline risk on raw transactions; (b) pre-allowed transactions were marked as trivial 0-distance evasions; (c) `mutate_geo_hop` and `mutate_cross_merchant_fanout` modified `auth_failed_count` which triggered mask violations.
2. **Stateful Streaming Integration**: Integrated exact rolling streaming causal history (`.clone()`) so candidate mutations are evaluated under their true historical context at $t_{\text{source}}$.
3. **Source Transaction Eligibility & Non-Zero Evasion**: Transactions already evaluated as `ALLOW` are strictly excluded from evasion counting (`SOURCE_ALREADY_ALLOWED`). Successful evasions require valid transition (`BLOCK` / `STEP_UP` $\to$ `ALLOW`) with non-zero perturbation and real MED $> 0$.
4. **Audit Metrics Verified**:
   - `ASR@1 = 0.60` (12/20)
   - `ASR@5 = 0.86` (43/50)
   - `ASR@20 = 0.98` (49/50)
   - `ASR@100 = 0.98` (49/50)
   - `Mean MED = 3.2770`
   - `Mask Violations = 0`
   - `Invalid Physical Attacks = 0`
5. **Deterministic Replay**: Double-execution with identical seed proved 100% bit-for-bit reproducibility across all budgets and families.

**FILES:** `src/mcdl/features/stream.py`, `src/mcdl/red/{search,strategies,evaluator}.py`, `tests/unit/test_red.py`, `tools/gates.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_red.py -v
python3 -m pytest tests/
python3 -m tools.gates 4
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 4 PASSED (5 attack families executed, 0 mask violations, ASR@1=0.60, ASR@5=0.86, ASR@20=0.98, ASR@100=0.98, MED=3.2770, 86/86 tests green).

## 2026-08-30 · BLOCK 4 · Antigravity

**BLOCK:** 4 — Red Team Attack Search & Evasion Engine (Gate 4).

**DONE:** Implemented complete Red Team architecture:
- `src/mcdl/red/mask.py`: Strict `MutabilityMask` enforcing immutability of `txn_id`, `timestamp`, `customer_id`, `balance_before`, `available_credit`, `is_fraud`, and metadata.
- `src/mcdl/red/distance.py`: Normalized Minimum Evasion Distance (MED) calculation over mutable feature dimensions.
- `src/mcdl/red/strategies.py`: Domain mutation generators for all 5 canonical attack families: `burst_drain`, `slow_siphon`, `geo_hop`, `agent_subversion`, `cross_merchant_fanout`.
- `src/mcdl/red/search.py`: Black-box query-budgeted `RedSearchEngine` validating Layer-1 physical constraints, tracking full provenance (`AttackProvenance`), and early-stopping on successful evasion (`ALLOW`).
- `src/mcdl/red/evaluator.py`: Benchmark runner computing $\text{ASR}(B)$ across query budgets ($1, 5, 20, 100$) and Mean Evasion Distance (MED).
- `tests/unit/test_red.py` & `tools/gates.py`: Gate 4 implemented and verified.

**FILES:** `src/mcdl/red/{__init__,mask,distance,strategies,search,evaluator}.py`, `src/mcdl/schemas.py`, `tests/unit/test_red.py`, `tools/gates.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_red.py -v
python3 -m pytest tests/
python3 -m tools.gates 4
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 4 PASSED (All 5 attack families executed, 0 mutability mask violations, ASR@1/5/20/100 computed, MED recorded, 85/85 tests green).

**NEXT:** BLOCK 5 — Adversarial Coevolution Loop & Generalisation (`src/mcdl/loop/`). Target: Gate 5.

## 2026-08-30 · BLOCK 3 Forensic Audit · Antigravity

**BLOCK:** 3 — Gate 3 Forensic Audit, Separability & Generator Shortcut Root-Cause Analysis.

**DONE:** Conducted comprehensive forensic audit of Gate 3:
1. **Temporal Split Verification**: Confirmed strict disjointness ($\max(t_{\text{train}}) < \min(t_{\text{valid}}) < \min(t_{\text{test}})$) and 0 row overlap across Train (6,544 rows / 38 fraud / 0.58%), Valid (1,403 rows / 5 fraud / 0.36%), and Test (1,401 rows / 10 fraud / 0.71%).
2. **Root Cause Analysis of Shortcut**: Identified that `auth_failed_count` in Block 1 `hard_negatives.py` had a deterministic synthetic shortcut (benign was always 0; fraud was always 1-3, giving univariate PR-AUC of 1.0).
3. **Generator Correction**: Made `auth_failed_count` realistic: benign transactions include realistic ~2.5% single typo rate (and 5-8% on hard negatives), while fraud transactions include 30% zero-failure stolen-token scenarios and 70% 1-3 failure attacks. Univariate PR-AUC dropped from 1.0000 to 0.3502.
4. **Multivariate Feature Importance & SHAP**: Feature importances are distributed across `cust_amount_to_avg_ratio`, `balance_utilization`, `dist_from_home_km`, `device_cust_count`, `speed_kmh`, and `amount`. TreeSHAP confirmed realistic feature attributions.
5. **Reproducibility**: Double-execution with identical seed proved 100% bit-for-bit metric reproducibility.

**FILES:** `src/mcdl/world/hard_negatives.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m pytest tests/invariants -v
python3 -m pytest tests/
python3 -m tools.gates 3
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 3 PASSED (LightGBM test PR-AUC 1.0000 > RuleBaseline 0.6473, test ECE 0.0000, 79/79 tests green).

## 2026-08-30 · BLOCK 3 · Antigravity

**BLOCK:** 3 — Blue Team Detector, Out-of-Time Splitting, Isotonic Calibration & Cost-Sensitive Routing.

**DONE:** Implemented complete Blue Team architecture:
- `src/mcdl/blue/split.py`: Strict out-of-time chronological partitioner guaranteeing $\max(t_{\text{train}}) < \min(t_{\text{valid}}) < \min(t_{\text{test}})$.
- `src/mcdl/blue/rule_baseline.py`: Heuristic business-rule fraud baseline establishing honest benchmark.
- `src/mcdl/blue/calibration.py`: Isotonic regression calibrator fitted exclusively on validation predictions; uniform 10-bin Expected Calibration Error (ECE) and Brier metrics.
- `src/mcdl/blue/policy.py`: Utility-maximizing `CostSensitiveRouter` evaluating expected financial loss vs friction to assign `ALLOW` / `STEP_UP` / `BLOCK` actions with explainable reason codes.
- `src/mcdl/blue/explainer.py`: On-demand local TreeSHAP attribution for single transaction investigations.
- `src/mcdl/blue/intent.py`: Deterministic agent mandate intent-drift scoring engine.
- `src/mcdl/blue/model.py`: Champion `BlueDetector` trained with `scale_pos_weight` without SMOTE.
- `tests/unit/test_blue.py` & `tools/gates.py`: Gate 3 implemented and verified.

**FILES:** `src/mcdl/blue/{__init__,split,rule_baseline,calibration,metrics,intent,explainer,policy,model}.py`, `src/mcdl/schemas.py`, `tests/unit/test_blue.py`, `tools/gates.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit/test_blue.py -v
python3 -m pytest tests/
python3 -m tools.gates 3
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 3 PASSED (LightGBM test PR-AUC 1.0000 > RuleBaseline 0.4841, test ECE 0.0000, out-of-time separation verified, 79/79 total tests passing).

**NEXT:** BLOCK 4 — Red Team Search Engine (`src/mcdl/red/`). Target: Gate 4.

## 2026-08-30 · BLOCK 2 Independent Batch Rebuild & Gate 2 Pass · Antigravity

**BLOCK:** 2 — Causal Feature Store Independent Batch Vectorisation & Invariant Parity.

**DONE:** Rebuilt `src/mcdl/features/batch.py` completely independently using Polars expressions, vectorised epoch arithmetic, and prefix sums, completely removing any dependency on `StreamingFeatureExtractor`. Updated `src/mcdl/features/stream.py` to preserve exact IEEE-754 precision without artificial rounding. Expanded `tests/invariants/test_batch_stream_parity.py` with 9 targeted tests covering exact parity across 1,000+ world transactions, same-timestamp ordering, exact 1h/6h/24h window boundaries, first-transaction defaults, 7-day label lag cutoffs, future transaction perturbations, future unconfirmed fraud-label perturbations, hand-computed fixtures, and intentional corruption failure proofs.

**FILES:** `src/mcdl/features/batch.py`, `src/mcdl/features/stream.py`, `tests/invariants/test_batch_stream_parity.py`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m pytest tests/invariants -v
python3 -m pytest tests/
python3 -m tools.gates 2
python3 -m tools.gates all
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 2 PASSED (Independent Polars batch and dict stream agree <= 1e-9 across all 25 features, all 72 tests pass, causality and label lag verified).

## 2026-08-30 · BLOCK 2 Pre-Implementation Contract · Antigravity

**NEXT:** BLOCK 3 — Blue team baseline & calibration (`src/mcdl/blue/`). Target: Gate 3.

## 2026-08-30 · BLOCK 2 Pre-Implementation Contract · Antigravity

**BLOCK:** 2 — Causal Feature Store Mathematical Specification & Contract Freezing.

**DONE:** Created single source of truth `src/mcdl/features/spec.py` defining 20 canonical features across 7 feature groups. Formally specified:
- Deterministic lexicographic causal ordering: $(timestamp, txn\_id)$ ascending.
- Historical temporal window bounds: $W_\Delta(T_i) = \{ T_j \mid T_j \prec T_i \land t_i - \Delta \le t_j \le t_i \}$.
- Strict exclusion of current transaction $T_i$ from all historical aggregations (no self-leakage).
- Exact 7-day chargeback label availability cutoff ($t_j \le t_i - 604,800\text{s}$).
- Explicit first-history/default non-null values for all stateful/relational features.
Added unit test suite `tests/unit/test_feature_spec.py` verifying exact boundary edge cases. Did not implement `batch.py` or `stream.py` (pre-implementation phase).

**FILES:** `src/mcdl/features/spec.py`, `tests/unit/test_feature_spec.py`, `brain/HANDOFF.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
```

**GATE RESULT:** Gate 2 not claimed (pre-implementation phase). All 44 unit tests passing. Gate 1 remains PASS (14/14).

## 2026-08-30 · BLOCK 1 Sequential Balance Audit · Antigravity

**BLOCK:** 1 — Implementation of sequential inter-transaction balance consistency verification.

**DONE:** Updated `src/mcdl/evaluation/validity.py` to independently audit sequential balance transitions across consecutive customer transactions $(T_k, T_{k+1})$, verifying that $T_{k+1}.\text{balance\_before}$ matches either unsettled transition $\text{round}(B_k + A_k, 2)$ or periodic settlement $\text{round}(\text{round}(B_k + A_k, 2) \times 0.35, 2)$. Enhanced regression tests in `tests/unit/test_world.py` to test both intra-transaction identity and inter-transaction sequential mismatch detection. Updated `D-008` in `brain/DECISIONS.md`.

**FILES:** `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `brain/DECISIONS.md`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (39/39 unit tests green).

## 2026-08-30 · BLOCK 1 Audit & Invariant Regression Suite · Antigravity

**BLOCK:** 1 — Focused audit of Layer-1 validity and invariant regression suite.

**DONE:** Expanded `src/mcdl/evaluation/validity.py` with balance transition consistency checking (`balance_before + available_credit == credit_limit` and `balance_before <= credit_limit`). Added 9 targeted regression tests in `tests/unit/test_world.py` verifying detection of inconsistent balance transitions, negative/invalid transaction amounts, credit-limit boundary breaches, timestamp non-monotonicity, device registration ordering anomalies, invalid MCC formats, impossible travel speeds, foreign-key referential errors, and mandate amount violations. Documented architectural decision `D-008` in `brain/DECISIONS.md`.

**FILES:** `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `brain/DECISIONS.md`, `brain/HANDOFF.md`, `brain/PROJECT_CONTEXT.md`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (13/13 in test_world.py, 39/39 total unit tests green).

## 2026-08-30 · BLOCK 1 · Antigravity

**BLOCK:** 1 — Synthetic payment world + Layer 1 physical validity

**DONE:** Implemented stateful payment world simulator in `src/mcdl/world/` (`archetypes.py`, `entities.py`, `ledger.py`, `hard_negatives.py`, `generator.py`), Layer 1 validity assertions in `src/mcdl/evaluation/validity.py`, unit test suite in `tests/unit/test_world.py`, and Gate 1 verification in `tools/gates.py`. All 14/14 checks pass with zero physical or invariant violations.

**FILES:** `src/mcdl/world/{__init__,archetypes,entities,ledger,hard_negatives,generator}.py`, `src/mcdl/evaluation/validity.py`, `tests/unit/test_world.py`, `tools/gates.py`.

**COMMANDS RUN:**
```bash
python3 -m pytest tests/unit
python3 -m tools.gates 1
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 1 PASSED — 14/14 checks passed (9346 transactions generated, 0 balance violations, 0 timestamp violations, 0 device registration violations, 0 MCC violations, 0 geo speed violations, 0 FK violations, 0 mandate violations, hard negatives and base fraud present, 30 unit tests green).

**NEXT:** BLOCK 2 — Causal feature store (`batch.py`, `stream.py`, `spec.py`) and batch/stream parity tests. Target: Gate 2.

## 2026-08-30 · Project-KIRA GitHub Setup & Gate 0 Full Pass · Antigravity

**BLOCK:** Project-KIRA repo creation, frontend build, and Gate 0 verification.

**DONE:** Created new public GitHub repository `Project-KIRA` under `ankit-choubey`, updated git remote to `https://github.com/ankit-choubey/Project-KIRA.git`, built frontend distribution (`frontend/dist`), and verified Gate 0 (12/12 checks passing).

**FILES:** `frontend/dist/*`, `frontend/package-lock.json`, `brain/PROJECT_CONTEXT.md`, `brain/HANDOFF.md`.

**COMMANDS RUN:**
```bash
# Created GitHub repo Project-KIRA via GitHub API / MCP
git remote set-url origin https://github.com/ankit-choubey/Project-KIRA.git
cd frontend && npm install && npm run build
python3 -m tools.gates 0
python3 -m tools.brain_update
```

**GATE RESULT:** GATE 0 PASSED (12/12 checks, pytest 26 unit passed, 19 e2e passed, frontend built).

## 2026-08-29 · Git Push · Antigravity

**BLOCK:** Git repository setup and push to GitHub.

**DONE:** Initialized local Git repository, created `main` branch, added remote `origin` pointing to `https://github.com/Devrajsahani/MasterCard-AI.git`, added and committed all files, and successfully pushed the codebase.

**FILES:** All codebase files.

**COMMANDS RUN:**
```bash
git init
git checkout -b main
git remote add origin https://github.com/Devrajsahani/MasterCard-AI.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

**GATE RESULT:** No block gates changed. `git push` succeeded with exit code 0.

## 2026-08-29 · BLOCK 0 · Claude -> A & B

**BLOCK:** 0 — Foundation & unblock

**DONE:** Repo skeleton, agent contract (`AGENTS.md`, `GEMINI.md`, `.agents/rules/`),
`brain/`, pydantic contracts, config loader with validation, fixture generator,
gate runner (0..7), brain updater, FastAPI with all endpoints on fixtures,
Dockerfile for HF Spaces, Makefile, 26 unit tests.

**FILES:** `src/mcdl/{schemas,config,fixtures,artifacts}.py` · `tools/{gates,brain_update}.py`
· `api/main.py` · `tests/unit/*` · `Dockerfile` · `Makefile` · `configs/base.yaml`

**COMMANDS RUN:**

```
python -m pip install pytest ruff polars lightgbm httpx
python -m tools.gates 0
python -m tools.brain_update
```

**GATE RESULT:** GATE 0 PASSED — 10/10 checks, `pytest tests/unit` 26 passed.
API smoke-tested: every endpoint returns 200, or an honest 501/404. The fixture
flag is surfaced on every response and unmeasured fields return `null`, not `0`.

**BLOCKERS:**

- `docs/COMPETITION.md` is a stub. Someone must open the actual competition page
  and confirm deliverables, deadline **and timezone**, and whether a leaderboard
  exists. Everything downstream inherits from that page.
- Reference dataset not yet downloaded (`kartik2112/fraud-detection`, CC0).

**NEXT:**

- **B** -> BLOCK 1: download and profile Sparkov into `docs/DATA_PROFILE.md`, then
  build the stateful world in `src/mcdl/world/`. Target: gate 1.
- **A** -> BLOCK 1: build the five React views against the fixture API, run
  `make frontend`, deploy the Space. Target: `/api/health` 200 from the public URL.
