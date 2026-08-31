# KIRA — Final Research Expansion Master Plan
## Revised Implementation Plan — PLANNING ONLY, NOT IMPLEMENTED

> **BASELINE FROZEN.** `run_tiny_s20260827_193f7897_40997ab` at commit `40997ab`.
> Nothing in this plan touches the verified baseline.

---

## EXECUTION PHASES (HARD GATES — NO PHASE STARTS AUTOMATICALLY)

```
PHASE 1: CPU-only implementation + unit tests   → STOP FOR REVIEW
PHASE 2: GPU notebook configuration             → STOP FOR REVIEW
PHASE 3: GPU experiment execution               → STOP FOR REVIEW
PHASE 4: Master comparison + final report       → STOP FOR REVIEW
```

Each phase requires explicit written approval before the next begins.

---

## A. Current Repository Audit

### What exists and is verified (FROZEN — DO NOT TOUCH)

| Path | Status |
| :--- | :---: |
| `src/mcdl/` (world, features, blue, red, loop, evaluation, artifacts, schemas, config, pipeline) | ✅ Frozen |
| `artifacts/run_tiny_s20260827_193f7897_40997ab/` (22 artifacts, SHA-256 signed) | ✅ Frozen |
| `brain/CLAIMS.md` | ✅ Frozen |
| `docs/LIMITATIONS.md` | ✅ Frozen |
| `brain/HANDOFF.md` | ✅ Frozen |
| `tests/unit/`, `tests/invariants/`, `tests/e2e/` | ✅ Frozen (125 passing) |
| `api/main.py` | ✅ Frozen |
| `frontend/src/` | ✅ Frozen |

### What does NOT exist yet (research expansion targets)

- `src/mcdl/research/` — new sub-package (additive, no interference)
- `notebooks/kaggle/03_research_expansion.ipynb` — new orchestrating notebook
- `research_runs/` — new top-level directory, gitignored for binary artifacts
- `docs/research/RESEARCH_EXPANSION.md` — post-run narrative
- `tests/unit/research/` — unit tests for research modules

---

## B. Exact Files to Create

```
# New sub-package — pure additive, zero imports from existing tests
src/mcdl/research/
  __init__.py                 # exports: budget, checkpoint, all experiment runners
  budget.py                   # BudgetContext, GlobalBudget, StageTimeoutError
  checkpoint.py               # save/load per-stage checkpoints + RNG state
  provenance.py               # dataset hash, namespace tagging, access-date recording
  environment.py              # GPU/CPU detection, memory estimation, profile selection
  l3_fidelity.py              # P1–P4 ratio computation (synthetic vs real Sparkov)
  c2st.py                     # binary discriminator (LightGBM/LR), AUC + CI
  tstr.py                     # TSTR + TRTR evaluation, same split discipline
  graph.py                    # causal graph construction + GraphSAGE-style training
  graph_leakage_audit.py      # temporal/neighbor/label/post-cutoff leakage checks
  rl_red.py                   # PPO-lite RL Red challenger
  generator_comparison.py     # CTGAN/VAE generator + L1/L2/L3/C2ST acceptance gate
  llm_planner.py              # proposal-only LLM → JSON → KIRA validator wrapper
  continual.py                # lightweight incremental replay ablation
  label_delay.py              # fixed_7d vs empirical-delay research mode
  comparison.py               # master comparison table builder

# Orchestrating notebook
notebooks/kaggle/
  03_research_expansion.ipynb

# Research artifact store
research_runs/
  .gitkeep
  README.md                   # schema + recovery docs
  global_config.json          # all configurable limits (see Section I)

# Documentation
docs/research/
  RESEARCH_EXPANSION.md       # post-run narrative (filled after execution)

# Tests
tests/unit/research/
  __init__.py
  test_budget.py
  test_checkpoint.py
  test_provenance.py
  test_environment.py
  test_l3_fidelity.py
  test_c2st.py
  test_tstr.py
  test_graph_leakage_audit.py
  test_rl_red_contracts.py
  test_generator_acceptance.py
  test_llm_sandbox.py
  test_comparison.py

# Minor additions (no modifications to existing content)
.gitignore                    # append: research_runs/**/*.pkl, research_runs/**/*.bin, research_runs/**/*.ckpt
pyproject.toml                # append [project.optional-dependencies] research = [...]
```

---

## C. Files That Must Remain Completely Untouched

```
src/mcdl/__init__.py
src/mcdl/artifacts.py
src/mcdl/blue/
src/mcdl/config.py
src/mcdl/evaluation/
src/mcdl/features/
src/mcdl/fixtures.py
src/mcdl/loop/
src/mcdl/pipeline.py
src/mcdl/red/
src/mcdl/schemas.py
src/mcdl/world/
artifacts/run_tiny_s20260827_193f7897_40997ab/   (ENTIRE DIRECTORY)
brain/CLAIMS.md
brain/HANDOFF.md
docs/LIMITATIONS.md
tests/unit/test_*.py          (all existing tests)
tests/invariants/
tests/e2e/
api/
frontend/
Makefile
configs/
```

> [!CAUTION]
> Any edit to the above must be explicitly justified, documented in `brain/DECISIONS.md`, and approved before implementation.

---

## D. Dependency Graph

