"""FastAPI service.

Thin by design: read artifacts, return a schema. The Space never computes - that
is what makes the demo structurally unable to fail the way live training fails,
and it is why the latency number from /api/score means something.

Route order matters. The static mount is a catch-all and must come LAST, after
every /api route, or it swallows the API and the UI shows an empty page.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from mcdl import artifacts as art  # noqa: E402
from mcdl.config import load_config  # noqa: E402
from mcdl.schemas import (  # noqa: E402
    BlueDecision,
    Counterfactual,
    EvaluationResult,
    Transaction,
)

app = FastAPI(title="Mastercard AI Defense Lab", version="0.1.0")

# The Vite dev server runs on a different port; the built app is same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Response models the frontend mirrors in src/api.ts
# --------------------------------------------------------------------------- #


class Health(BaseModel):
    status: str
    run_id: str | None
    is_fixture: bool
    artifacts_loaded: bool
    detail: str = ""


class StreamRow(BaseModel):
    transaction: Transaction
    decision: BlueDecision | None


class StreamPage(BaseModel):
    run_id: str
    is_fixture: bool
    offset: int
    limit: int
    total: int
    rows: list[StreamRow]


class InspectResult(BaseModel):
    run_id: str
    is_fixture: bool
    transaction: Transaction
    decision: BlueDecision | None
    counterfactual: Counterfactual | None
    # Populated from BLOCK 3 onward. Null means not measured - the UI renders it
    # as "not measured", never as zero.
    shap: dict[str, float] | None = None
    intent_breakdown: dict[str, float] | None = None
    neighbours: list[str] | None = None


class ScoreRequest(BaseModel):
    transaction: Transaction


class ScoreResponse(BaseModel):
    decision: BlueDecision
    served_by: str
    api_latency_ms: float


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #


def _current():
    """Resolve the active run. Raises 503 with an actionable message, because a
    blank page with no explanation costs twenty minutes on demo day."""
    try:
        d = art.resolve_run()
        return d, art.load_evaluation(d)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/health", response_model=Health)
def health() -> Health:
    try:
        d, ev = _current()
    except HTTPException as exc:
        return Health(
            status="degraded",
            run_id=None,
            is_fixture=False,
            artifacts_loaded=False,
            detail=str(exc.detail),
        )
    return Health(
        status="ok",
        run_id=ev.manifest.run_id,
        is_fixture=ev.manifest.is_fixture,
        artifacts_loaded=True,
        detail=f"scale={ev.manifest.scale} commit={ev.manifest.git_commit}",
    )


@app.get("/api/runs")
def runs() -> dict:
    return {"runs": art.list_runs()}


@app.get("/api/stream", response_model=StreamPage)
def stream(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)) -> StreamPage:
    d, ev = _current()
    txns = art.load_transactions(d, limit=limit, offset=offset)
    decisions = art.load_decisions(d)
    total = len(art.load_transactions(d))
    return StreamPage(
        run_id=ev.manifest.run_id,
        is_fixture=ev.manifest.is_fixture,
        offset=offset,
        limit=limit,
        total=total,
        rows=[StreamRow(transaction=t, decision=decisions.get(t.txn_id)) for t in txns],
    )


@app.get("/api/transaction/{txn_id}", response_model=InspectResult)
def inspect(txn_id: str) -> InspectResult:
    d, ev = _current()
    txn = next((t for t in art.load_transactions(d) if t.txn_id == txn_id), None)
    if txn is None:
        raise HTTPException(status_code=404, detail=f"no transaction {txn_id} in {ev.manifest.run_id}")

    cf_path = d / "counterfactual_sample.json"
    cf = Counterfactual.model_validate_json(cf_path.read_text(encoding="utf-8")) if cf_path.exists() else None

    return InspectResult(
        run_id=ev.manifest.run_id,
        is_fixture=ev.manifest.is_fixture,
        transaction=txn,
        decision=art.load_decisions(d).get(txn_id),
        counterfactual=cf if cf and cf.txn_id == txn_id else None,
        shap=None,             # BLOCK 3
        intent_breakdown=None,  # BLOCK 5
        neighbours=None,        # BLOCK 4
    )


_cached_decisions_run_id: str | None = None
_cached_decisions: dict[str, BlueDecision] | None = None


def _get_decisions(d: Path, run_id: str) -> dict[str, BlueDecision]:
    global _cached_decisions_run_id, _cached_decisions
    if _cached_decisions_run_id != run_id or _cached_decisions is None:
        _cached_decisions = art.load_decisions(d)
        _cached_decisions_run_id = run_id
    return _cached_decisions


@app.post("/api/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> ScoreResponse:
    """Score one transaction. This is the endpoint we time for the latency claim."""
    t0 = time.perf_counter()
    try:
        from mcdl.blue.model import score_one  # type: ignore[attr-defined]

        decision = score_one(req.transaction)
        served_by = "mcdl.blue.model"
    except (ImportError, AttributeError):
        d, ev = _current()
        if not ev.manifest.is_fixture:
            decisions = _get_decisions(d, ev.manifest.run_id)
            if req.transaction.txn_id in decisions:
                decision = decisions[req.transaction.txn_id]
                served_by = f"artifact-backed ({ev.manifest.run_id})"
            else:
                decision = BlueDecision(
                    txn_id=req.transaction.txn_id,
                    risk_score=0.0,
                    calibrated_score=0.0,
                    decision="ALLOW",  # type: ignore[arg-type]
                    reason_codes=["STANDARD_LOW_RISK_PROFILE"],
                    model_version=ev.manifest.run_id,
                )
                served_by = f"default-allow ({ev.manifest.run_id})"
        else:
            decision = BlueDecision(
                txn_id=req.transaction.txn_id,
                risk_score=0.0,
                calibrated_score=0.0,
                decision="ALLOW",  # type: ignore[arg-type]
                reason_codes=["MODEL_NOT_BUILT"],
                model_version="none",
            )
            served_by = "placeholder (BLOCK 3 not built)"
    return ScoreResponse(
        decision=decision,
        served_by=served_by,
        api_latency_ms=round((time.perf_counter() - t0) * 1000, 3),
    )



@app.get("/api/coevolution")
def coevolution() -> dict:
    _, ev = _current()
    return {
        "run_id": ev.manifest.run_id,
        "is_fixture": ev.manifest.is_fixture,
        "rounds": [r.model_dump(mode="json") for r in ev.rounds],
    }


@app.get("/api/evidence", response_model=EvaluationResult)
def evidence() -> EvaluationResult:
    _, ev = _current()
    return ev


@app.post("/api/attack")
def attack(payload: dict) -> dict:
    """Run the Red engine on demand. BLOCK 4."""
    try:
        from mcdl.red.search import run_attack  # type: ignore[attr-defined]
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Red engine not built yet (BLOCK 4). The UI should disable this control.",
        ) from None
    return run_attack(**payload)


@app.get("/api/config")
def config() -> dict:
    cfg = load_config()
    return {
        "scale": cfg["scale"],
        "families": cfg["red"]["families"],
        "hidden_from_blue": cfg["red"]["hidden_from_blue"],
        "query_budgets": cfg["red"]["query_budgets"],
        "config_hash": cfg.hash,
    }


# --------------------------------------------------------------------------- #
# Static frontend - MUST be mounted last (see module docstring)
# --------------------------------------------------------------------------- #

_DIST = REPO_ROOT / "frontend" / "dist"

if _DIST.is_dir():
    # Hashed bundles, fonts, images.
    app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        """Serve index.html for any non-API path so client-side routing survives a
        refresh. Without this, a judge reloading on /evidence gets a 404 - the app
        works only if you never touch the address bar.

        An unknown /api/* path must still 404 as JSON. Letting the catch-all return
        HTML there turns a typo'd endpoint into an unreadable JSON parse error in
        the browser instead of an obvious 404.

        A real file wins over the fallback so favicons and similar still resolve.
        """
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail=f"no such API route: /{full_path}")

        candidate = (_DIST / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(_DIST.resolve()):
            return FileResponse(candidate)
        return FileResponse(_DIST / "index.html")

else:

    @app.get("/")
    def _no_frontend() -> dict:
        return {
            "status": "api only",
            "detail": "frontend/dist not found. Run `cd frontend && npm run build`.",
            "try": ["/api/health", "/api/evidence", "/docs"],
        }
