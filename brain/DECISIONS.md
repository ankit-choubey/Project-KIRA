# DECISIONS

Append-only. One entry per decision that rules something out. If you disagree with
a decision here, add a new entry arguing against it — do not edit the old one.

---

### D-001 · Simulator-first, with a real dataset as anchor

**Decision:** Our own stateful simulator is the primary training world. Sparkov
(`kartik2112/fraud-detection`, **CC0**) is the external reality anchor, the C2ST
reference, the calibration source, and the TSTR test set.

**Why:** Attack generation needs a world we control end to end; a static CSV cannot
be attacked. But a simulator cannot prove its own realism, so we need the anchor.

**Rules out:** Training primarily on a public CSV. Claiming realism without the anchor.

### D-002 · Do not use the BAF / Feedzai dataset

**Decision:** BAF is excluded despite being a good fraud dataset.

**Why:** Licensed CC BY-NC-**ND** 4.0. No-Derivatives is a real exposure for a public
repo attached to a corporate-sponsored competition. Sparkov is CC0 and sufficient.

**Rules out:** Any use of BAF, including "just for calibration".

### D-003 · No GPU anywhere

**Decision:** Everything runs on CPU. Kaggle CPU notebooks for the full run.

**Why:** The P0 path is tabular gradient boosting, simulation and genetic search —
all CPU-bound. Kaggle CPU sessions (4 cores, ~30 GB, 12 h) do not draw down the
weekly GPU quota, so our other projects keep their GPU hours intact.

**Rules out:** The six-profile compute system in the original spec. Any Tier-3 model
whose only justification is that we have GPU credit available.

### D-004 · `scale_pos_weight`, never SMOTE

**Decision:** Class imbalance is handled with `scale_pos_weight` plus threshold
optimisation. SMOTE appears only as an ablation, reported on ECE and FPR.

**Why:** SMOTE preserves ranking but distorts posterior probabilities. A published
comparison saw false alarms go 35 -> 5,775 with ROC-AUC essentially unchanged. Our
decision policy is cost-sensitive and therefore depends on calibrated probabilities.

**Rules out:** Reporting a SMOTE result on AUC alone — the metric that hides the damage.

### D-005 · Commit `frontend/dist`; npm never runs in Docker

**Decision:** The React app is built locally and `frontend/dist` is force-added to
git. The Dockerfile is pure Python.

**Why:** npm inside a Hugging Face Space build is the most likely last-day deploy
failure. Removing node from the image makes the build ~2 minutes and unbreakable.

**Rules out:** Multi-stage node builds in the shipped Dockerfile.

### D-006 · Fixtures before features

**Decision:** `src/mcdl/fixtures.py` emits schema-valid fake artifacts, and the API,
UI, evaluation harness and report are all built against them first.

**Why:** Otherwise one developer is blocked for two days and then builds the UI on
day 3 against artifacts they have never seen.

**Rules out:** "Wait for the real data" as a reason not to start a downstream block.

### D-007 · A gate is never green by default

**Decision:** An unimplemented gate reports PENDING and exits 2. It never reports PASS.

**Why:** "The gate passed" must always mean the check actually ran. A default-green
ladder is worse than no ladder, because it manufactures false confidence.

**Rules out:** Stubbing a gate to return success in order to unblock a commit.

### D-008 · Sequential balance verification and observable transaction schema

**Decision:** The `Transaction` schema retains causal `balance_before` and
`available_credit` at event time `t`, but intentionally omits post-authorization
`balance_after`. Layer-1 validity independently verifies:
1. Intra-transaction accounting identity: `balance_before + available_credit == credit_limit`
2. Credit-limit ceiling: `balance_before <= credit_limit`
3. Sequential inter-transaction transitions: For consecutive transactions of the same
   customer $(T_k, T_{k+1})$, $T_{k+1}.\text{balance\_before}$ must strictly match either
   unsettled transition $\text{round}(B_k + A_k, 2)$ or periodic settlement
   $\text{round}(\text{round}(B_k + A_k, 2) \times 0.35, 2)$.

**Why:** Online detectors scoring at time $t$ only have access to pre-authorization
ledger state. Proving balance validity through pre-state sequences prevents post-event
feature leakage into training datasets while strictly catching ledger transition bugs.

**Rules out:** Adding `balance_after` to `Transaction` or manufacturing fake post-event fields.

### D-009 · Adaptive Red/Blue Co-Evolution with Failure Diagnosis and Strict Zero-Day Isolation

**Decision:** Block 7 implements genuine adaptive co-evolution using:
1. **12-Class Failure Taxonomy (W1..W12)**: Systematically classifies defensive blind spots (velocity blindness, low-and-slow, intent drift, geo camouflage, multi-account coordination).
2. **Failure-Driven WeaknessProfiles**: Round $r$ Red search distributions and mutation ranges are dynamically re-seeded based on Round $r-1$ observed failures, avoiding memorized replays.
3. **Prioritized Replay Hardening**: Replay buffer samples evasions proportional to a composite priority score ($\text{hardness}, \text{novelty}, \text{boundary\_proximity}, \text{rarity}$), converting to observable features with zero metadata leakage.
4. **Three-World Evaluation & Zero-Day Isolation**: World A (Evolution), World B (Shifted Physics), and World C (Hidden Families) enforce hard runtime isolation $\text{Adaptation} \cap \text{Hidden} = \emptyset$.
5. **Multi-Objective Promotion Gate with Deterministic Rollback**: Challenger promotion requires meeting PR-AUC, Held-out ASR reduction, FPR ($\le 0.05$), ECE ($\le 0.08$), Retention ($\ge 0.95$), and Latency budgets. Failed promotions trigger automated rollback.
6. **No Architecture Bloat**: Excludes GNN, RL (PPO/DQN), Diffusion, LLMs, and Generative Replay, maintaining pure constrained mutation search, LightGBM, isotonic calibration, and cost-sensitive Bayesian routing.

**Why:** Real-world payment defense requires measurable, generalizable robustness against adaptive adversaries without destroying legitimate transaction approval or introducing unmaintainable complex models.

**Rules out:** Fake adaptation (random seeds without weakness feedback), circular evaluation (testing on training attack variants), unisolated zero-day claims, and architecture bloat.