```
S-00 (Environment & Safety Check)
  └──→ S-01 (Baseline Load & SHA-256 Integrity)
         │
         ├──→ [INDEPENDENT AFTER S-01]
         │       S-02 (L3 P1–P4 Fidelity)
         │       S-03 (C2ST Discriminator)
         │       S-04 (TSTR / TRTR Transfer)
         │       S-05 (Graph Preprocessing + Leakage Audit)
         │
         └──→ WAVE-1 PARTIAL REPORT
                     │
                     ▼ [EXPLICIT APPROVAL REQUIRED]
                     │
              G-01 (GraphSAGE Training)
              G-02 (Extended CoEvo 6R)
              G-03 (RL Red Challenger)
              G-04 (Generator CTGAN/VAE)
              G-05 (LLM Planner + CL Ablation + Label-Delay)
              G-06 (Master Comparison)

Notes:
- G-04 uses S-02 (L3), S-03 (C2ST), S-04 (TSTR) as EVALUATION EVIDENCE only.
  It does not require them to complete before generator training begins.
- G-05 (LLM Planner) needs G-02/G-03 context for attack grammar, but can run
  on baseline world context if GPU experiments are skipped.
- G-06 reads status.json from ALL stages (completed, failed, skipped — all included).
```

---

## E. CPU / GPU Separation

### Wave 1 — CPU Only (No Training of Neural/Large Models)

| Stage | Compute | Training? |
| :---: | :---: | :---: |
| S-00 | CPU | ❌ |
| S-01 | CPU | ❌ |
| S-02 (L3) | CPU | ❌ |
| S-03 (C2ST with LightGBM discriminator) | CPU | ✅ (tabular, lightweight) |
| S-04 (TSTR with LightGBM) | CPU | ✅ (tabular, lightweight) |
| S-05 (Graph preprocessing + leakage audit only) | CPU | ❌ |

### Wave 2 — GPU Preferred (Training-Heavy)

| Stage | Compute | Training? | GPU Required? |
| :---: | :---: | :---: | :---: |
| G-01 (GraphSAGE) | GPU preferred | ✅ | Preferred, not mandatory |
| G-02 (Extended CoEvo 6R) | CPU | ✅ (LightGBM) | ❌ |
| G-03 (RL Red) | GPU preferred | ✅ | Preferred, not mandatory |
| G-04 (CTGAN/VAE) | GPU strongly preferred | ✅ | Strongly preferred |
| G-05 (LLM/CL/Label-Delay) | CPU + API | Mixed | ❌ |
| G-06 (Master Comparison) | CPU | ❌ | ❌ |

---

## F. Wave 1 Detailed Plan (CPU, ≤ 90 minutes total)

### S-00 · Environment & Safety Check (10 min limit)
```
Actions:
1. Clone public GitHub repo → verify commit hash == 40997ab
2. pip install -e ".[research]" → print version matrix
3. Detect accelerator: GPU type, count, VRAM, CPU cores, RAM
4. Compute baseline provenance SHA-256 → store as BASELINE_PROVENANCE_HASH
5. Create research_runs/<session_id>/ directory tree
6. Write global_config.json with all resource limits (see Section I)
7. Check for research_runs/STOP kill-switch file → abort if present
8. Confirm Sparkov dataset mounted / downloadable → record dataset SHA-256

Output: research_runs/S-00/status.json, environment_profile.json
Termination: Abort if SHA-256 mismatch OR baseline missing OR STOP file present
```

### S-01 · Baseline Load & Integrity (5 min limit)
```
Actions:
1. Load all 22 artifacts from run_tiny_s20260827_193f7897_40997ab/
2. Re-verify each artifact SHA-256 against provenance.json → must match 22/22
3. Snapshot champion metrics into champion_snapshot.json
4. Load verified champion LightGBM model in read-only mode
5. Load world transactions as read-only reference dataset
6. ASSERT: baseline_run_id == "run_tiny_s20260827_193f7897_40997ab"

Termination: ABORT ENTIRE NOTEBOOK if any SHA-256 fails.
Output: research_runs/S-01/champion_snapshot.json, status.json
```

### S-02 · L3 Behavioral Fidelity P1–P4 (25 min limit)
```
Actions:
1. Load KIRA synthetic transactions (from S-01 world)
2. Load Sparkov reference dataset (REAL_WORLD namespace, CC0)
3. Compute split denominator: split Sparkov in half (time or customer-based)
   Record which split method was used
4. P1 — inter-event timing ratio:
     synthetic_interarrival_dist vs real_interarrival_dist
     metric: KL divergence + ratio to same-split real variability
5. P2 — burst structure ratio:
     burstiness coefficient (σ/μ of inter-event times) per customer segment
     ratio: synthetic_burstiness / real_burstiness
6. P3 — multi-account motif ratio:
     shared-device transaction subgraph density
     shared-merchant fan-out degree distribution
     ratio: synthetic_motif_density / real_motif_density
7. P4 — velocity-trigger rate ratio:
     fraction of transactions exceeding velocity thresholds
     ratio: synthetic_trigger_rate / real_trigger_rate
8. For each Px: record synthetic value, real value, ratio, N, CI, split method
9. If real denominator not directly comparable → mark NOT COMPARABLE (do not invent)

Output: research_runs/RES-L3/metrics.json (ratios, CIs, sample counts)
```

### S-03 · C2ST Discriminator (20 min limit)
```
Actions:
1. Construct balanced dataset: synthetic txns (label=0) + Sparkov real txns (label=1)
2. Feature alignment: use only features available in both datasets (log-transform amounts,
   inter-event timing, merchant category dummies, hour-of-day)
3. Train/validation/test split (60/20/20, stratified)
4. Train LightGBM binary discriminator
5. Compute AUC on held-out test set + 95% bootstrap CI (1000 resamples)
6. Record feature importances (top 10)
7. Interpretation table:
     AUC ~0.50: hard to distinguish (good fidelity signal)
     AUC > 0.80: easy to distinguish (poor fidelity)
8. NEVER claim "realistic" merely because AUC < threshold

Output: research_runs/RES-C2ST/metrics.json (AUC, CI, N_synthetic, N_real, feature_importances)
```

