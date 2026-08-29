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
