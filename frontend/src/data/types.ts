/**
 * Shared Type Definitions for Project KIRA Frontend
 * Synchronized with `src/mcdl/schemas.py` & authoritative artifact models.
 */

export type Decision = "ALLOW" | "STEP_UP" | "BLOCK";

export interface Transaction {
  txn_id: string;
  customer_id: string;
  merchant_id: string;
  device_id: string;
  timestamp: string;
  amount: number;
  mcc: string;
  channel: string;
  lat: number;
  lon: number;
  ip_prefix: string;
  is_new_device: boolean;
  auth_failed_count: number;
  agent_id: string | null;
  mandate_id: string | null;
  balance_before: number;
  available_credit: number;
  // Hidden evaluation metadata. Present in artifacts for display, never a feature.
  is_fraud: boolean;
  attack_family: string | null;
  attack_instance_id: string | null;
  attack_variant: number | null;
  hard_negative: string;
}

export interface BlueDecision {
  txn_id: string;
  risk_score: number;
  calibrated_score: number;
  decision: Decision;
  reason_codes: string[];
  intent_drift_score: number | null;
  model_version: string;
  feature_version: string;
  policy_version: string;
  latency_ms: number;
}

export interface Counterfactual {
  txn_id: string;
  found: boolean;
  changed_field: string | null;
  original_value: number | null;
  evading_value: number | null;
  distance: number | null;
  human_readable: string | null;
}

export interface Health {
  status: string;
  run_id: string | null;
  is_fixture: boolean;
  artifacts_loaded: boolean;
  detail?: string;
}

export interface StreamRow {
  transaction: Transaction;
  decision: BlueDecision | null;
}

export interface StreamPage {
  run_id: string;
  is_fixture: boolean;
  offset: number;
  limit: number;
  total: number;
  rows: StreamRow[];
}

export interface InspectResult {
  run_id: string;
  is_fixture: boolean;
  transaction: Transaction;
  decision: BlueDecision | null;
  counterfactual: Counterfactual | null;
  shap: Record<string, number> | null;
  intent_breakdown: Record<string, number> | null;
  neighbours: string[] | null;
}

export interface BlueMetrics {
  pr_auc: number | null;
  roc_auc: number | null;
  precision: number | null;
  recall: number | null;
  fpr: number | null;
  ece: number | null;
  brier: number | null;
  decision_counts: Record<string, number>;
  latency_p50_ms: number | null;
  latency_p95_ms: number | null;
  latency_p99_ms: number | null;
}

export interface RedMetrics {
  asr_by_budget: Record<string, number>;
  asr_seen_variants: number | null;
  asr_heldout_variants: number | null;
  asr_unseen_family: number | null;
  mean_evasion_distance: number | null;
  mask_violations: number;
  invalid_attacks: number;
}

export interface PromotionDecision {
  promoted: boolean;
  champion_version: string;
  challenger_version: string;
  reasons: string[];
  metrics_evaluated: Record<string, number>;
  thresholds: Record<string, number>;
}

export interface AdaptationCost {
  attack_generation_time_s: number;
  training_time_s: number;
  evaluation_time_s: number;
  total_compute_s: number;
  retraining_steps: number;
  memory_mb: number;
}

export interface RoundResult {
  round_index: number;
  champion_version: string;
  challenger_version: string | null;
  promoted: boolean;
  promotion_reasons: string[];
  blue: BlueMetrics;
  red: RedMetrics;
  promotion_decision?: PromotionDecision | null;
  adaptation_cost?: AdaptationCost | null;
}

export interface ScoreboardEntry {
  round_index: number;
  red_asr_seen: number;
  heldout_asr: number;
  hidden_family_asr: number | null;
  med: number | null;
  fidelity_score: number;
  novelty_score: number;
  coverage_score: number;
  blue_pr_auc: number | null;
  blue_fpr: number | null;
  blue_ece: number | null;
  robustness_retention: number;
  plasticity: number;
  latency_p95_ms: number | null;
  adaptation_cost_s: number;
  champion_version: string;
}