### S-04 · TSTR / TRTR (20 min limit)
```
Actions:
TSTR arm:
1. Train Blue model on KIRA synthetic data (same feature spec, same causal split)
2. Evaluate on Sparkov real data test set (REAL_WORLD namespace only)
3. Metrics: PR-AUC, ROC-AUC, FPR, ECE, Brier

TRTR arm (baseline comparison, where feasible):
4. Train Blue model on Sparkov training split
5. Evaluate on Sparkov real data test set
6. Same metrics

Record both arms side by side + delta.
DO NOT mix real data into primary KIRA Blue training.
Dataset used for TRTR must stay in REAL_WORLD namespace only.

Output: research_runs/RES-TSTR/metrics.json (TSTR arm, TRTR arm, delta, N per arm)
```

### S-05 · Graph Preprocessing + Causal Leakage Audit (15 min limit)
```
Actions:
1. Build entity registry from world transactions:
     customer_id, merchant_id, device_id, agent_id, txn_id
2. Build adjacency lists: customer→merchant, customer→device, agent→customer
3. Assign chronological timestamps to all edges
4. Run causal leakage audit (see Section Q):
     check no future edge exists in the train-time graph
     check no future node state propagates
     check no post-cutoff neighbor aggregation
     check no label leakage via graph structure
5. Record: N nodes per type, N edges per type, temporal gap statistics
6. Output: graph_manifest.json (topology stats + leakage audit result = PASS/FAIL)
7. If FAIL: mark G-01 GraphSAGE as BLOCKED_LEAKAGE_AUDIT

Output: research_runs/S-05/graph_manifest.json, leakage_audit.json
NOTE: NO TRAINING in this stage. Graph construction only.
```

### Wave-1 Partial Report
```
After S-02..S-05: auto-generate research_runs/WAVE1_REPORT.md
Contents:
- Environment profile (accelerator type, RAM, etc.)
- Baseline integrity: PASS/FAIL
- L3 ratios: P1..P4
- C2ST AUC: value + CI
- TSTR vs TRTR delta
- Graph leakage audit: PASS/FAIL
- Stage completion summary table
- Preliminary KEEP/DISCARD signals

STOP. Print to notebook output. Await explicit approval.
```

---

## G. Wave 2 Detailed Plan (GPU, ≤ 8 hours total)

### Activation Gate
```python
RUN_GPU_RESEARCH = os.environ.get("RUN_GPU_RESEARCH", "false").lower() == "true"
if not RUN_GPU_RESEARCH:
    print("WAVE 2 SKIPPED — set RUN_GPU_RESEARCH=true to enable")
    sys.exit(0)
```

### G-01 · GraphSAGE Relational Challenger (60 min limit)
```
Pre-condition: leakage_audit.json from S-05 must == PASS
Actions:
1. Build time-causal graph snapshots for train/valid/test chronological windows
2. Node features: tabular features for each entity type at snapshot time t
3. GraphSAGE: 2-layer message passing, mean aggregation, 64-dim hidden
4. Train on train split, tune threshold on valid split
5. Evaluate on test split: PR-AUC, ROC-AUC, FPR, ECE, Brier
6. Attack evaluation on same Blue scorer: ASR@1/5/20/100, held-out ASR, hidden ASR
7. Latency benchmark: 200 requests, P50/P95/P99
8. Specific analysis: shared device, fan-out, coordinated accounts, camouflage, swarm
9. Compare vs LightGBM champion on IDENTICAL split + IDENTICAL attack protocol

Output: research_runs/RES-GRAPH/ (metrics.json, model.pkl, latency.json)
```

### G-02 · Extended Co-Evolution 6 Rounds (90 min limit)
```
Pre-condition: LightGBM champion from S-01 champion_snapshot.json
Actions:
1. Extend existing pipeline for 6 rounds using IDENTICAL evaluation protocol
2. Track per-round: ASR, held-out ASR, hidden-family ASR, MED, retention, plasticity
3. Track: promotion/rollback events, attack diversity per round, failure taxonomy
4. Convergence detection: stop early if:
     |ASR[r] - ASR[r-1]| < 0.01 for 2 consecutive rounds
     OR metrics plateau
     OR oscillation (ASR[r] > ASR[r-2] by > 10%)
5. Adaptation cost: wall-clock + model-fit count per round

Output: research_runs/RES-COEVO6/ (round_metrics.json, convergence_analysis.json)
```

### G-03 · RL Red Challenger (60 min limit)
```
Pre-condition: LightGBM champion from S-01
Actions:
1. Define RL environment (see Section R for full spec)
2. Train PPO-lite: max 500 episodes, max 20 steps/episode
3. Same mutable fields as heuristic Red, same physical constraints, same query budget
4. Compare: RL Red vs heuristic adaptive Red:
     ASR@1/5/20/100, queries-to-evasion, MED, novelty, validity, compute cost
5. Record: training curve, episode rewards, constraint violations (must = 0)

Output: research_runs/RES-RL-RED/ (metrics.json, rl_policy.pkl, training_curve.json)
```

