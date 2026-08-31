# 20 — ML rules

These exist because each one, if broken, produces a result that looks correct and
is not. Read this before writing anything under `src/mcdl/features`, `blue`,
`red`, `loop` or `evaluation`.

## 1. Causality — the rule that matters most

Every feature must satisfy:

```
feature(t) = f(events <= t)        never  f(events > t)
```

Sort order is **`(timestamp, txn_id)` everywhere**, defined once. Ties on equal
timestamps are the classic source of batch/stream disagreement.

There are two implementations of every feature and they must agree:

- `features/batch.py` — polars, vectorised, used for training.
- `features/stream.py` — dict state, one row at a time, used for serving.

Both are driven by the single list in `features/spec.py`. **Never add a feature to
one path only.** `tests/invariants/test_batch_stream_parity.py` asserts they match
to 1e-9 on sampled rows, and gate 2 runs it. If that test is failing, nothing
downstream is trustworthy.

Polars trap: `.rolling(window_size=n)` is a **row-count** window. Time-based
velocity needs `rolling(index_column=..., period="1h")` or `group_by_dynamic`.
Using the row-count form silently produces wrong velocity features.

## 2. Label delay

Fraud labels arrive days later via chargebacks. Any feature reading another
entity's *label* (e.g. `recent_neighbor_fraud_rate`) must only see labels
confirmed at least `features.label_availability_lag_days` before `t`. Using
same-day neighbour labels is information the real system would not have.

We report performance under realistic lag **and** with oracle labels. The gap is
a result worth having, not something to hide.

## 3. Class imbalance — do not use SMOTE

Use `scale_pos_weight` (LightGBM/XGBoost) plus threshold optimisation.

Reason, not preference: SMOTE preserves ranking but distorts posterior
probabilities. A published comparison saw false alarms rise from 35 to 5,775
while ROC-AUC barely moved (0.9806). Our entire decision policy is cost-sensitive
and therefore depends on calibrated probabilities, so a method that wrecks
calibration while flattering AUC is exactly wrong for us.

We still *run* the comparison as an ablation — and report it on **ECE and FPR**,
not AUC, because AUC is the metric that hides the damage.

## 4. Splits and anti-circularity

- Out-of-time only: `train.max_ts < valid.min_ts` and `valid.max_ts < test.min_ts`.
  Asserted, not assumed.
- Resampling or reweighting happens **after** the split, inside training folds only.
- `train_attack_ids ∩ test_attack_ids = ∅`.
- Generation seeds used for training must differ from evaluation seeds.
- Families in `red.hidden_from_blue` never appear in Blue's training data. They
  are the zero-day transfer test.

## 5. The closed loop must not measure memorisation

Blue hardens on variants `0 .. harden_on_variants-1` of a family. The **headline**
number is ASR on the remaining variants of that same family — generalisation
within a family. Then:

- ASR on an entirely unseen family — transfer.
- PR-AUC on the original benign+fraud test set — no regression.

Reporting ASR on the variants you trained on is not a result.

## 6. Attacks must be constrained

The mutability mask splits fields into attacker-controllable and not:

- **Mutable:** amount, timestamp/timing, merchant choice within category, device,
  channel, session ordering.
- **Immutable:** victim account age, historical spend distribution, past
  transactions, merchant's own history, anything already written to the ledger.

Enforce the mask **inside the sampler**, not as a check afterwards. Every
generated attack must also pass validity (filter L1) — an "evasion" that violates
physics is a bug in the mask, not a discovery.

Record the **query budget** consumed per successful evasion. ASR without a budget
describes an attacker with impossible capabilities.

## 7. Calibration and decisions

Isotonic calibration fitted on a held-out slice, never on the training data.
Report Brier and ECE. The decision policy optimises expected cost:

```
utility = -(fraud_loss * P(fraud) * amount) - (friction * P(step_up)) - (review * P(review))
```

Report a **cost/friction curve across the threshold sweep**, not F1. Payments
audiences think in loss and friction.

## 8. Latency

Measure `feature build (warm state) + inference + policy`, end to end, over the
real HTTP path. Report P50/P95/P99. Name the state store honestly — an in-process
dict is not production, and saying so earns more credibility than hiding it.

Reporting `model.predict()` time alone as end-to-end latency is misleading.

## 9. Reproducibility

Every run writes `artifacts/<run_id>/manifest.json` containing: git commit, config
hash, seed, scale, timings, and the metrics. A metric with no run_id does not go
in the report or the UI.
