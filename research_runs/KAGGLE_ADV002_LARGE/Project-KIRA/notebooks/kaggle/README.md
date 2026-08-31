# Kaggle notebooks

Two notebooks. One profiles the reference dataset; the other produces the final
artifacts. Both run on **CPU only**.

> **Accelerator must be `None`.** This project needs no GPU. Kaggle CPU sessions
> draw from a **separate allocation** and do not consume the ~30 h/week GPU quota,
> so your other projects keep their GPU hours. Setting an accelerator here burns
> quota for zero benefit.

---

## Session setup (both notebooks)

1. **kaggle.com → Settings → phone-verify your account.** Without this, notebooks
   have no internet and cannot clone the repo.
2. **Code → New Notebook**
3. Right sidebar:
   - **Accelerator** → `None`
   - **Internet** → `On`
   - **Persistence** → `Files only` (so artifacts survive a session restart)
4. Confirm you have 4 CPU cores, ~30 GB RAM, 12 h session limit.

### Secrets

**Add-ons → Secrets → Add a secret**, name `HF_TOKEN`, value = a Hugging Face
**write**-scoped token.

Never paste a token into a cell. Notebook output is saved, and a token in output is
a leaked credential.

---

## `01_profile_reference.ipynb` — owner B, BLOCK 0

**Purpose:** produce every number in `docs/DATA_PROFILE.md`. Those numbers become
the simulator's calibration targets. Until this runs, any claim about realism is
unsupported.

### Input

Sidebar → **Add Input → Datasets** → search `kartik2112/fraud-detection` → Add.
It mounts read-only at `/kaggle/input/fraud-detection/`. Licence is **CC0**, so
there is nothing to check.

### What it must compute

Follow `docs/DATA_PROFILE.md` section by section — volume and fraud rate,
per-customer activity and clusters, amount distributions (log-normal parameters per
archetype), timing (inter-arrival, hour-of-day, burstiness, autocorrelation),
merchant degree distribution, geography and implied travel speed, and fraud
characteristics.

### The most important cell

**§2.8 — the variability floor.** Split the real data in half and compute every
P1–P4 metric *between the two halves*. That is the denominator for every degradation
ratio in the fidelity filter. Without it, layer 3 produces numbers nobody can
interpret. State whether the split is by time or by customer.

### Output

Fill `docs/DATA_PROFILE.md` and commit it. It is a document, not an artifact — it
does not go to the Dataset repo.

---

## `02_full_run.ipynb` — owner B, BLOCK 6

**Purpose:** one notebook, one `run_id`, every final number. This is the run the
report and the live demo both cite.

### Shape of the notebook

| Cell group | Does |
|---|---|
| 1 · setup | clone the **public** GitHub repo, `pip install -e ".[heavy]"`, print versions |
| 2 · config | `MCDL_SCALE=full`, set the seed, create the `run_id`, write the manifest |
| 3 · world | generate the world; **run filter L1 and stop if violations > 0** |
| 4 · features | build batch features; run the parity check on a sample |
| 5 · blue | train, calibrate, evaluate on the out-of-time split |
| 6 · anchor | evaluate on Sparkov; run TSTR |
| 7 · fidelity | filter layers L2, L3, L4, L5 |
| 8 · red | attacks per family; ASR by budget; MED |
| 9 · loop | three rounds: failure store → replay → challenger → promotion gate |
| 10 · write | `evaluation.json`, `transactions.json`, `decisions.json`, `manifest.json` |
| 11 · demo pack | downsample the stream to ~20k rows into `artifacts/demo/` |
| 12 · upload | `upload_folder()` to the HF Dataset repo |

### Non-negotiables

**Checkpoint after every stage.** The session has a hard 12 h limit and can die
without warning. If a stage completes, its output must survive. A run that has to
restart from zero on day 3 is a lost day.

**Stop on a failing gate.** If L1 reports violations, the notebook must halt, not
continue to training. Every number after a failed gate is meaningless, and
producing them wastes the session.

**One run_id for everything.** Do not mix stages from different runs. The whole
provenance chain depends on it.

**Keep the demo pack small.** Under ~200 MB, ideally far less. It is baked into the
Space image, and a large image makes every redeploy slow.

### Output

```
artifacts/<run_id>/
  manifest.json            git commit, config hash, seed, scale, timings
  evaluation.json          fidelity + rounds + anchor + ablations
  transactions.json        the replay stream
  decisions.json           one decision per transaction
  counterfactual_sample.json
```

Uploaded to the Dataset repo, from which the Space pulls at startup. See
`docs/DEPLOYMENT.md` §4.

---

## After the run

1. Update `brain/CLAIMS.md` — every claim gets its `run_id` and measured value
2. Run `make gate 6` locally — it fails if the active run is still a fixture, if
   the git commit is unknown, or if the external anchor was not measured
3. Redeploy the Space and confirm the FIXTURE banner is gone
4. Open the Space **on a phone, on mobile data**, and check a number in the UI
   against `evaluation.json`

If those agree, the system is honest end to end.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Cannot clone the repo | make it public; Internet On; phone-verify the account |
| Out of memory at `scale: full` | process per entity, write incrementally, use lazy polars |
| Session died mid-run | resume from the last checkpoint — that is what they are for |
| `HF_TOKEN` not found | Add-ons → Secrets, then attach the secret to the notebook |
| Upload fails | confirm the Dataset repo exists and the token has **write** scope |

More in `docs/ERRORS_PLAYBOOK.md`.