### G-04 · Generator Comparison — CTGAN/VAE (60 min limit)
```
Pre-condition: L3 (S-02), C2ST (S-03), TSTR (S-04) results available as evidence
Actions:
1. Train ONE generator (CTGAN preferred, VAE as fallback, diffusion-lite as last resort)
2. Do NOT train multiple generators unless first result clearly warrants it
3. Generate MAX_GENERATOR_SAMPLES=5000 synthetic transactions
4. Run FULL acceptance gate pipeline (see Section S):
     L1: physics validity (must be 0 violations)
     L2: KS statistics vs real (same threshold as KIRA baseline ≤ 0.25)
     L3: P1–P4 ratios vs S-02 real benchmark
     C2ST: AUC of discriminator trained on generator output vs real
     TSTR: train on generator output → test on Sparkov real
     Causal consistency: no label leakage, no future feature
5. Record: generated_N, training_time, inference_time, memory, invalid_rate, all fidelity metrics

Output: research_runs/RES-GEN/ (metrics.json, acceptance_gate.json)
```

### G-05 · Optional Research Track (30 min limit total)
```
LLM Planner (if API key available):
- see Section T for full sandbox contract
- max 50 API calls, max 20-min time limit

Continual Learning Ablation:
- see Section U for comparison design
- max 20-min time limit

Adaptive Label Delay Research Mode:
- see Section V for research mode design
- max 15-min time limit

Each substage writes its own status.json.
If API unavailable → mark SKIPPED_API_UNAVAILABLE
If time budget exhausted → mark INCOMPLETE
```

### G-06 · Master Comparison (10 min limit)
```
Actions:
1. Re-verify baseline SHA-256 (second verification — see Section A)
2. Load all status.json and metrics.json from RES-L3, RES-C2ST, RES-TSTR,
   RES-GRAPH, RES-COEVO6, RES-RL-RED, RES-GEN, RES-LLM, RES-CL, RES-LD
3. Build master comparison table (see Section W)
4. Apply decision rules (see Section X)
5. Write MASTER_COMPARISON.json + FINAL_RESEARCH_REPORT.md
6. NEVER populate with fabricated values — null for any unexecuted stage

Output: research_runs/MASTER_COMPARISON.json, FINAL_RESEARCH_REPORT.md
```

---

## H. Per-Stage Wall-Clock Budgets

### Wave 1 (total ≤ 90 minutes)

| Stage | Limit | Cumulative Max |
| :---: | :---: | :---: |
| S-00 | 10 min | 10 min |
| S-01 | 5 min | 15 min |
| S-02 | 25 min | 40 min |
| S-03 | 20 min | 60 min |
| S-04 | 20 min | 80 min |
| S-05 | 10 min | 90 min |

### Wave 2 (total ≤ 8 hours)

| Stage | Limit | Cumulative Max |
| :---: | :---: | :---: |
| G-01 | 60 min | 60 min |
| G-02 | 90 min | 150 min |
| G-03 | 60 min | 210 min |
| G-04 | 60 min | 270 min |
| G-05 | 30 min | 300 min |
| G-06 | 10 min | 310 min (5h 10m) |
| **Safety buffer** | **170 min** | **480 min (8h)** |

---

## I. Per-Stage Memory & Compute Limits (`global_config.json`)

```json
{
  "resource_limits": {
    "MAX_TRANSACTIONS":        50000,
    "MAX_ATTACKS":             200,
    "MAX_QUERIES":             100,
    "MAX_GRAPH_NODES":         10000,
    "MAX_GRAPH_EDGES":         100000,
    "MAX_MODEL_FITS":          12,
    "MAX_SHAP_SAMPLES":        500,
    "MAX_GENERATOR_SAMPLES":   5000,
    "MAX_LLM_CALLS":           50,
    "MAX_RL_EPISODES":         500,
    "MAX_RL_STEPS_PER_EPISODE": 20,
    "MAX_COEVO_ROUNDS":        6,
    "MAX_MEMORY_GB":           24,
    "MAX_GPU_MEMORY_GB":       14,
    "C2ST_BOOTSTRAP_RESAMPLES": 1000,
    "TSTR_MAX_TRAIN_SAMPLES":  20000,
    "GRAPH_EMBEDDING_DIM":     64,
    "GRAPH_SAGE_LAYERS":       2
  },
  "wave_limits": {
    "WAVE_1_MAX_SECONDS": 5400,
    "WAVE_2_MAX_SECONDS": 28800,
    "GLOBAL_MAX_SECONDS": 34200
  }
}
```

---

## J. Exact GPU Requirements

### Detection protocol (runs in S-00)

```python
import torch, psutil, platform

env = {
    "gpu_available": torch.cuda.is_available(),
    "gpu_count": torch.cuda.device_count(),
    "gpu_type": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    "gpu_vram_gb": torch.cuda.get_device_properties(0).total_memory / 1e9
                   if torch.cuda.is_available() else 0,
    "cpu_cores": os.cpu_count(),
    "ram_gb": psutil.virtual_memory().total / 1e9,
    "platform": platform.platform(),
}
```

### Stage GPU policy

| Stage | GPU Absent Action |
| :---: | :--- |
| G-01 (GraphSAGE) | Fall back to CPU if VRAM ≥ 0 (graph is small) BUT flag `CPU_FALLBACK` |
| G-02 (CoEvo6) | GPU not needed; runs on CPU by design |
| G-03 (RL Red) | If no GPU → mark `SKIPPED_GPU_UNAVAILABLE`, log, continue |
| G-04 (Generator) | If no GPU → reduce MAX_GENERATOR_SAMPLES to 1000, flag `CPU_FALLBACK_REDUCED` |
| G-05 (LLM) | CPU + API only; GPU not used |

> [!WARNING]
> Never silently fall back to an unbounded CPU run for any GPU-preferred stage. Always flag the condition explicitly in status.json.

---

