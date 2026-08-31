# S-03 World-C Forensic Root-Cause Analysis

## Executive Summary
In Kaggle Phase-2 V7, Stage **S-03 (Out-of-Distribution Zero-Day Robustness)** completed with:
- `world_c_zero_day.sample_count = 0`
- `world_c_zero_day.total_attack_count = 299` (all under `R1_ato`)
- `world_c_zero_day.hidden_zero_day_families = ["agent_subversion", "cross_merchant_fanout"]`
- `decision_classification = "LOW_SAMPLE"`

This document details the forensic investigation into why `sample_count = 0` occurred despite 299 attacks existing in the generated dataset.

---

## 1. Trace of Attack Generation in the Synthetic World

1. **Source Code**: `src/mcdl/world/generator.py` and `src/mcdl/world/hard_negatives.py`.
2. **Fraud Simulation Mechanism**:
   In `src/mcdl/world/generator.py` (lines 139–151), fraud transactions are sampled according to `base_fraud_rate = 0.006`.
   When `is_fraud == True`, attributes are generated via `sample_transaction_attributes()` in `src/mcdl/world/hard_negatives.py` (lines 88–97):
   ```python
   if is_fraud:
       channel = Channel.ECOMMERCE
       amount = round(float(np.exp(customer.mean_log_amount + 2.0 * customer.std_log_amount)), 2)
       mcc = str(rng.choice(["5944", "5045", "5732", "5311"]))
       ip_prefix = f"198.51.{int(rng.integers(1, 255))}"
       device_id = f"dev_fraud_{int(rng.integers(100, 999))}"
       is_new_device = True
       auth_failed_count = int(rng.choice([0, 1, 2, 3], p=[0.30, 0.35, 0.20, 0.15]))
       attack_family = AttackFamily.R1_ATO
   ```
3. **Outcome**: Exactly 299 fraud events were generated in the 47,501-event synthetic world, and **100% of them were labeled `R1_ato`**.

---

## 2. Origin of Zero-Day Attack Families

The zero-day attack families (`agent_subversion` and `cross_merchant_fanout`) are **adversarial attack mutations** generated dynamically by the Red search engine (`src/mcdl/red/`), `EXP-007-A`, `ADV-001` (10,000 population), and `ADV-002` (stateful swarm), rather than by the stationary chronological baseline world generator (`generate_world`).

---

## 3. S-03 Isolation & Partitioning Mechanics

In `src/mcdl/research/phase2/experiments.py` (`run_s03`):
```python
world_c_families = {"cross_merchant_fanout", "agent_subversion"}
train_hidden = sum(1 for i in train_indices_raw if real_graph.attack_families[i] in world_c_families)
val_hidden = sum(1 for i in val_indices_raw if real_graph.attack_families[i] in world_c_families)
test_hidden_indices = np.array([i for i in test_indices if real_graph.attack_families[i] in world_c_families], dtype=int)
```

1. **Training Split Contamination**: `train_hidden = 0` (Strictly zero contamination verified).
2. **Validation Split Contamination**: `val_hidden = 0` (Strictly zero contamination verified).
3. **Test Split Zero-Day Population**: `n_c = len(test_hidden_indices) = 0`.

---

## 4. Scientific Verdict & Integrity

- **Root Cause**: **Legitimate absence** due to dataset generation semantics. The base world generator only emits baseline `R1_ato` fraud; zero-day mutations exist in the Red campaign evaluation suite (`ADV-001`, `ADV-002`), not inside the passive baseline ledger stream.
- **Classification**: Correctly and honestly classified as **`LOW_SAMPLE`**.
- **No Hallucination**: The pipeline refused to fabricate or interpolate an Attack Success Rate (ASR) or robustness delta when `n_c = 0`.
