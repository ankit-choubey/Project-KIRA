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

