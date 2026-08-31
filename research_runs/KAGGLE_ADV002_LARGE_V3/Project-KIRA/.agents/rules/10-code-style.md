# 10 — Code style

## Stack

`polars` for dataframes. `pydantic v2` for every cross-module contract.
`lightgbm` for models. `fastapi` for the API. Standard library for everything else.

**No pandas.** If you need something polars cannot do, write it in `numpy` or ask
in `brain/DECISIONS.md`. Mixing the two doubles the memory footprint and the bugs.

**No new dependencies** without a line in `brain/DECISIONS.md` saying what it
replaces and why. The API container must stay small — heavy extras
(`xgboost`, `shap`, `networkx`, `huggingface-hub`) live in the `heavy` optional
group and are installed on Kaggle, not in the Space.

## Contracts

Everything that crosses a module boundary is a pydantic model in
`src/mcdl/schemas.py`. If two modules pass a dict, that is a bug waiting for day 3.

`frontend/src/api.ts` mirrors `schemas.py`. When you change a schema, change both
in the same commit — the UI should break loudly, not render wrong numbers.

## Layout

- `src/mcdl/` is a library. It must not know about FastAPI, and it must not print.
- `api/` is a thin adapter: read artifacts, call `mcdl`, return a schema.
- `tools/` are entry points humans run.
- Anything under `artifacts/` is generated. Never hand-edit it, never commit it
  except `artifacts/demo/`.

## Conventions

- Type hints on public functions. Return a schema or a `pl.DataFrame`, not a tuple
  of five things.
- `pathlib.Path`, never string concatenation for paths. This repo is developed on
  Windows and runs on Linux.
- Seeds threaded explicitly: `rng = np.random.default_rng(seed)`. No global
  `np.random.seed`. Every entry point takes a seed and records it in the manifest.
- No bare `except:`. Catch what you expect, and let the rest crash loudly — a
  swallowed exception on day 2 becomes an inexplicable number on day 3.
- Docstrings explain **why**, not what. The signature already says what.

## Errors

When something fails in a way that cost you more than ten minutes, append to
`brain/ERRORS.md`: symptom, root cause, the fix that actually worked. That file
becomes `docs/ERRORS_PLAYBOOK.md` and it is genuinely useful to a reader.

## Commits

Small and frequent, straight to `main`. Two people in one conversation do not
need PR review, and in a 3-day build the ceremony costs more than it catches.

Message format: `BLOCK-N: what changed`. Example: `BLOCK-2: batch/stream parity test`.
