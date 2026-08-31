# AGENTS.md

Mastercard AI Defense Lab — an adversarial payment-security laboratory. A stateful
synthetic payment world generates realistic transactions; a Red engine mutates
constrained attacks against a Blue detector; every successful evasion is analysed,
replayed and used to harden a challenger model. We measure whether hardening
actually generalises rather than memorises.

## Before you touch anything

1. Read `brain/PROJECT_CONTEXT.md` — current block, what exists, what does not.
2. Read the rule file for your area in `.agents/rules/`.
3. When done, append an entry to `brain/HANDOFF.md`.

## Commands

```bash
make setup            # install (uv preferred, pip fallback)
make gate N           # N = 0..7. Prints PASS/FAIL, exits non-zero, updates brain/
make run SCALE=tiny   # full pipeline, ~2 min
make dev              # FastAPI :8000 + Vite :5173
make brain            # regenerate brain/PROJECT_CONTEXT.md from artifacts
```

## Compute rule

Laptop = code, tests, `scale: tiny|small`. Kaggle CPU notebook = `scale: full`.
Hugging Face Space = serves artifacts only, **never computes**. No GPU is used
anywhere in this project.

## Hard prohibitions

1. **Never fabricate a metric.** Every number comes from a file under `artifacts/`.
2. **Never claim a cloud run happened** without a `manifest.json` to point at.
3. **Never let a feature read an event after time `t`.** See `.agents/rules/20-ml-rules.md`.
4. **Never use SMOTE**, and never use pandas where polars is already used.
5. **Never edit `brain/PROJECT_CONTEXT.md` by hand** — it is generated.

Scope discipline: implement the assigned block only. Do not add dependencies, do
not redesign architecture, do not "improve" unrelated files. If something outside
your block is broken, write it in `brain/ERRORS.md` and keep going.
