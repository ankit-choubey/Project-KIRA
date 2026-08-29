# ERRORS

Symptom -> root cause -> the fix that actually worked. Add an entry whenever
something costs more than ten minutes. This file becomes `docs/ERRORS_PLAYBOOK.md`,
which is genuinely useful to a reader and shows the work.

---

### E-001 · `UnicodeEncodeError: 'charmap' codec can't encode` when running gates

**Symptom:** `python -m tools.gates 0` crashed instantly on Windows with a cp1252
encoding error at the very first `print`.

**Root cause:** The Windows console defaults to cp1252, which cannot encode the
box-drawing character `U+2500` used in the gate header rule.

**Fix:** ASCII-only console output in `tools/gates.py`, plus
`sys.stdout.reconfigure(encoding="utf-8", errors="replace")` guarded by `hasattr`.
ANSI colour is now also suppressed when stdout is not a TTY, so CI logs stay clean.

**Lesson:** This repo is written on Windows and runs on Linux. Keep console output
ASCII, and always use `pathlib` rather than string path concatenation.

---

## Errors we expect and how to handle them

Pre-loaded from the build plan so nobody debugs these from scratch. Move an entry
above the line with a real fix once it actually bites.

### Deploy

- **HF Space "Configuration error"** — the Space `README.md` YAML block needs
  `sdk: docker` and `app_port: 7860`.
- **Permission denied on Space startup** — the Dockerfile must `useradd -m -u 1000 user`,
  `USER user`, and use `COPY --chown=user` for every copy.
- **Blank page on the Space, fine on localhost** — `vite.config.ts` needs
  `base: './'`, and FastAPI must mount static at `/` *after* the `/api` routes.
- **Space asleep before judging** — free CPU Spaces sleep after 48 h idle and wake
  on visit (~30 s). Open the URL once before the demo.

### Features

- **Wrong velocity numbers, no error** — `polars.rolling(window_size=n)` is a
  *row-count* window. Time-based velocity needs `rolling(index_column=..., period="1h")`
  or `group_by_dynamic`.
- **Batch/stream parity fails on a handful of rows** — ties at identical timestamps.
  Sort by `(timestamp, txn_id)` everywhere, defined once.

### Modelling

- **PR-AUC around 0.99** — this is a bug report, not a success. Go back to gate 2.
  It almost always means leakage or the detector learning a generator rule.
- **C2ST AUC = 1.0 immediately** — usually a leaked id column or an exactly-round
  amount distribution. The discriminator's SHAP will name the culprit in one run.
- **Isotonic calibration overfits** — fit on a held-out slice, never on train.

### Red team

- **Attack search takes hours** — never score candidates one at a time. Score the
  whole population in a single `predict()` call. Fallback: population 40,
  15 generations, two families, and say so in the report.
- **Mask violations appear** — the mask must be enforced inside the sampler, not
  checked afterwards.

### Cloud

- **Kaggle 12 h timeout** — checkpoint after each stage; the notebook must resume.
- **Kaggle cannot clone the repo** — make it public early, or upload the source as
  a Kaggle Dataset.
- **Space OOM at 16 GB** — load parquet lazily; never hold the full frame.
