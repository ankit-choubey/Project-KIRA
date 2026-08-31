# ADV-003: Pre-Execution Architecture & Scientific Audit

## 1. Architectural Overview
- **Module**: `src/mcdl/research/advanced/adv003/`
- **Objective**: Evaluates whether Blue challengers learn from validated Red attack failures across sequential defense rounds without modifying production/baseline models.
- **Control Arms**:
  1. `static_blue`: Baseline detector frozen at Round 0; Red evolves against static defense.
  2. `adaptive_challenger`: Challenger ingests validated weakness profiles from prior round with strict promotion gating.
  3. `replay_control`: Challenger ingests arbitrary historical replay samples without targeted weakness validation.

## 2. Invariant & Safety Guarantees
- **Production Immutability**: Production Blue detector (`run_tiny_s20260827_193f7897_40997ab`) is read-only and never mutated.
- **Strict Disjointness**: Training targets, validation targets, legacy baseline targets, and held-out targets are strictly partitioned.
- **Promotion & Rollback**: Challengers failing validation ASR, legacy baseline ASR, or anti-forgetting thresholds ($\Delta > 0.05$) trigger immediate rollback.
- **Non-RL Determinism**: Attacker evolves via deterministic empirical weakness weighting.
