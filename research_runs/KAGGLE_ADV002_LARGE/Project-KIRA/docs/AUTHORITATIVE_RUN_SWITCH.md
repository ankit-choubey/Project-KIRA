# Authoritative Run Switch Protocol

**Document Version**: 1.0.0  
**Target Run**: `KAGGLE_PHASE2_V7`  
**Current Baseline Pointer**: `artifacts/run_tiny_s20260827_193f7897_40997ab` (`artifacts/LATEST` -> `run_fixture_0000`)  

---

## 1. Overview & Pre-Conditions

This document defines the procedure to promote `KAGGLE_PHASE2_V7` to authoritative status after Devraj's frontend merge and verification.

### Pre-Switch Checklist:
- [x] V7 Research execution completed on Kaggle CPU (`KernelWorkerStatus.COMPLETE`).
- [x] All 14 stages (`S00`–`S04`) completed and validated.
- [x] `research_runs/KAGGLE_PHASE2_V7/FINAL/v7_evidence_manifest.json` generated with SHA-256 signatures.
- [x] 22/22 Authoritative baseline artifacts verified (`PASS`).
- [x] Claim registry audited and bounded in `docs/FINAL_CLAIM_REGISTRY.md`.
- [x] Null, `LOW_SAMPLE`, and `NOT_MEASURED` serialization safety verified by automated tests.
- [ ] Devraj's frontend merge completed and verified.

---

## 2. Pointer Status & Paths

- **Current `artifacts/LATEST`**: `run_fixture_0000` (fixture testing mode)
- **Authoritative Baseline Directory**: `artifacts/run_tiny_s20260827_193f7897_40997ab/`
- **Proposed V7 Expansion Directory**: `research_runs/KAGGLE_PHASE2_V7/FINAL/`

---

## 3. Exact Switch Commands

When Devraj's frontend is ready, execute:

```bash
# 1. Switch LATEST pointer to authoritative baseline run
echo "run_tiny_s20260827_193f7897_40997ab" > artifacts/LATEST

# 2. Generate production stream.json from authoritative baseline
python3 tools/build_stream_json.py artifacts/run_tiny_s20260827_193f7897_40997ab --output frontend/public/stream.json

# 3. Verify baseline integrity
python3 -c "
from mcdl.research.phase2.validation import verify_authoritative_baseline_integrity
from pathlib import Path
rep = verify_authoritative_baseline_integrity(Path('artifacts/run_tiny_s20260827_193f7897_40997ab'))
assert rep['status'] == 'PASS', f'Integrity failure: {rep}'
print('Baseline 22/22 verification: PASS')
"

# 4. Run backend contract tests against authoritative run
pytest tests/e2e/test_api.py -v
```

---

## 4. Rollback Command

If any contract or integration failure occurs:

```bash
# Rollback LATEST to fixture mode
echo "run_fixture_0000" > artifacts/LATEST

# Verify fixture health
pytest tests/e2e/test_api.py -v
```
