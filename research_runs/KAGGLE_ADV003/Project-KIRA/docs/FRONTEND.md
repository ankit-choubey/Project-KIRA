# FRONTEND — React + Vite

Owner: **A**. Lives in `frontend/`.

---

## 1. The governing idea

> **The app is a test instrument, not a dashboard.**

A dashboard displays. An instrument lets you turn a knob and see what moves. Every
view must have something the user can change, and **seeds must be settable from the
UI** — "reproducible from the interface" is the single most credible detail you can
put in front of a technical judge.

## 2. Stack

React 18 + Vite + TypeScript, strict mode. `react-router-dom` for routing. Charts
as hand-drawn SVG or a small library. **No component library** — five views do not
justify the bundle.

## 3. The five views

| Route | Job |
|---|---|
| `/monitor` | Replayed transaction stream with speed control, decision chips, running recall and false-positive rate, latency |
| `/inspect/:txnId` | One transaction: features, score, SHAP bars, decision, intent-drift breakdown, graph neighbourhood, **and the counterfactual** |
| `/red` | Family / query budget / mutation strength / seed controls, run, then ASR, fidelity, MED, attack-surface scatter |
| `/coevolution` | Round scrubber; ASR, MED and PR-AUC moving together; champion vs challenger side by side |
| `/evidence` | The five filter layers, the 17×–99× comparison table, anchor results, ablations, claim register |

### `/inspect` does the work of three views

Build it properly. The line people remember is the counterfactual:

> "Reducing the amount by 340 flips BLOCK to ALLOW."

### `/evidence` is what makes a judge trust the other four

It is the view that shows explicit gaps next to populated numbers. A page of
suspiciously complete numbers reads as invented; a page where four things are
measured and two say "not measured" reads as real.

## 4. Non-negotiable rules

1. **The UI never computes a metric.** It renders what `/api/*` returns. If a
   number needs deriving, derive it in Python where a test can cover it. (The one
   exception is the Monitor's running tally over revealed rows, which is a display
   artefact of the replay, not a reported metric.)

2. **Honest empty states.** When a metric was not measured, render `not measured`
   in muted italic type. Never a zero, never a dash that reads as zero, never a
   placeholder chart. This is a correctness feature, not decoration.

3. **One typed client**, `src/api.ts`, mirroring `src/mcdl/schemas.py`. No `fetch`
   calls scattered through components. When a schema changes, change both in the
   same commit so the UI breaks loudly rather than rendering a wrong number.

4. **Provenance always visible.** The `run_id` sits in the header. Any number on
   screen belongs to that run.

5. **The FIXTURE banner.** When `is_fixture` is true, a banner states plainly that
   these are placeholder values and must never be cited. Do not remove it to make a
   screenshot look better.

6. **Loading and error states on every view.** A judge on hotel wifi should see
   "loading" and then a retry, not a blank page.

## 5. Build and deploy — read before committing

**npm must never run inside the Docker build on Hugging Face Spaces.** It is the
single most likely last-day deploy failure: slow, occasionally flaky, and it fails
at the worst possible time.

```
locally:   cd frontend && npm run build      ->  frontend/dist/
           git add -f frontend/dist          ->  dist/ is gitignored; force it
Docker:    pure Python image, copies frontend/dist. No node at all.
```

`make frontend` does the build and the force-add in one step.

### Two settings that cause a blank page on the Space while localhost works

- `vite.config.ts` must set `base: './'`. Absolute asset paths give a blank page
  when the app is not served from the domain root.
- FastAPI must mount static at `/` **after** the `/api` routes.

## 6. Development

```
make dev      FastAPI :8000 + Vite :5173, with /api proxied
```

Work against `:5173` so you are not rebuilding on every change. Before deploying,
build and check the built app at `:8000` — that is the path the Space uses, and it
is where `base: './'` and route-ordering problems show up.

## 7. Styling

Dense, legible, honest about gaps. Dark instrument-panel palette defined as CSS
variables in `src/styles.css`. Monospace with tabular figures for every number.
Decision states carry colour: ALLOW green, STEP_UP amber, BLOCK red — and the
`.unmeasured` class is deliberately styled to look **different from a value**, not
like a small one.

Wide content (tables) scrolls inside its own container so the page body never
scrolls sideways.

## 8. What each view needs from the API

| View | Endpoints |
|---|---|
| Monitor | `GET /api/stream` |
| Inspector | `GET /api/transaction/{id}` |
| Red Console | `GET /api/config`, `POST /api/attack` |
| Co-Evolution | `GET /api/coevolution` |
| Evidence | `GET /api/evidence` |
| All | `GET /api/health` for the header and the FIXTURE banner |

Endpoints that 501 (Red engine before BLOCK 4) should disable their control and
explain why, rather than surfacing a raw error.

## 9. What not to build

No auth. No dark/light toggle. No animations beyond what the replay needs. No
routing state in the URL beyond the transaction id and the current view. Five views
that work beat eight that half-work, and the ML is the risk here, not the interface.
