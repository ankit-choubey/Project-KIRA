/**
 * The single typed client. Mirrors `src/mcdl/schemas.py`.
 *
 * When a schema changes, change both in the same commit. The UI should break
 * loudly rather than render the wrong number silently.
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
  detail: string;
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

/** Every numeric field is nullable. `null` means NOT MEASURED and must render as
 *  such — never as a zero. */
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
  result_status: "VERIFIED" | "TARGET" | "RESULT" | "TARGET_NOT_MET";
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

// --------------------------------------------------------------------------- //

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* body was not json; keep statusText */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => get<Health>("/api/health"),
  config: () => get<AppConfig>("/api/config"),
  runs: () => get<{ runs: string[] }>("/api/runs"),
  stream: (offset = 0, limit = 100) =>
    get<StreamPage>(`/api/stream?offset=${offset}&limit=${limit}`),
  transaction: (id: string) => get<InspectResult>(`/api/transaction/${encodeURIComponent(id)}`),
  coevolution: () =>
    get<{ run_id: string; is_fixture: boolean; rounds: RoundResult[] }>("/api/coevolution"),
  evidence: () => get<EvaluationResult>("/api/evidence"),
};

/** Render a possibly-unmeasured number. Never returns "0" for null. */
export function fmt(v: number | null | undefined, digits = 3, suffix = ""): string {
  if (v === null || v === undefined) return "not measured";
  return `${v.toFixed(digits)}${suffix}`;
}