## K. Exact Termination Conditions

Every stage is wrapped in:

```python
class BudgetContext:
    """Raises StageTimeoutError when wall-clock limit is reached."""
    def __init__(self, stage_id: str, limit_seconds: int): ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb):
        if timeout: raise StageTimeoutError(stage_id, elapsed)

# Kill-switch check at every stage boundary
def check_kill_switch():
    if Path("research_runs/STOP").exists():
        checkpoint_current_state()
        write_status("KILLED")
        raise SystemExit("KILL SWITCH ACTIVATED")
```

A stage terminates when:
1. Stage wall-clock limit reached → `INCOMPLETE`
2. Global wall-clock limit reached → `INCOMPLETE`, abort notebook
3. `research_runs/STOP` file detected → `KILLED`
4. Resource limit violated (OOM, MAX_MODEL_FITS exceeded) → `FAILED`
5. Baseline SHA-256 verification fails → `ABORT_TAMPER`
6. Experiment completes naturally → `COMPLETE`

---

## L. Checkpoint Strategy

### Model checkpointing (training stages)

```python
# Called after every training epoch/round/episode
checkpoint = {
    "stage_id": "G-01",
    "experiment_id": "RES-GRAPH",
    "epoch": current_epoch,
    "model_state": model.state_dict(),          # serialized via torch.save / joblib
    "optimizer_state": optimizer.state_dict(),  # for RL/neural stages only
    "rng_state": {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state().tolist() if torch.cuda.is_available() else None
    },
    "metrics_so_far": metrics_dict,
    "config": config_dict,
    "timestamp": datetime.utcnow().isoformat()
}
# Write atomically: write to .tmp then rename
```

### Non-model stages (L3, C2ST, TSTR)
- Write intermediate DataFrames as Parquet files after each major computation
- status.json written as final action of every stage (not during)

### Recovery: if a stage is interrupted mid-training
- Re-entry: load most recent checkpoint, resume from last epoch/round/episode
- If no checkpoint exists: restart from scratch (within time limit)
- If time limit reached on restart: mark `INCOMPLETE`, continue to next stage

---

## M. Kill-Switch Strategy

### Mechanism

```
research_runs/STOP      ← plain empty file
```

When this file is detected at any `check_kill_switch()` call:
1. Finish current atomic write operation
2. Checkpoint current stage state
3. Write `status.json` with `"status": "KILLED"`
4. Write `research_runs/ABORT_REASON.txt` with timestamp
5. Raise `SystemExit` → notebook terminates

### Trigger points

`check_kill_switch()` is called:
- At the start of every stage
- After every round (CoEvo6)
- After every episode (RL Red)
- After every 100 generator samples
- At every epoch boundary (GraphSAGE)

### Global timeout (automatic kill)

```python
GLOBAL_DEADLINE = session_start_time + timedelta(seconds=GLOBAL_MAX_SECONDS)

def global_timeout_check():
    if datetime.utcnow() >= GLOBAL_DEADLINE:
        # Same flush + checkpoint + abort sequence as kill-switch
        raise GlobalTimeoutError()
```

---

## N. Dataset Provenance Requirements

Every dataset used by research experiments records:

```json
{
  "dataset_name": "Sparkov Credit Card Transactions Fraud Detection",
  "source_platform": "Kaggle",
  "source_url": "https://kaggle.com/datasets/kartik2112/fraud-detection",
  "license": "CC0 1.0 Universal",
  "provenance": "Sparkov Data Generator (Brandon Harris)",
  "access_date": "2026-08-31",
  "sha256_content_hash": "<computed at runtime>",
  "feature_mapping": {
    "amount": "log_amount",
    "category": "merchant_category",
    "trans_date_trans_time": "event_timestamp"
  },
  "namespace": "REAL_WORLD",
  "sample_count": 1296675,
  "positive_count": 7506,
  "split_method": "temporal_customer"
}
```

Namespaces:
- `SYNTHETIC` — KIRA world generator output
- `REAL_WORLD` — Sparkov, ULB, or any external permitted dataset
- `INFERRED` — derived features that mix both (must be flagged explicitly)

Never mix namespaces silently. A feature derived from REAL_WORLD data cannot appear in SYNTHETIC training without explicit documentation.

---

## O. Experiment Identity / Hash Strategy

```json
{
  "experiment_id": "RES-GRAPH-20260831T030215Z",
  "baseline_run_id": "run_tiny_s20260827_193f7897_40997ab",
  "git_commit": "fb99a17",
  "experiment_config_hash": "<sha256 of config.json>",
  "dataset_hash": "<sha256 of Sparkov CSV or KIRA world transactions>",
  "environment_hash": "<sha256 of pip freeze output>",
  "seed": 20260827,
  "created_at": "2026-08-31T03:02:15Z",
  "runtime_seconds": null,
  "python_version": "3.14.0",
  "lightgbm_version": "4.x.x",
  "torch_version": "2.x.x"
}
```

Experiment IDs are generated as `RES-<NAME>-<UTC_ISO_COMPACT>` and are stable for reproduction.

---

## P. Statistical & Uncertainty Strategy

### Required for every reported metric

```json
{
  "metric": "c2st_auc",
  "point_estimate": 0.673,
  "n_samples": 4200,
  "n_positive": 1400,
  "n_negative": 2800,
  "bootstrap_ci_95": [0.641, 0.703],
  "bootstrap_n_resamples": 1000,
  "standard_error": 0.016
}
```

### Automatic flags

