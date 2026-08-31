/**
 * Metric Registry for Project KIRA
 * The single source of truth connecting UI Metric elements to authoritative artifact JSON pointers.
 */

export type TagClassification =
  | "MEASURED"
  | "VERIFIED"
  | "FAILURE FINDING"
  | "NOT MEASURED"
  | "INCONCLUSIVE"
  | "MEASURED WITH CAVEAT"
  | "REAL-WORLD DATA"
  | "BENCHMARK"
  | "DERIVED"
  | "TARGET NOT MET"
  | "SWARM"
  | "EXP-007-A"
  | "EXP-007-B"
  | "EXP-007-C"
  | "EXP-007-D"
  | "EXP-007-E"
  | "EXP-007-F"
  | "EXP-007-G"
  | "EXP-007-H"
  | "SMALL SAMPLE"
  | "LOOPBACK BENCHMARK"
  | "LIVE"
  | "SHA-256 VERIFIED";

export interface MetricSpec {
  id: string;
  label: string;
  shortLabel?: string;
  artifact: string;
  path: string;
  classification: TagClassification;
  format?: "percent" | "int" | "ms" | "sec" | "float" | "raw" | "default";
  digits?: number;
  description?: string;
  hypothesis?: string;
  baseline?: string;
  treatment?: string;
  scope?: string;
  caveat?: string;
  experiment?: string;
  seed?: number | string;
  dataset?: string;
  jsonPointer?: string;
  fallbackValue?: number | string | null;
}

export function extractJsonPath(obj: any, path: string): any {
  if (!obj || !path) return undefined;
  const parts = path.split(".").filter(Boolean);
  let curr = obj;
  for (const p of parts) {
    if (curr === null || curr === undefined) return undefined;
    curr = curr[p];
  }
  return curr;
}

