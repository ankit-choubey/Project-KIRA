# 30 — Frontend

React 18 + Vite + TypeScript. Charts with `uplot` (small, fast) or hand-drawn SVG.
No component library — five views do not justify the bundle.

## The app is a test instrument, not a dashboard

A dashboard displays. An instrument lets you turn a knob and see what moves. Every
view must have something the user can change, and seeds must be settable from the
UI — "reproducible from the interface" is the single most credible detail we can
put in front of a technical judge.

## Views

| Route | Job |
|---|---|
| `/monitor` | Replayed transaction stream, speed control, decision chips, running FPR/recall, latency histogram |
| `/inspect/:id` | One transaction: features, score, SHAP bars, decision, intent-drift breakdown, small graph neighbourhood, **and the counterfactual line** ("change amount by ₹340 → ALLOW") |
| `/red` | Family / budget / mutation-strength / seed controls → run → ASR, fidelity, MED, attack-surface scatter |
| `/coevolution` | Round scrubber; ASR, MED and PR-AUC moving together; champion vs challenger side by side |
| `/evidence` | The 5 filter layers, the 17×–99× comparison table, anchor results, ablations, claim register |

`/inspect` does the work of three views — build it properly. `/evidence` is what
makes a judge trust the other four.

## Rules

1. **The UI never computes a metric.** It renders what `/api/*` returns. If a
   number needs deriving, derive it in Python where a test can cover it.
2. **Honest empty states.** When a metric was not measured, render `not measured`
   in muted type. Never a zero, never a dash that reads as zero, never a
   placeholder chart. Judges notice, and it makes the populated numbers credible.
3. **One typed client**, `src/api.ts`, mirroring `src/mcdl/schemas.py`. No `fetch`
   calls scattered through components.
4. **Every number shows its provenance.** The run_id is visible in the header and
   any metric can be traced to it.
5. Loading and error states on every view. A judge on hotel wifi should see
   "loading" and then a retry, not a blank page.

## Build and deploy — read this before committing

**npm must never run inside the Docker build on Hugging Face Spaces.** It is the
most likely deploy failure on the last day. Instead:

```bash
cd frontend && npm run build      # produces frontend/dist/
git add -f frontend/dist          # dist/ is gitignored by default - force it
```

The Dockerfile is pure Python and just copies `frontend/dist`. Build time on the
Space is ~2 minutes and cannot fail on a node toolchain.

Two settings that cause a blank page on the Space while localhost works fine:

- `vite.config.ts` must set `base: './'` (relative asset paths).
- FastAPI must mount the static files at `/` **after** the `/api` routes,
  otherwise the catch-all swallows the API.

Dev mode (`make dev`) runs Vite on :5173 proxying `/api` to FastAPI on :8000, so
you are not rebuilding on every change.