| Condition | Flag |
| :--- | :---: |
| N_positive < 30 | `LOW_SAMPLE` |
| CI width > 0.15 | `HIGH_VARIANCE` |
| N_total < 100 | `UNDERPOWERED` |
| point_estimate within CI margin of null hypothesis | `INCONCLUSIVE` |

> [!IMPORTANT]
> A result flagged `UNDERPOWERED` or `INCONCLUSIVE` can never receive decision `KEEP`. Maximum decision is `INCONCLUSIVE`.

---

## Q. GraphSAGE Causal Leakage Controls

### What must be checked (leakage_audit.py)

```
1. TEMPORAL LEAKAGE
   For every edge (u → v) in graph G(train):
   edge.timestamp <= max_train_timestamp
   ASSERTION: no future edge exists in training graph

2. NEIGHBOR FEATURE LEAKAGE
   For node v at prediction time t:
   all neighbor features must be from timestamp <= t
   ASSERTION: no neighbor feature from t+1..T

3. LABEL LEAKAGE
   Graph structure must not encode the fraud label of any test transaction
   ASSERTION: is_fraud not used as edge weight or node attribute in training graph

4. POST-CUTOFF AGGREGATION LEAKAGE
   Aggregated neighbor statistics (mean, sum, max) computed at time t
   must not include events from t+1..T
   ASSERTION: rolling aggregation window is strictly t-window <= ts < t

5. TRAIN/VALID/TEST CHRONOLOGICAL ISOLATION
   train_cutoff < valid_cutoff < test_cutoff
   No transaction from valid/test window appears in train graph
```

### Audit output

```json
{
  "audit_passed": true,
  "checks": {
    "temporal_edge": {"passed": true, "violations": 0},
    "neighbor_feature": {"passed": true, "violations": 0},
    "label": {"passed": true, "violations": 0},
    "post_cutoff_aggregation": {"passed": true, "violations": 0},
    "chronological_isolation": {"passed": true, "violations": 0}
  }
}
```

If `audit_passed == false` → G-01 GraphSAGE is **BLOCKED**. Do not train.

---

## R. RL Red State / Action / Reward Design

### State space
```python
state = {
    # Attacker's observable context
    "attack_family": AttackFamily,              # one-hot encoded
    "current_variant_features": np.ndarray,    # mutable feature values only
    "queries_used": int,                       # 0..MAX_QUERIES
    "queries_remaining": int,
    "last_score": float,                       # Blue's last fraud probability
    "last_decision": Decision,                 # ALLOW / STEP_UP / BLOCK
    "mutation_history": np.ndarray,            # rolling last-k mutations (k=5)
}
# State dimension: ~50 floats
```

### Action space
```python
# Discrete action: which mutable field to mutate + by how much
# Constrained to exactly the same mutable fields as heuristic Red
actions = [
    (field_id, mutation_delta)
    for field_id in MUTABLE_FIELDS
    for mutation_delta in DELTA_BUCKETS  # e.g. {-2.0, -1.0, -0.5, +0.5, +1.0, +2.0}
]
# Total actions: len(MUTABLE_FIELDS) × len(DELTA_BUCKETS)
```

### Reward function
```python
def reward(prev_score, new_score, decision, is_valid, query_cost):
    evasion_bonus = 10.0 if decision == Decision.ALLOW else 0.0
    detection_penalty = -1.0 if decision == Decision.BLOCK else 0.0
    score_progress = (prev_score - new_score) * 2.0  # reward score reduction
    invalidity_penalty = -5.0 if not is_valid else 0.0
    query_cost_penalty = -0.1 * query_cost
    return evasion_bonus + detection_penalty + score_progress + invalidity_penalty + query_cost_penalty
```

### Constraints (same as heuristic Red — NON-NEGOTIABLE)
- Immutable fields: `txn_id`, `customer_id`, `merchant_id`, `is_agent_initiated`, timestamps
- Physical validity: credit limit, non-negative amounts, balance consistency
- Query budget: total queries per episode ≤ MAX_QUERIES
- Any constraint violation: immediate episode termination, penalty reward

---

## S. Generator Acceptance Tests (Full Pipeline)

A generated dataset is only considered for KEEP/SPECIALIST after passing ALL:

```
ACCEPTANCE GATE
│
├── L1: Physics Validity
│   PASS condition: 0 violations (credit limit, non-negative, balance, coordinate bounds)
│   FAIL → DISCARD immediately
│
├── L2: Statistical Similarity
│   PASS condition: per-column KS statistic ≤ 0.25 for all columns
│   FAIL → DISCARD
│
├── L3: Behavioral Fidelity
│   PASS condition: P1..P4 ratios all ≤ 2.0 (within 2× real variability)
│   FAIL → DISCARD (better marginals but broken behavior)
│
├── C2ST: Discriminability
│   PASS condition: discriminator AUC ≤ 0.70 (hard to distinguish from real)
│   NOTE: lower AUC = better (harder to distinguish)
│   FAIL → DISCARD
│
├── TSTR: Transfer Learning
│   PASS condition: TSTR PR-AUC ≥ 0.60 on Sparkov real test set
│   FAIL → DISCARD
│
└── Causal Consistency Check
    PASS condition: no future label features detected
    FAIL → DISCARD
```

If generator passes all → decision eligible for KEEP AS SPECIALIST.
If generator fails any gate → DISCARD (record exact failure gate + metric).

---

## T. LLM Planner Sandbox Contract

### What LLM may do
```
INPUT TO LLM:
- Attack family description (text)
- Available mutable fields + allowed ranges (text)
- Current transaction feature values (anonymized, no real PII)
- Query budget remaining

OUTPUT FROM LLM:
- Structured JSON attack proposal (see schema below)
```

