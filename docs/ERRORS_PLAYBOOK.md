# ERRORS PLAYBOOK

Failures we expect at each step, and the fix for each. Pre-loaded from the audit so
nobody debugs these from scratch at 2 a.m.

When something costs you more than ten minutes, add it to `brain/ERRORS.md` with
symptom → root cause → the fix that actually worked. That file feeds back into this
one, and it is genuinely useful to a reader — it shows the work.

---

## The general rule

> **A suspicious success is a failure you have not found yet.**

PR-AUC around 0.99, ASR dropping to zero in one round, C2ST AUC of exactly 0.5 —
each is a bug report, not a result. Go back up the gate ladder.

---

## BLOCK 0 — contracts and deployment

| Symptom | Cause | Fix |
|---|---|---|
| `UnicodeEncodeError: 'charmap' codec can't encode` | Windows console is cp1252 and cannot encode box-drawing characters | ASCII-only console output; `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`. Already fixed — see `brain/ERRORS.md` E-001 |
| LightGBM wheel fails to install on Windows | build toolchain | use `pip` rather than `uv`, or build inside WSL |
| Space shows "Configuration error" | missing YAML header | `sdk: docker` and `app_port: 7860` at the top of `README.md` |
| Space build fails on permissions | files copied as root | `useradd -m -u 1000 user`, `USER user`, `COPY --chown=user` |
| Push to Space rejected | HF password used | use a **write**-scoped access token |
| Gate 0 fails on "observable+hidden cover all fields" | a field was added to `Transaction` without classifying it | add it to `observable_fields()` or `hidden_fields()`. If unsure, it is hidden |

---

## BLOCK 1 — the world

| Symptom | Cause | Fix |
|---|---|---|
| Simulator runs at a few hundred events/sec | per-event Python object churn | generate per entity in a loop, write with polars. Target 5k+ events/sec |
| Ledger rejects nearly everything | usually an off-by-one on credit limits | log the first 20 rejections **with reasons** before changing anything |
| Gate 1 fails on geography feasibility | travel-speed threshold too tight | set it from the p99 implied speed in `DATA_PROFILE.md`, not a guess |
| FK integrity failures | entity written after the transaction referencing it | generate entities first, then events. Assert inside the pipeline |
| All customers of an archetype behave identically | behavioural parameters drawn per archetype instead of per customer | draw per customer. Identical customers make the detector look better than it is |
| React blank page on the Space, fine on localhost | absolute asset paths | `base: './'` in `vite.config.ts`; rebuild and recommit `dist` |
| `/api/*` returns HTML | static mounted before the API routes | mount static **last** |
| `/evidence` 404s on refresh | no SPA fallback | catch-all serves `index.html` for non-API paths, and 404s JSON for `api/*` |

---

## BLOCK 2 — features (the dangerous one)

| Symptom | Cause | Fix |
|---|---|---|
| **Velocity numbers look wrong, no error raised** | `polars.rolling(window_size=n)` is a **row-count** window | use `rolling(index_column=..., period="1h")` or `group_by_dynamic` |
| Batch/stream parity fails on a handful of rows | ties at identical timestamps | sort by `(timestamp, txn_id)` everywhere, defined once |
| Parity fails only for the first N rows per entity | warm-up state differs between paths | define the cold-start value explicitly in `features/spec.py` and use it in both |
| Parity passes but the model is suspiciously good | a feature reads events after `t` | run the leakage probe; check any aggregate computed before the split |
| A new feature is not covered by the parity test | it was added to `batch.py` only | both paths must be generated from `spec.py`. Never add to one side |
| C2ST AUC = 1.0 immediately | usually a leaked id column, or exactly-round amounts | read the discriminator's SHAP — it names the culprit in one run |
| C2ST AUC = exactly 0.5 | the discriminator did not train, or labels are constant | check class balance in the discriminator's own training set |

> Gate 2 is the gate that catches the bug that looks like success. If it is
> failing, **do not proceed to BLOCK 3**.

---

## BLOCK 3 — Blue team

| Symptom | Cause | Fix |
|---|---|---|
| **PR-AUC around 0.99** | leakage, or the detector learned a generator rule | this is a **gate-2 failure**, not a success. Do not celebrate. Check hidden fields, aggregates computed pre-split, and attack camouflage in the world |
| Isotonic calibration overfits | fitted on few positives, or on train | fit on a held-out slice with a cross-validated wrapper |
| ECE worse after calibration | too few positives in the calibration slice | enlarge the slice or fall back to Platt, and report which was used |
| SMOTE ablation shows "no difference" on AUC | AUC is the metric that hides the damage | report ECE and FPR. That is the whole point of the ablation |
| Anchor evaluation errors on column names | Sparkov schema differs from ours | one mapping module, `evaluation/anchor_map.py`. Not scattered renames |
| Anchor PR-AUC is near zero | feature distributions differ too much to transfer | that is a **result**. Report it and say what it implies about simulator realism |
| Model beats the rule baseline by a tiny margin | features are not carrying behavioural signal | check velocity windows are time-based (see BLOCK 2) |

