# BACKEND — FastAPI

Owner: **A**. Lives in `api/`.

---

## 1. Design rule

> **Thin by design: read an artifact, call `mcdl`, return a schema.**

The Space never computes. Two consequences:

1. The demo cannot fail the way live training fails — no model to load badly, no
   dataset to run out of memory on, no run to time out mid-presentation.
2. `POST /api/score` is a genuine end-to-end HTTP measurement, which is what makes
   the latency claim defensible.

`api/` may import `src/mcdl/`. `src/mcdl/` must **never** import `api/` or FastAPI.

## 2. Endpoints

| Method | Path | Returns | Notes |
|---|---|---|---|
| GET | `/api/health` | `status`, `run_id`, `is_fixture`, `artifacts_loaded`, `detail` | Never 500s. Degrades to `status: "degraded"` with an actionable `detail`. |
| GET | `/api/runs` | list of available `run_id`s | |
| GET | `/api/config` | scale, families, hidden families, query budgets, config hash | Drives the Red Console controls. |
| GET | `/api/stream?offset=&limit=` | paged transactions + decisions, `total` | Drives the Monitor. `limit` capped at 1000. |
| GET | `/api/transaction/{id}` | transaction, decision, counterfactual, SHAP, intent breakdown, neighbours | 404 if unknown. Unbuilt fields return `null`. |
| POST | `/api/score` | decision, `served_by`, `api_latency_ms` | **The latency endpoint.** |
| POST | `/api/attack` | attack set, ASR, fidelity, MED | 501 until BLOCK 4. |
| GET | `/api/coevolution` | per-round metrics | Drives the Co-Evolution view. |
| GET | `/api/evidence` | the full `EvaluationResult` | Drives the Evidence view. |

## 3. Rules the API must keep

### `null` means not measured

Every metric field is nullable. Return `null`, never `0`, for anything not yet
computed. The UI renders `null` as "not measured". A zero standing in for an
unmeasured value is a lie that will survive into the report.

### Be honest about unbuilt blocks

- `POST /api/score` before BLOCK 3 returns a placeholder carrying the reason code
  `MODEL_NOT_BUILT` and `served_by: "placeholder (BLOCK 3 not built)"` — never a
  plausible-looking fake score.
- `POST /api/attack` before BLOCK 4 returns **501** with a message naming the
  missing module, so the UI can disable the control instead of showing an error.

### Surface `is_fixture` on every response that carries data

`health`, `stream`, `transaction`, `coevolution` and `evidence` all expose it. The
UI keys its FIXTURE banner off this flag. If it stops being surfaced, placeholder
numbers start looking like measurements.

### Errors must be actionable

A missing artifact returns 503 with the command that fixes it (`make gate 0` or
`make run SCALE=tiny`), not a bare `FileNotFoundError`. A blank page with no
explanation costs twenty minutes on demo day.

## 4. Static serving — two ordering bugs that only appear in front of a judge

### Route order

The SPA catch-all is registered **last**, after every `/api` route. Registered
first, it swallows the API and the UI shows an empty page.

### Deep links must not 404

React Router uses the history API. A judge refreshing on `/evidence` must get the
app, not a 404. The catch-all serves `index.html` for any non-API path, with a real
file on disk winning over the fallback so favicons and similar still resolve.

### Unknown API routes must 404 as JSON

If the catch-all swallows `/api/nonexistent`, a typo'd endpoint surfaces in the
browser as an unreadable JSON parse error instead of an obvious 404. The catch-all
must explicitly reject paths beginning with `api/`.

Both behaviours are covered by tests in `tests/e2e/test_api.py`.

## 5. Artifact loading

All loading goes through `src/mcdl/artifacts.py`, so there is exactly one
definition of "the current run":

- `resolve_run(run_id=None)` — a specific run, or follow the `LATEST` pointer
- `load_manifest` / `load_evaluation` / `load_transactions` / `load_decisions`
- `list_runs()` — everything with a `manifest.json`

On the Space, artifacts arrive one of two ways: baked into the image from
`artifacts/demo/`, or pulled at startup from the Hugging Face Dataset repo via
`snapshot_download`. See [DEPLOYMENT.md](DEPLOYMENT.md) §4.

**Do not hold the full frame in memory.** The Space has 16 GB and the stream
endpoint is paged for a reason.

## 6. Latency measurement

`POST /api/score` is the only endpoint whose timing is reported. Measure
`feature build (warm state) + inference + policy`. Report P50/P95/P99 from a
sample of real requests, and state what the state store is.

An in-process dict is not production. Writing *"in-process state; a production
deployment would need Redis or equivalent, which adds a network hop"* earns more
credibility than omitting it.

Do not report `model.predict()` time alone as end-to-end latency.

## 7. Local development

```
make api      FastAPI on :8000 with reload
make dev      FastAPI on :8000 + Vite on :5173 (Vite proxies /api)
```

CORS is open only to the Vite dev origins. In production the app and API are
same-origin, so CORS is not involved.

## 8. What must not go in the backend

- No training, no attack generation, no metric computation. If a number needs
  deriving, derive it in `mcdl` where a test can cover it.
- No secrets in code. `HF_TOKEN` comes from the environment (a Space secret).
- No new dependencies without a line in `brain/DECISIONS.md`. The container must
  stay small; heavy extras (`xgboost`, `shap`, `networkx`, `huggingface-hub`) are
  in the `heavy` optional group and install on Kaggle, not in the Space.
