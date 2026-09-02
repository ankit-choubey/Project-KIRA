"""API contract tests.

These run against fixtures, so they work from a clean clone before the simulator
or any model exists. They cover the two routing bugs that would only show up in
front of a judge: deep links 404-ing on refresh, and the static catch-all
swallowing unknown API routes into HTML.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcdl.config import REPO_ROOT
import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DIST = REPO_ROOT / "frontend" / "dist"


@pytest.fixture(scope="module")
def client() -> TestClient:
    from mcdl.artifacts import artifacts_dir
    from mcdl.fixtures import make_fixtures

    make_fixtures(artifacts_dir())
    from api.main import app

    return TestClient(app)


class TestHealth:
    def test_health_ok(self, client):
        body = client.get("/api/health").json()
        assert body["status"] == "ok"
        assert body["artifacts_loaded"] is True

    def test_health_surfaces_fixture_flag(self, client):
        # The UI keys its FIXTURE banner off this. If it stops being surfaced,
        # placeholder numbers start looking like measurements.
        assert client.get("/api/health").json()["is_fixture"] is True

    def test_runs_endpoint(self, client):
        body = client.get("/api/runs").json()
        assert "runs" in body
        assert isinstance(body["runs"], list)


class TestStream:
    def test_returns_rows_and_total(self, client):
        body = client.get("/api/stream?offset=0&limit=5").json()
        assert len(body["rows"]) == 5
        assert body["total"] > 5

    def test_rows_carry_decisions(self, client):
        for row in client.get("/api/stream?limit=20").json()["rows"]:
            assert row["decision"]["txn_id"] == row["transaction"]["txn_id"]

    def test_limit_is_bounded(self, client):
        assert client.get("/api/stream?limit=99999").status_code == 422
        assert client.get("/api/stream?offset=-1").status_code == 422


class TestInspect:
    def test_known_transaction(self, client):
        txn_id = client.get("/api/stream?limit=1").json()["rows"][0]["transaction"]["txn_id"]
        body = client.get(f"/api/transaction/{txn_id}").json()
        assert body["transaction"]["txn_id"] == txn_id

    def test_unmeasured_fields_are_null(self, client):
        # Not 0, not {}. The UI renders null as "not measured".
        txn_id = client.get("/api/stream?limit=1").json()["rows"][0]["transaction"]["txn_id"]
        body = client.get(f"/api/transaction/{txn_id}").json()
        assert body["shap"] is None
        assert body["intent_breakdown"] is None

    def test_unknown_transaction_404s(self, client):
        assert client.get("/api/transaction/NOPE").status_code == 404


class TestEvidence:
    def test_evidence_validates(self, client):
        body = client.get("/api/evidence").json()
        assert body["manifest"]["is_fixture"] is True
        assert len(body["rounds"]) == 3

    def test_anchor_absent_until_measured(self, client):
        assert client.get("/api/evidence").json()["anchor"] is None

    def test_coevolution_separates_seen_from_heldout(self, client):
        for r in client.get("/api/coevolution").json()["rounds"]:
            assert r["red"]["asr_seen_variants"] is not None
            assert r["red"]["asr_heldout_variants"] is not None


class TestUnbuiltBlocks:
    def test_score_is_honest_about_missing_model(self, client):
        txn = client.get("/api/stream?limit=1").json()["rows"][0]["transaction"]
        body = client.post("/api/score", json={"transaction": txn}).json()
        assert "MODEL_NOT_BUILT" in body["decision"]["reason_codes"]
        assert "placeholder" in body["served_by"]

    def test_score_response_schema_completeness(self, client):
        txn = client.get("/api/stream?limit=1").json()["rows"][0]["transaction"]
        res = client.post("/api/score", json={"transaction": txn})
        assert res.status_code == 200
        body = res.json()
        assert "decision" in body
        assert "served_by" in body
        assert "api_latency_ms" in body
        assert isinstance(body["api_latency_ms"], float)
        assert body["decision"]["decision"] in ("ALLOW", "STEP_UP", "BLOCK")

    def test_attack_501s_until_red_exists(self, client):
        assert client.post("/api/attack", json={"family": "R1_ato"}).status_code == 501

    def test_config_endpoint_returns_valid_structure(self, client):
        res = client.get("/api/config")
        assert res.status_code == 200
        body = res.json()
        assert "scale" in body
        assert "families" in body
        assert "hidden_from_blue" in body
        assert "query_budgets" in body


class TestGenericArtifacts:
    def test_artifacts_list(self, client):
        res = client.get("/api/artifacts")
        assert res.status_code == 200
        body = res.json()
        assert "run_id" in body
        assert "artifacts" in body
        assert isinstance(body["artifacts"], list)
        assert "manifest.json" in body["artifacts"] or "evaluation.json" in body["artifacts"]

    def test_get_artifact_known(self, client):
        res = client.get("/api/artifact/evaluation")
        assert res.status_code == 200
        data = res.json()
        assert "manifest" in data or "rounds" in data

        # Also support explicit .json suffix
        res_ext = client.get("/api/artifact/evaluation.json")
        assert res_ext.status_code == 200
        assert res_ext.json() == data

    def test_get_artifact_unknown_404s(self, client):
        res = client.get("/api/artifact/nonexistent_file")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_get_artifact_path_traversal_blocked(self, client):
        # Traversal attempts should be blocked and 404
        res = client.get("/api/artifact/..%2F..%2Fmain")
        assert res.status_code == 404

        res2 = client.get("/api/artifact/.env")
        assert res2.status_code == 404


class TestScoreFallbackSemantics:
    def test_fallback_on_unknown_transaction_in_real_run(self, client, monkeypatch):
        # Emulate non-fixture run without live model to verify fallback label
        from datetime import datetime, timezone
        from api import main
        from mcdl.schemas import RunManifest, EvaluationResult, FidelityReport

        mock_manifest = RunManifest(
            run_id="run_tiny_mock",
            created_at=datetime.now(timezone.utc),
            scale="tiny",
            is_fixture=False,
            git_commit="mock_commit",
            config_hash="mock_hash",
            seed=20260827,
        )
        mock_fidelity = FidelityReport(l1_violations=0)
        mock_eval = EvaluationResult(manifest=mock_manifest, fidelity=mock_fidelity, rounds=[])
        monkeypatch.setattr(main, "_current", lambda: (REPO_ROOT / "artifacts" / "run_fixture_0000", mock_eval))
        monkeypatch.setattr(main, "_get_decisions", lambda d, r: {})

        txn = client.get("/api/stream?limit=1").json()["rows"][0]["transaction"]
        txn["txn_id"] = "TXN_UNKNOWN_9999"

        res = client.post("/api/score", json={"transaction": txn})
        assert res.status_code == 200
        body = res.json()
        assert "artifact-fallback-unmeasured" in body["served_by"]
        assert "UNMEASURED_TRANSACTION_FALLBACK" in body["decision"]["reason_codes"]
        assert "unmeasured-fallback" in body["decision"]["model_version"]


@pytest.mark.skipif(not DIST.is_dir(), reason="frontend not built; run `make frontend`")
class TestStaticRouting:
    """The two bugs that only appear in front of a judge."""

    @pytest.mark.parametrize("path", ["/", "/monitor", "/evidence", "/inspect/T0000001"])
    def test_deep_links_serve_the_app(self, client, path):
        # BrowserRouter uses the history API, so a refresh on /evidence must not 404.
        res = client.get(path)
        assert res.status_code == 200
        assert '<div id="root">' in res.text

    def test_unknown_api_route_404s_as_json_not_html(self, client):
        # If the SPA catch-all swallows this, a typo'd endpoint surfaces in the
        # browser as an unreadable JSON parse error instead of an obvious 404.
        res = client.get("/api/nonexistent")
        assert res.status_code == 404
        assert res.headers["content-type"].startswith("application/json")

    def test_api_still_wins_over_static(self, client):
        res = client.get("/api/health")
        assert res.headers["content-type"].startswith("application/json")

    def test_api_root_returns_json_directory(self, client):
        res = client.get("/api")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("application/json")
        body = res.json()
        assert "endpoints" in body
        assert body["status"] == "online"

    def test_health_alias_returns_json(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("application/json")
        body = res.json()
        assert "status" in body


class TestLiveSimulation:
    """Verification of truthful live simulation endpoints."""

    def test_simulation_lifecycle(self, client):
        # 1. Start simulation
        start_res = client.post(
            "/api/simulation/start",
            json={"total_swarms": 200, "batch_size": 25, "speed_multiplier": 5.0},
        )
        assert start_res.status_code == 200
        job_data = start_res.json()
        assert "job_id" in job_data
        assert job_data["status"] == "running"
        assert job_data["total_swarms"] == 200
        assert job_data["source"] == "live"
        job_id = job_data["job_id"]

        # 2. Get status
        status_res = client.get(f"/api/simulation/{job_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["job_id"] == job_id
        assert status_data["processed_swarms"] >= 0

        # 3. Get latest simulation
        latest_res = client.get("/api/simulation/latest")
        assert latest_res.status_code == 200
        assert latest_res.json()["job_id"] == job_id

        # 4. Get events
        events_res = client.get(f"/api/simulation/{job_id}/events?limit=10")
        assert events_res.status_code == 200
        events_data = events_res.json()
        assert "events" in events_data
        assert events_data["source"] == "live"

        # 5. Get individual swarm
        swarm_res = client.get("/api/simulation/swarm/SWARM-000001")
        assert swarm_res.status_code == 200
        swarm_data = swarm_res.json()
        assert "swarm_id" in swarm_data
        assert "outcome" in swarm_data

        # 6. Stop simulation
        stop_res = client.post(f"/api/simulation/{job_id}/stop")
        assert stop_res.status_code == 200
        assert stop_res.json()["status"] == "stopped"

    def test_simulation_nonexistent_job_404(self, client):
        res = client.get("/api/simulation/nonexistent_job_12345")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()