---

## BLOCK 4 — Red team

| Symptom | Cause | Fix |
|---|---|---|
| **Attack search takes hours** | candidates scored one at a time | score the whole population in one `predict()` call. 10–50× win, first thing to build |
| Still too slow after batching | population/generations too large | drop to 40 × 15; then full search on two families only — and say so in the report |
| Mutability mask violations appear | mask checked after sampling instead of during | enforce it **inside** the sampler |
| Attacks evade but are absurd | they violate physics | that is filter L1 doing its job. Reject and count them |
| ASR is implausibly high | unlimited query budget | record `queries_used` and report ASR per budget. Unlimited-query ASR is meaningless |
| MED cannot be found for most attacks | the search step is too coarse | bisect on the mutable field rather than sweeping a fixed grid |
| P3 graph motif ratio is wildly off | Sparkov has no device column | device structure is a modelling assumption, not fitted. Say so in `LIMITATIONS.md` |
| Degradation ratios are uninterpretable | the variability floor was never computed | §2.8 of `DATA_PROFILE.md`. Without it, layer 3 means nothing |

---

## BLOCK 5 — closed loop

| Symptom | Cause | Fix |
|---|---|---|
| **ASR drops to zero in one round** | you are measuring memorisation | check the variants 0–4 / 5–9 split is actually enforced. Report held-out separately |
| False positives explode after hardening | replay mix is too fraud-heavy | cap replay at `loop.replay_max_fraction` |
| Challenger wins on new attacks, wrecks old ones | catastrophic forgetting | that is a **result**. Report it, and let the promotion gate reject the challenger |
| Nothing is ever promoted | the five-dimension gate is too strict for three rounds | loosen deliberately and document the change, or report "no promotion" honestly |
| Intent score fires on legitimate agent traffic | mandate too narrow, or weights untuned | tune on legitimate agent transactions first, then evaluate on R8 |
| Intent engine catches nothing | R8 attacks are not actually violating the mandate | check the attack generator is drifting *intent*, not just amount |

---

## BLOCK 6 — cloud run

| Symptom | Cause | Fix |
|---|---|---|
| Kaggle session dies at 12 h | no checkpoints | checkpoint after every stage; make the notebook resumable |
| Kaggle cannot clone the repo | repo private, or Internet off, or account unverified | make it public, toggle Internet On, phone-verify the account |
| Kaggle out of memory at `scale: full` | holding full frames | process per entity, write incrementally, use lazy polars |
| Artifacts too large for the Space | full stream committed | keep `artifacts/demo/` under ~200 MB; downsample the replay to ~20k rows |
| Space OOM at 16 GB | loading everything at startup | load lazily; the stream endpoint is paged for a reason |
| Space restarts and loses data | free Spaces have **ephemeral** disk | never write state on the Space. Artifacts come from the image or the Dataset repo |
| Gate 6 fails on "run is NOT a fixture" | `LATEST` still points at the fixture run | run the real pipeline and update the pointer. **Do not weaken the check** |
| Numbers in the UI differ from `evaluation.json` | UI is computing instead of rendering | the UI must never compute a metric |

---

## BLOCK 7 — submission

| Symptom | Cause | Fix |
|---|---|---|
| Space asleep when a judge opens it | 48 h idle sleep | visit the URL before the session; keep the demo video as a fallback |
| A number in the report has no `run_id` | typed by hand | remove it or measure it. There is no third option |
| Secret found in the repo | committed and later deleted | it is still in git **history**. Rotate the token and rewrite history |
| Writeup saved but not submitted | the most common way a project scores zero | check for the confirmation on screen and screenshot it |

---

## Escalation

If a gate fails and the fix is not here:

1. Re-run the gate above it. The problem is usually one layer up.
2. Reduce `scale` to `tiny` and reproduce. Most bugs survive the shrink; the ones
   that do not are memory or timing bugs, which is itself information.
3. Check `brain/ERRORS.md` for it.
4. **Never weaken an assertion to make a gate pass.** Fix the cause, or record in
   `brain/ERRORS.md` why the assertion itself was wrong.