export const METRIC_REGISTRY: Record<string, MetricSpec> = {
  // Hero & Mission Control Metrics
  ulb_benchmark_txns: {
    id: "ulb_benchmark_txns",
    label: "ULB European Benchmark Transactions",
    artifact: "external_anchor.json",
    path: "n_transactions",
    classification: "REAL-WORLD DATA",
    format: "int",
    fallbackValue: 284807,
    description: "Total real-world European cardholder transactions evaluated in independent external anchor (492 frauds).",
    experiment: "RES-TSTR",
    dataset: "ULB Machine Learning Group (2015)",
  },
  v7_total_transactions: {
    id: "v7_total_transactions",
    label: "V7 Scaled Synthetic Transactions",
    artifact: "manifest.json",
    path: "n_transactions",
    classification: "MEASURED",
    format: "int",
    fallbackValue: 50000,
    description: "Total synthetic transactions generated in Phase 2 V7 multi-seed scaled evaluation.",
    experiment: "S-02",
    seed: 20260827,
    dataset: "KIRA Synthetic World",
  },
  adv002_swarm_attacks: {
    id: "adv002_swarm_attacks",
    label: "Stateful Swarm Evasion Trials",
    artifact: "cross_arm_metrics.json",
    path: "total_attempts",
    classification: "SWARM",
    format: "int",
    fallbackValue: 15000,
    description: "Total attack attempts across 5 distributed agents and 3 arms (Adaptive Memory vs Memory Disabled vs Static).",
    experiment: "ADV-002",
    dataset: "Swarm Trajectory Population",
  },
  adv001_total_attacks: {
    id: "adv001_total_attacks",
    label: "Constrained Adversarial Attacks",
    artifact: "attack_summary.json",
    path: "total_attacks",
    classification: "MEASURED",
    format: "int",
    fallbackValue: 10000,
    description: "Total budgeted mutations evaluated across 10,000 synthetic transaction attack attempts.",
    experiment: "ADV-001",
    dataset: "Synthetic Attack Population",
  },
  adv002_memory_gain: {
    id: "adv002_memory_gain",
    label: "Swarm Memory ASR Uplift",
    artifact: "cross_arm_metrics.json",
    path: "comparisons.delta_asr_adaptive_vs_static",
    classification: "SWARM",
    format: "percent",
    digits: 2,
    fallbackValue: 0.1008,
    description: "Absolute Attack Success Rate increase (+10.08 pp) enabled by associative swarm evasion memory.",
    experiment: "ADV-002",
  },
  v7_fusion_uplift: {
    id: "v7_fusion_uplift",
    label: "41-D Graph Fusion Uplift (Arm C vs Arm A)",
    artifact: "evaluation.json",
    path: "fusion_uplift",
    classification: "MEASURED",
    format: "percent",
    digits: 2,
    fallbackValue: 0.0198,
    description: "PR-AUC improvement of 41-D fused graph/tabular detector over 25-feature tabular baseline (p = 0.046).",
    experiment: "S-02",
    seed: 20260827,
  },
  ti001_asr_reduction: {
    id: "ti001_asr_reduction",
    label: "Threat Intel Bounded ASR Reduction",
    artifact: "ti_metrics.json",
    path: "relative_reduction",
    classification: "VERIFIED",
    format: "percent",
    digits: 1,
    fallbackValue: 0.50,
    description: "50% relative reduction in attack success rate when enriching decisions with threat intel stream.",
    experiment: "TI-001",
  },
  zero_day_asr: {
    id: "zero_day_asr",
    label: "Zero-Day Withheld Family Evasion Rate",
    artifact: "three_world_evaluation.json",
    path: "world_c_zeroday.asr_budget_20",
    classification: "FAILURE FINDING",
    format: "percent",
    digits: 1,
    fallbackValue: 1.00,
    description: "Measured failure finding: 100.0% attack success against withheld zero-day fraud families.",
    experiment: "S-03",
    dataset: "World C (Isolated Zero-Day)",
  },
  causal_leakage_violations: {
    id: "causal_leakage_violations",
    label: "Temporal Causal Graph Violations",
    artifact: "world_summary.json",
    path: "violations_count",
    classification: "VERIFIED",
    format: "int",
    fallbackValue: 0,
    description: "Zero temporal lookahead or future edge leakage violations verified across 28,044 edges.",
    experiment: "S-05",
  },
  automated_tests_count: {
    id: "automated_tests_count",
    label: "Verified Invariant Test Suite",
    artifact: "manifest.json",
    path: "test_suite_passed",
    classification: "VERIFIED",
    format: "int",
    fallbackValue: 225,
    description: "Complete repository invariant and failure-localisation test suite (225 passing, 0 failures).",
    experiment: "GATES",
  },

  // Graph Fusion Section
  v7_tabular_pr_auc: {
    id: "v7_tabular_pr_auc",
    label: "Arm A — 25 Tabular Features Baseline PR-AUC",
    artifact: "blue_metrics.json",
    path: "pr_auc",
    classification: "MEASURED",
    format: "float",
    digits: 4,
    fallbackValue: 0.9607,
    description: "Baseline LightGBM tabular-only fraud detector PR-AUC on scaled synthetic evaluation split.",
    experiment: "S-02",
    seed: 20260827,
  },
  v7_causal_fusion_pr_auc: {
    id: "v7_causal_fusion_pr_auc",
    label: "Arm C — 41-D Dual-Branch Causal Fusion PR-AUC",
    artifact: "evaluation.json",
    path: "anchor.pr_auc",
    classification: "MEASURED",
    format: "float",
    digits: 4,
    fallbackValue: 0.9805,
    description: "Dual-branch fused detector (25 tabular + 16-D dynamic graph embedding) PR-AUC.",
    experiment: "S-02",
    seed: 20260827,
  },
  v7_topology_contribution: {
    id: "v7_topology_contribution",
    label: "Arm C Topology Contribution vs Shuffled Control",
    artifact: "evaluation.json",
    path: "topology_delta",
    classification: "MEASURED",
    format: "percent",
    digits: 2,
    fallbackValue: 0.0085,
    description: "+0.85 pp PR-AUC uplift over shuffled topology control (0.9721), confirming causal graph structure contribution.",
    experiment: "S-02",
    seed: 20260827,
  },

  // Real-World Validation Section
  sparkov_c2st_auc: {
    id: "sparkov_c2st_auc",
    label: "C2ST Classifier Two-Sample Test AUC",
    artifact: "fidelity_report.json",
    path: "l4_c2st_auc_row",
    classification: "REAL-WORLD DATA",
    format: "float",
    digits: 4,
    fallbackValue: 0.7780,
    description: "Discriminator AUC distinguishing synthetic from Sparkov 50k real transactions (95% CI: [0.7641, 0.7918]).",
    experiment: "RES-C2ST",
    dataset: "Sparkov Credit Card Benchmark",
  },
  sparkov_tstr_roc_auc: {
    id: "sparkov_tstr_roc_auc",
    label: "TSTR Synthetic-to-Real ROC-AUC",
    artifact: "fidelity_report.json",
    path: "l5_tstr_pr_auc",
    classification: "REAL-WORLD DATA",
    format: "float",
    digits: 4,
    fallbackValue: 0.7597,
    description: "Train on Synthetic, Test on Real (TSTR) transfer ROC-AUC on independent Sparkov real dataset.",
    experiment: "RES-TSTR",
    dataset: "Sparkov Real vs KIRA Synthetic",
  },
};
