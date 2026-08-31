# Project KIRA — Backend API & Deployment Handoff for Devraj

**Handoff Date:** 2026-08-31T22:30:00Z  
**Authoritative Baseline Run:** `run_tiny_s20260827_193f7897_40997ab` (Commit `40997ab`)  
**Backend Deployment Engine:** FastAPI on Hugging Face Spaces (Docker SDK / CPU Basic)  

---

## 1. Backend Service URLs

- **Hugging Face Space Live URL:** `https://ankit-choubey-project-kira.hf.space`
- **Hugging Face Space Repository:** `https://huggingface.co/spaces/ankit-choubey/Project-KIRA`
- **API Base URL:** `https://ankit-choubey-project-kira.hf.space/api`
- **Interactive OpenAPI Docs:** `https://ankit-choubey-project-kira.hf.space/docs`

---

## 2. API Contract & Endpoints Summary

| Method | Endpoint | Description / Purpose | Key Query/Body Parameters |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/health` | Runtime and artifact loading status | None |
| **GET** | `/api/runs` | List of available evaluated runs | None |
| **GET** | `/api/stream` | Paginated transaction stream with decisions | `offset` (int, default 0), `limit` (int, default 100, max 1000) |
| **GET** | `/api/transaction/{txn_id}` | Detailed inspection of a specific transaction | Path param `txn_id` |
| **POST** | `/api/score` | Score / evaluate transaction against model/artifacts | Body: `{"transaction": TransactionSchema}` |
| **GET** | `/api/coevolution` | Multi-round defensive co-evolution results | None |
| **GET** | `/api/evidence` | Comprehensive multi-layer evaluation result | None |
| **POST** | `/api/attack` | On-demand adversarial red attack simulation | Body: `{"source_txn": ...}` |
| **GET** | `/api/config` | Public configuration & parameters | None |
| **GET** | `/api/artifacts` | Inventory of available JSON artifact files | None |
| **GET** | `/api/artifact/{name}` | Direct JSON content of a specific artifact | Path param `name` (e.g. `scoreboard`, `external_anchor`) |

---

## 3. Serving Semantics & Score Endpoint Behavior

The backend operates strictly as an **artifact-backed evidence serving API**. When transactions are submitted to `POST /api/score`:

1. **Known Authoritative Transactions ($N=9,348$):**
   - Returns the exact pre-computed, cryptographically verified `BlueDecision`.
   - `served_by`: `artifact-backed (run_tiny_s20260827_193f7897_40997ab)`
2. **Arbitrary / Unknown Transactions:**
   - Returns a governed fallback response rather than a hallucinated score.
   - `served_by`: `artifact-fallback-unmeasured (run_tiny_s20260827_193f7897_40997ab)`
   - `reason_codes`: `["UNMEASURED_TRANSACTION_FALLBACK"]`
   - `decision`: `"ALLOW"`

---

## 4. Scientific Classification & Metric Display Rules

Every numeric field in the API is nullable. **`null` signifies `NOT MEASURED` and must never be coerced or rendered as `0` or `0.00%`.**

The frontend must adhere to the following taxonomy:

- **`VERIFIED`**: Cryptographically bound to an on-disk execution artifact with verified integrity.
- **`MEASURED_WITH_CAVEAT`**: Empirically computed, but subject to specific scope limitations (e.g. baseline PR-AUC = 1.0 due to 5 positive test samples; loopback latency = 2.3ms in-process).
- **`FAILURE_FINDING`**: Genuinely negative scientific result demonstrating model limits (e.g. Zero-Day Hidden Family ASR = 100.0%).
- **`INCONCLUSIVE`**: Statistical test does not reject null hypothesis (e.g. Graph Fusion G-03 $p = 0.156$; Intent Ablation $\Delta\text{ASR} = 0.0\%$).
- **`LOW_SAMPLE`**: Sample count insufficient for statistical significance.
- **`NOT_MEASURED`**: Metric was not evaluated (render as muted / unmeasured state, never zero).
- **`NOT_RUN`**: Full scale pipeline run was not scheduled.

---

## 5. Explicit Prohibitions for Frontend Presentation

To ensure the submission remains defensible under technical audit, the UI must **NOT**:

1. **Never fabricate or interpolate metrics**: Only display numbers received from `/api/` or verified artifact JSONs.
2. **Never claim PR-AUC = 1.000 as a production capability**: Always present the tiny sample caveat (5 positive test cases) alongside the scaled small result (PR-AUC = 0.9375).
3. **Never claim 100% defense against zero-day attacks**: EXP-007-E / S-03 proved 100% vulnerability against withheld topologies.
4. **Never call local ASGI latency "production network latency"**: P95 = 2.30ms is an in-process loopback benchmark.
5. **Never describe synthetic Sparkov cardholders as Mastercard production data**: It is CC0 open-source benchmark data.
6. **Never present AG-001 as live LLM reasoning**: The backend executed under deterministic heuristic fallback.

---

## 6. Example Request & Response Payloads

### `GET /api/health`
```json
{
  "status": "ok",
  "run_id": "run_tiny_s20260827_193f7897_40997ab",
  "is_fixture": false,
  "artifacts_loaded": true,
  "detail": "scale=tiny commit=40997ab"
}
```

### `POST /api/score`
```json
// Request
{
  "transaction": {
    "txn_id": "tx_00000000",
    "customer_id": "cust_000000",
    "merchant_id": "merch_000000",
    "device_id": "dev_000000",
    "timestamp": "2026-08-27T00:00:00",
    "amount": 42.50,
    "mcc": "5411",
    "channel": "pos",
    "lat": 40.7128,
    "lon": -74.0060,
    "ip_prefix": "192.168.1",
    "is_new_device": false,
    "auth_failed_count": 0,
    "agent_id": null,
    "mandate_id": null,
    "balance_before": 1000.0,
    "available_credit": 4000.0,
    "is_fraud": false,
    "attack_family": null,
    "attack_instance_id": null,
    "attack_variant": null,
    "hard_negative": "NONE"
  }
}

// Response
{
  "decision": {
    "txn_id": "tx_00000000",
    "risk_score": 0.012,
    "calibrated_score": 0.005,
    "decision": "ALLOW",
    "reason_codes": [],
    "intent_drift_score": null,
    "model_version": "0.1.0",
    "feature_version": "0.1.0",
    "policy_version": "0.1.0",
    "latency_ms": 0.0
  },
  "served_by": "artifact-backed (run_tiny_s20260827_193f7897_40997ab)",
  "api_latency_ms": 0.45
}
```

---

## 7. Verification & Sanity Test Results

- `pytest tests/e2e/test_api.py`: **27/27 PASS**
- `pytest tests/unit/evidence/test_evidence.py`: **3/3 PASS**
- Baseline Cryptographic Hash Audit: **22/22 PASS**
- Path Traversal & Injection Check: **PASS (404 on invalid/traversal queries)**
- Frontend Static Build: **`built in 300ms`**
