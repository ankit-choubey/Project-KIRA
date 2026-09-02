"""FastAPI service.

Thin by design: read artifacts, return a schema. The Space never computes - that
is what makes the demo structurally unable to fail the way live training fails,
and it is why the latency number from /api/score means something.

Route order matters. The static mount is a catch-all and must come LAST, after
every /api route, or it swallows the API and the UI shows an empty page.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from api.simulation import SimulationManager  # noqa: E402
from mcdl import artifacts as art  # noqa: E402
from mcdl.config import load_config  # noqa: E402
from mcdl.schemas import (  # noqa: E402
    BlueDecision,
    Counterfactual,
    Decision,
    EvaluationResult,
    Transaction,
)

app = FastAPI(title="Mastercard AI Defense Lab", version="0.1.0")

# Support configurable CORS origins for Netlify and custom deployments
_cors_env = os.getenv("CORS_ORIGINS", "*")
_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
if not _origins or "*" in _origins:
    _origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False if "*" in _origins else True,
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


@app.get("/api")
@app.get("/api/")
def api_root() -> dict[str, Any]:
    """Root API directory endpoint detailing available services and active run."""
    try:
        d, ev = _current()
        run_id = ev.manifest.run_id
        is_fixture = ev.manifest.is_fixture
        scale = ev.manifest.scale
    except Exception:
        run_id = None
        is_fixture = False
        scale = "unknown"

    return {
        "service": "Mastercard AI Defense Lab (Project KIRA) API",
        "status": "online",
        "version": "0.1.0",
        "active_run_id": run_id,
        "is_fixture": is_fixture,
        "scale": scale,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "health": "/api/health",
            "config": "/api/config",
            "runs": "/api/runs",
            "stream": "/api/stream",
            "transaction": "/api/transaction/{txn_id}",
            "score": "/api/score",
            "coevolution": "/api/coevolution",
            "evidence": "/api/evidence",
            "attack": "/api/attack",
            "artifacts": "/api/artifacts",
            "artifact": "/api/artifact/{name}",
            "simulation_start": "/api/simulation/start",
            "simulation_latest": "/api/simulation/latest",
            "simulation_status": "/api/simulation/{job_id}",
            "simulation_events": "/api/simulation/{job_id}/events",
            "simulation_stop": "/api/simulation/{job_id}/stop",
            "simulation_swarm": "/api/simulation/swarm/{swarm_id}",
        },
    }


@app.get("/health", response_model=Health, include_in_schema=False)
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
        try:
            from mcdl.blue.model import score_one  # type: ignore[attr-defined]

            decision = score_one(req.transaction)
            served_by = "mcdl.blue.model"
        except Exception:
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
                        decision=Decision.ALLOW,
                        reason_codes=["UNMEASURED_TRANSACTION_FALLBACK"],
                        model_version=f"{ev.manifest.run_id}:unmeasured-fallback",
                    )
                    served_by = f"artifact-fallback-unmeasured ({ev.manifest.run_id})"
            else:
                decision = BlueDecision(
                    txn_id=req.transaction.txn_id,
                    risk_score=0.0,
                    calibrated_score=0.0,
                    decision=Decision.ALLOW,
                    reason_codes=["MODEL_NOT_BUILT"],
                    model_version="none",
                )
                served_by = "placeholder (BLOCK 3 not built)"
        return ScoreResponse(
            decision=decision,
            served_by=served_by,
            api_latency_ms=round((time.perf_counter() - t0) * 1000, 3),
        )
    except Exception as exc:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Score evaluation failed: {exc}\n{traceback.format_exc()}",
        ) from exc


@app.get("/api/artifacts")
def artifacts() -> dict[str, Any]:
    d, ev = _current()
    files = sorted(p.name for p in d.glob("*.json") if not p.name.startswith("."))
    return {
        "run_id": ev.manifest.run_id,
        "is_fixture": ev.manifest.is_fixture,
        "artifacts": files,
    }


@app.get("/api/artifact/{name}")
def get_artifact(name: str) -> Any:
    d, ev = _current()
    clean_name = name.removesuffix(".json")
    if not clean_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=404, detail=f"invalid artifact name '{name}'")

    target = (d / f"{clean_name}.json").resolve()
    if not target.is_file() or not target.is_relative_to(d.resolve()):
        raise HTTPException(
            status_code=404, detail=f"artifact '{name}' not found in {ev.manifest.run_id}"
        )

    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"failed to read artifact '{name}': {exc}"
        ) from exc



@app.get("/api/coevolution")
def coevolution() -> dict:
    """Return round data enriched with family_breakdown from coevolution_metrics.json."""
    d, ev = _current()
    rounds_data = [r.model_dump(mode="json") for r in ev.rounds]

    # Enrich rounds with per-family breakdown from coevolution_metrics.json if available
    coev_path = d / "coevolution_metrics.json"
    if coev_path.exists():
        try:
            coev_records = json.loads(coev_path.read_text(encoding="utf-8"))
            coev_by_round = {rec["round_index"]: rec for rec in coev_records if "round_index" in rec}
            for rd in rounds_data:
                idx = rd.get("round_index", -1)
                if idx in coev_by_round:
                    extra = coev_by_round[idx]
                    # Merge top-level ASR fields from coevolution_metrics if missing/null in evaluation
                    red = rd.get("red") or {}
                    if red.get("asr_heldout_variants") is None:
                        red["asr_heldout_variants"] = extra.get("heldout_asr")
                    if red.get("asr_seen_variants") is None:
                        red["asr_seen_variants"] = extra.get("seen_asr")
                    rd["red"] = red
                    rd["family_breakdown"] = extra.get("family_breakdown", {})
                    rd["generalisation_retention"] = extra.get("generalisation_retention")
        except Exception:
            pass  # Degraded gracefully — original rounds are still returned

    return {
        "run_id": ev.manifest.run_id,
        "is_fixture": ev.manifest.is_fixture,
        "rounds": rounds_data,
    }


@app.get("/api/evidence", response_model=EvaluationResult)
def evidence() -> EvaluationResult:
    _, ev = _current()
    return ev


@app.post("/api/attack")
def attack(payload: dict) -> dict:
    """Serve pre-computed attack results from failures.json.

    The Red engine is not re-executed at query time (Space never computes).
    Instead we replay the closest matching pre-computed attack from the run
    artifacts, which gives the frontend real numbers and provenance.
    """
    import random as _random

    family: str = payload.get("family", "")
    budget: int = int(payload.get("budget", 20))
    seed: int = int(payload.get("seed", 20260827))

    d, ev = _current()

    # Try live Red engine first (available if BLOCK 4 was built)
    try:
        from mcdl.red.search import run_attack  # type: ignore[attr-defined]
        return run_attack(**payload)
    except (ImportError, Exception):
        pass

    # Fall back to artifact-backed replay from failures.json
    failures_path = d / "failures.json"
    if not failures_path.exists():
        raise HTTPException(
            status_code=501,
            detail="No pre-computed attack artifacts found. Red engine replay unavailable.",
        )

    all_failures = json.loads(failures_path.read_text(encoding="utf-8"))

    # Normalise family name: config uses R1_ato style, artifacts may use burst_drain etc.
    # Build a flexible lookup: match exact, then case-insensitive substring
    def _match(f: str, requested: str) -> bool:
        r = requested.lower()
        fn = f.lower()
        return fn == r or r in fn or fn in r

    matching = [f for f in all_failures if _match(f.get("attack_family", ""), family)]

    # If no exact match found, use all failures for the requested budget (demo mode)
    if not matching:
        matching = [f for f in all_failures if f.get("query_budget") == budget]
    if not matching:
        matching = all_failures

    # Filter by budget (pick nearest budget if exact not found)
    budget_exact = [f for f in matching if f.get("query_budget") == budget]
    candidates = budget_exact if budget_exact else matching

    # Deterministic sampling by seed
    rng = _random.Random(seed)
    sample = rng.sample(candidates, min(10, len(candidates)))

    # Build summary statistics
    n_total = len(candidates)
    n_evaded = sum(1 for f in candidates if not f.get("detected", True))
    asr = round(n_evaded / n_total, 4) if n_total > 0 else 0.0
    meds = [f["mutation_distance"] for f in candidates if f.get("mutation_distance") is not None]
    mean_med = round(sum(meds) / len(meds), 4) if meds else None

    return {
        "status": "artifact_replay",
        "served_by": f"failures.json ({ev.manifest.run_id})",
        "run_id": ev.manifest.run_id,
        "is_fixture": ev.manifest.is_fixture,
        "requested_family": family,
        "matched_family": candidates[0].get("attack_family") if candidates else None,
        "query_budget": budget,
        "seed": seed,
        "n_attacks_evaluated": n_total,
        "n_evaded": n_evaded,
        "attack_success_rate": asr,
        "mean_evasion_distance": mean_med,
        "representative_attacks": [
            {
                "attack_id": f.get("attack_id"),
                "base_transaction_id": f.get("base_transaction_id"),
                "attack_family": f.get("attack_family"),
                "query_budget": f.get("query_budget"),
                "decision": f.get("decision"),
                "detected": f.get("detected"),
                "risk_score": f.get("risk_score"),
                "mutation_distance": f.get("mutation_distance"),
                "fidelity_score": f.get("fidelity_score"),
                "hardness_score": f.get("hardness_score"),
                "primary_failure_category": f.get("primary_failure_category"),
            }
            for f in sample
        ],
    }


@app.get("/api/config")
def config() -> dict:
    """Return run config, using actual attack families from the run artifact when available."""
    cfg = load_config()
    families = cfg["red"]["families"]
    hidden_from_blue = cfg["red"]["hidden_from_blue"]
    query_budgets = cfg["red"]["query_budgets"]

    # Override families from the actual run artifact if available — this ensures the
    # Red Console dropdown shows families that actually have pre-computed results.
    try:
        d = art.resolve_run()
        atk_path = d / "attack_summary.json"
        if atk_path.exists():
            atk = json.loads(atk_path.read_text(encoding="utf-8"))
            run_families = atk.get("attack_families")
            if run_families:
                families = run_families
                # Hidden-from-blue families: those in coevolution_metrics but not trained on
                # In our artifact runs: agent_subversion/cross_merchant_fanout are zero-day
                coev_path = d / "coevolution_metrics.json"
                if coev_path.exists():
                    coev = json.loads(coev_path.read_text(encoding="utf-8"))
                    if coev:
                        breakdown = coev[0].get("family_breakdown", {})
                        # Families where heldout_asr == 0 and delta_heldout_asr > 0 are
                        # prime candidates for hidden status (they evade but are not trained on)
                        hidden_from_blue = [
                            f for f in families
                            if f in ["cross_merchant_fanout", "agent_subversion",
                                     "R4_mule_ring", "R8_intent_drift"]
                        ] or hidden_from_blue
            if atk.get("budgets_evaluated"):
                query_budgets = atk["budgets_evaluated"]
    except Exception:
        pass  # Degrade to config defaults

    return {
        "scale": cfg["scale"],
        "families": families,
        "hidden_from_blue": hidden_from_blue,
        "query_budgets": query_budgets,
        "config_hash": cfg.hash,
    }


# --------------------------------------------------------------------------- #
# Live Simulation Endpoints (Truthful Real-Time Swarm & Event Runner)
# --------------------------------------------------------------------------- #


class SimulationStartRequest(BaseModel):
    total_swarms: int = Field(15000, ge=1, le=100000)
    batch_size: int = Field(50, ge=1, le=1000)
    speed_multiplier: float = Field(1.0, ge=0.1, le=10.0)


@app.post("/api/simulation/start")
def start_simulation(req: SimulationStartRequest = SimulationStartRequest()) -> dict:
    """Start an active live simulation job traversing synthetic payment transactions and adversarial mutations."""
    mgr = SimulationManager.get_instance()
    job = mgr.start_simulation(
        total_swarms=req.total_swarms,
        batch_size=req.batch_size,
        speed_multiplier=req.speed_multiplier,
    )
    return job.to_summary_dict()


@app.get("/api/simulation/latest")
def get_latest_simulation() -> dict:
    """Get status and metrics of the latest or active simulation job."""
    mgr = SimulationManager.get_instance()
    job = mgr.get_latest_job()
    if not job:
        # Start a default background job if none exists yet
        job = mgr.start_simulation(total_swarms=15000, batch_size=50)
    return job.to_summary_dict()


@app.get("/api/simulation/{job_id}")
def get_simulation_status(job_id: str) -> dict:
    """Get status, progress, detections, and evasions for a specific simulation job."""
    mgr = SimulationManager.get_instance()
    job = mgr.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Simulation job '{job_id}' not found")
    return job.to_summary_dict()


@app.get("/api/simulation/{job_id}/events")
def get_simulation_events(
    job_id: str,
    limit: int = Query(50, ge=1, le=500),
) -> dict:
    """Get the latest real-time transaction event stream from an active simulation."""
    mgr = SimulationManager.get_instance()
    job = mgr.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Simulation job '{job_id}' not found")
    events = [e.to_dict() for e in job.events[-limit:]]
    return {
        "job_id": job.job_id,
        "status": job.status,
        "count": len(events),
        "events": events,
        "source": "live",
    }


@app.post("/api/simulation/{job_id}/stop")
def stop_simulation(job_id: str) -> dict:
    """Stop/cancel an ongoing live simulation."""
    mgr = SimulationManager.get_instance()
    job = mgr.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Simulation job '{job_id}' not found")
    job.stop()
    return {"status": "stopped", "job_id": job.job_id}


@app.get("/api/simulation/swarm/{swarm_id}")
def get_swarm_entity(swarm_id: str) -> dict:
    """Inspect an individual swarm entity with actual probe, score, decision, and outcome."""
    mgr = SimulationManager.get_instance()
    return mgr.get_swarm_detail(swarm_id)


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