export interface ExperimentRecord {
  exp_id: string;
  hypothesis: string;
  dataset_world_version: string;
  code_commit: string;
  configuration_hash: string;
  seed: number;
  baseline_name: string;
  treatment_name: string;
  metrics: Record<string, number>;
  result_status: "VERIFIED" | "TARGET" | "RESULT" | "TARGET_NOT_MET" | "FAILURE_FINDING" | "INCONCLUSIVE" | "MEASURED" | "MEASURED_WITH_CAVEAT";
  conclusion: string;
  artifact_path: string;
}

export interface FidelityReport {
  l1_violations: number;
  l1_checks: Record<string, number>;
  l2_ks_by_column: Record<string, number>;
  l2_correlation_distance: number | null;
  l3_p1_interarrival_ratio: number | null;
  l3_p2_burstiness_ratio: number | null;
  l3_p3_graph_motif_ratio: number | null;
  l3_p4_velocity_trigger_ratio: number | null;
  l3_published_baselines: Record<string, number>;
  l4_c2st_auc_row: number | null;
  l4_c2st_auc_entity: number | null;
  l4_top_giveaway_features: string[];
  l5_tstr_pr_auc: number | null;
  l5_trtr_pr_auc: number | null;
}

export interface RunManifest {
  run_id: string;
  created_at: string;
  git_commit: string;
  config_hash: string;
  seed: number;
  scale: string;
  is_fixture: boolean;
  stages_completed: string[];
  timings_sec: Record<string, number>;
  n_customers: number;
  n_merchants: number;
  n_transactions: number;
  notes: string;
}

export interface WorldSummary {
  n_transactions: number;
  n_customers: number;
  n_merchants: number;
  n_devices?: number;
  fraud_rate: number;
  n_fraud: number;
  n_legit: number;
  physics_valid: boolean;
  violations_count: number;
}

export interface ProvenanceReport {
  run_id: string;
  timestamp: string;
  commit: string;
  config_hash: string;
  files: Record<string, string>;
  signatures_valid: boolean;
  total_artifacts: number;
  verified_artifacts: number;
}

export interface WeaknessCategory {
  code: string;
  name: string;
  count: number;
  share: number;
  reseed_weight: number;
  description: string;
}

export interface WeaknessProfile {
  total_failures: number;
  distribution: Record<string, number>;
  reseeding_weights: Record<string, number>;
  categories?: WeaknessCategory[];
  rare_patterns: string[];
}

export interface AttackMutation {
  field: string;
  original_value: string | number;
  mutated_value: string | number;
  delta: string;
}

export interface AttackSample {
  attack_id: string;
  family: string;
  target_txn_id: string;
  original_score: number;
  evaded_score: number;
  original_decision: Decision;
  evaded_decision: Decision;
  budget_probes_used: number;
  med_distance: number;
  mutations: AttackMutation[];
}

export interface AttackSummary {
  total_attacks: number;
  evasion_count: number;
  aggregate_asr: number;
  dominant_family: string;
  mean_med: number;
  samples: AttackSample[];
}

export interface ThreeWorldSubWorld {
  name?: string;
  asr?: number;
  asr_budget_20?: number;
  pr_auc?: number;
  sample_count?: number;
  med?: number;
  violations?: number;
  status?: string;
  [key: string]: any;
}

export interface ThreeWorldEvaluation {
  world_a?: ThreeWorldSubWorld;
  world_b?: ThreeWorldSubWorld;
  world_c?: ThreeWorldSubWorld;
  world_a_standard?: ThreeWorldSubWorld;
  world_b_shifted?: ThreeWorldSubWorld;
  world_c_zeroday?: ThreeWorldSubWorld;
  world_a_evolution?: any;
  isolation_verified?: boolean;
  [key: string]: any;
}

export interface EvaluationResult {
  manifest: RunManifest;
  fidelity: FidelityReport;
  rounds: RoundResult[];
  anchor: BlueMetrics | null;
  ablations: Record<string, BlueMetrics>;
}

export interface AppConfig {
  scale: string;
  families: string[];
  hidden_from_blue: string[];
  query_budgets: number[];
  config_hash: string;
}

export interface ScoreRequest {
  transaction: Transaction;
}

export interface ScoreResponse {
  decision: BlueDecision;
  served_by: string;
  api_latency_ms: number;
}

export interface RedAttackResult {
  attack_id?: string;
  status?: string;
  [key: string]: any;
}