### LLM attack proposal schema
```json
{
  "proposed_mutations": {
    "field_name": "new_value"
  },
  "rationale": "string",
  "estimated_evasion_probability": 0.0
}
```

### What LLM may NOT do (enforced by wrapper, not by trust)
```
❌ Modify immutable fields
❌ Access future labels
❌ Access hidden evaluation sets
❌ Decide whether attack succeeded
❌ Issue additional queries beyond budget
❌ Bypass KIRA validation
```

### Validation pipeline (deterministic, not LLM-controlled)
```
LLM JSON proposal
→ JSON schema validation (Pydantic model)
→ immutable field check (reject if any immutable field included)
→ KIRA mutability mask (reject if out-of-range)
→ physics validation (L1 checks)
→ Blue scoring (1 query counted toward budget)
→ result recorded
```

### Metrics
```
proposal_acceptance_rate     (% proposals passing schema + mask validation)
valid_attack_rate            (% proposals passing L1 physics)
novelty                      (fraction of proposals unlike existing attack library)
asr                          (% attacks that achieved ALLOW decision)
query_efficiency             (evasions per query)
api_cost_usd                 (recorded per call)
latency_per_call_ms
```

If API key absent or cost too high → `SKIPPED_API_UNAVAILABLE`

---

## U. Continual Learning Comparison Design

### Baseline (existing KIRA mechanism)
```
Prioritized replay buffer
→ challenger training on failure-weighted evasion history
→ multi-objective promotion gate
→ automated rollback on regression
```

### Treatment (one lightweight alternative)
```
Elastic Weight Consolidation (EWC) OR
Incremental LGBM warm-start from previous champion model
(choose based on implementation cost at execution time)
```

### Evaluation metrics
```
retention            (GR = held-out ASR improvement retention)
backward_transfer    (ASR on round-r-1 attacks after round-r training)
plasticity           (ability to learn new attack families)
adaptation_cost_s    (wall-clock seconds per round)
memory_mb            (peak memory usage)
n_model_fits         (total model training calls)
```

### Decision criterion
If treatment retention ≤ baseline retention: → **DISCARD**
If treatment has lower adaptation_cost AND comparable retention: → **KEEP AS SPECIALIST**

---

## V. Adaptive Label Delay Research Mode

### Existing (FROZEN — do not touch)
```python
LABEL_DELAY_SECONDS = 604800  # 7-day fixed chargeback lag
# In src/mcdl/features/spec.py — DO NOT MODIFY
```

### Research mode (isolated, additive only)
```python
# In src/mcdl/research/label_delay.py only

class EmpiricalDelayMode:
    """
    Simulates variable chargeback delay drawn from a parameterized distribution.
    Does NOT modify the feature spec or the submission baseline.
    """
    def sample_delay(self, txn_amount: float, archetype: str) -> int:
        # Returns delay_seconds drawn from fitted distribution
        # e.g. Weibull(alpha=2.3, beta=604800) for realistic chargeback timing
        ...
```

### Experiment protocol
```
ARM A: fixed_7d (existing KIRA semantics — read-only reference)
ARM B: empirical_delay (research mode only)

Measure per arm:
- feature availability times
- label availability distribution
- PR-AUC, FPR, ECE
- leakage check: zero future label reads confirmed
- delay distribution parameters

Record delta(ARM_B − ARM_A) for each metric.
```

---

## W. Master Comparison Table Design

```json
{
  "baseline_run_id": "run_tiny_s20260827_193f7897_40997ab",
  "comparison_timestamp": "2026-08-31T...",
  "baseline_sha256_verified": true,
  "components": [
    {
      "component": "L3 Behavioral Fidelity",
      "stage_id": "S-02",
      "status": "COMPLETE | INCOMPLETE | SKIPPED | FAILED",
      "baseline": {"p1": null, "p2": null, "p3": null, "p4": null},
      "treatment": {"p1": <value>, "p2": <value>, "p3": <value>, "p4": <value>},
      "delta": {...},
      "cost": {"wall_clock_s": <value>, "model_fits": 0},
      "latency": null,
      "adversarial_effect": null,
      "generalization": null,
      "statistical_flags": ["LOW_SAMPLE"],
      "decision": "RESEARCH ONLY | KEEP | DISCARD | INCONCLUSIVE"
    }
  ]
}
```

Table populated only from `metrics.json` files. Null for any unmeasured or failed stage. Never fabricated.

---

## X. KEEP / SPECIALIST / DISCARD Decision Rules

### Universal prerequisites for KEEP or KEEP AS SPECIALIST

All of the following must hold:

1. `status == "COMPLETE"` (not INCOMPLETE, not SKIPPED)
2. Point estimate confidence interval does not include the null hypothesis value
3. Statistical flags do not include `UNDERPOWERED`
4. No causal/temporal leakage detected
5. No constraint violations in any attack evaluation

### Component-specific thresholds

| Component | KEEP condition | KEEP AS SPECIALIST | DISCARD | INCONCLUSIVE |
| :--- | :--- | :--- | :--- | :--- |
| L3 Fidelity | P1..P4 all ≤ 1.5 | 1.5 < ratio ≤ 2.5 on ≥ 1 metric | Any ratio > 3.0 | Cannot compute denominator |
| C2ST | AUC < 0.55 | 0.55 ≤ AUC < 0.70 | AUC > 0.80 | CI overlaps 0.50 |
| TSTR | TSTR PR-AUC ≥ 0.75 | 0.60 ≤ PR-AUC < 0.75 | < 0.50 | CI width > 0.20 |
| GraphSAGE | PR-AUC ≥ champion+0.02 AND heldout-ASR ≤ champion-0.05 | Specialist on one family (e.g. fan-out) | No measurable lift | Delta within CI of zero |
| CoEvo6 | Convergence by R4, stable retention | Partial convergence by R6 | Oscillation, no improvement | Budget exhausted |
| RL Red | ASR@20 > heuristic ASR@20 + 0.05 | ASR within 0.05 but higher novelty | Lower ASR than heuristic | Within 0.02 |
| Generator | Passes all 6 acceptance gates | Passes L1/L2/L3 but marginal C2ST | Fails any gate | Passes gates, but TSTR underpowered |
| LLM Planner | proposal_acceptance_rate > 0.70 | 0.40–0.70 acceptance | < 0.30 acceptance | Budget/API exhausted |
| CL Ablation | retention ≥ 1.1 AND lower cost | retention ≥ 1.0 AND lower cost | retention < 0.95 | retention ≈ 1.0, unclear |

---

## Y. Unit / Invariant / Integration Test Matrix

### Unit tests (run during PHASE 1, pre-execution)

| Test file | Tests |
| :--- | :--- |
| `test_budget.py` | BudgetContext raises on timeout, StageTimeoutError structure, global timeout |
| `test_checkpoint.py` | Save/load round-trip, RNG state preservation, atomic write |
| `test_provenance.py` | Namespace tagging, SHA-256 computation, dataset hash stability |
| `test_environment.py` | GPU detection fallback, memory estimation, profile selection |
| `test_l3_fidelity.py` | P1..P4 ratio computation, NOT_COMPARABLE flag, sample count |
| `test_c2st.py` | AUC range assertion (0..1), CI coverage, feature importance non-null |
| `test_tstr.py` | TSTR PR-AUC is non-null, real data stays in REAL_WORLD namespace |
| `test_graph_leakage_audit.py` | Synthetic future edge → detected, causal edge → passes |
| `test_rl_red_contracts.py` | Immutable field violation → episode terminated, query budget enforced |
| `test_generator_acceptance.py` | L1 violation → DISCARD gate fires, all 6 gates required |
| `test_llm_sandbox.py` | Immutable field in LLM proposal → rejected pre-scoring |
| `test_comparison.py` | Null for failed stages, DISCARD for UNDERPOWERED, no fabrication |

### Invariant tests (post-execution, verify research isolation)

```
invariant_research_isolation.py:
  - baseline SHA-256 unchanged after any research stage
  - research_runs/ contains no files from artifacts/run_tiny_*/
  - no research_runs artifact has been committed to Git without explicit flag
```

### Integration test

```
test_wave1_integration.py:
  - Runs Wave 1 in dry-run mode (max 100 transactions, max 10 attacks)
  - Verifies all status.json files are written
  - Verifies MASTER_COMPARISON.json is parseable JSON with null values for GPU stages
```

---

## Z. Recovery Strategy

| Failure Type | Detection | Recovery |
| :--- | :--- | :--- |
| SHA-256 mismatch | S-01 integrity check | **ABORT ENTIRE NOTEBOOK** |
| Stage timeout | BudgetContext timer | checkpoint + `INCOMPLETE` + continue |
| OOM during training | MemoryError catch | reduce batch/graph size, retry once, then `FAILED` |
| GPU unavailable at G-01 | torch.cuda check | `CPU_FALLBACK` flag + continue with CPU |
| API key missing (LLM) | pre-flight check in S-00 | `SKIPPED_API_UNAVAILABLE` |
| Kill-switch file found | every-stage check | checkpoint + `KILLED` + sys.exit |
| Global timeout | global_deadline check | checkpoint all in-progress stages + sys.exit |
| G-04 Generator fails acceptance | acceptance gate pipeline | `DISCARD` + continue to G-05 |
| G-06 comparison fails | status.json load errors | write `MASTER_COMPARISON_PARTIAL.json` with null rows |
| Network failure (Kaggle clone) | S-00 git check | retry 3× with backoff, then abort |

---

## Final File Structure (Complete)

```
notebooks/kaggle/
  03_research_expansion.ipynb

src/mcdl/research/
  __init__.py
  budget.py
  checkpoint.py
  provenance.py
  environment.py
  l3_fidelity.py
  c2st.py
  tstr.py
  graph.py
  graph_leakage_audit.py
  rl_red.py
  generator_comparison.py
  llm_planner.py
  continual.py
  label_delay.py
  comparison.py

research_runs/
  .gitkeep
  README.md
  global_config.json
  <experiment_id>/
    config.json
    metrics.json
    status.json
    provenance.json
    logs/
    artifacts/

docs/research/
  RESEARCH_EXPANSION.md

tests/unit/research/
  __init__.py
  test_budget.py
  test_checkpoint.py
  test_provenance.py
  test_environment.py
  test_l3_fidelity.py
  test_c2st.py
  test_tstr.py
  test_graph_leakage_audit.py
  test_rl_red_contracts.py
  test_generator_acceptance.py
  test_llm_sandbox.py
  test_comparison.py

# Minor modifications
.gitignore                    (append only)
pyproject.toml                (append [research] extras only)
```

---

## Execution Phase Gates (REPEATED — MANDATORY)

```
PHASE 1: CPU-only implementation + unit tests   → STOP FOR REVIEW
PHASE 2: GPU notebook configuration             → STOP FOR REVIEW
PHASE 3: GPU experiment execution               → STOP FOR REVIEW
PHASE 4: Master comparison + final report       → STOP FOR REVIEW
```

---

`REVISED PLAN COMPLETE — AWAITING APPROVAL`
