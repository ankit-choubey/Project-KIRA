/**
 * Unified Data Source Adapter for Project KIRA
 * Supports dual-mode architecture:
 *  - Live Mode: Queries FastAPI backend at `/api/*`
 *  - Static Mode: Loads baked static JSON artifacts from `/data/*` or `./data/*`
 */

import type {
  Health,
  AppConfig,
  StreamPage,
  InspectResult,
  EvaluationResult,
  RoundResult,
  ScoreRequest,
  ScoreResponse,
  RedAttackResult,
} from "./types";

export type DataMode = "live" | "static";

export const DATA_MODE: DataMode =
  (import.meta.env.VITE_DATA_MODE as DataMode) || "live";

const API_BASE = (
  (import.meta.env.VITE_API_BASE_URL as string) ||
  (import.meta.env.VITE_API_BASE as string) ||
  ""
).replace(/\/$/, "");

function toUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  if (!API_BASE) return path;
  return `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
}

class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(toUrl(url));
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore non-json error response */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

async function postJson<T>(url: string, payload: unknown): Promise<T> {
  const res = await fetch(toUrl(url), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export const source = {
  mode: DATA_MODE,

  async health(): Promise<Health> {
    if (DATA_MODE === "static") {
      try {
        const manifest = await this.loadArtifact<{ run_id: string; is_fixture: boolean }>("manifest.json");
        return {
          status: "ok",
          run_id: manifest.run_id,
          is_fixture: manifest.is_fixture ?? false,
          artifacts_loaded: true,
          detail: "Static Artifacts Loaded",
        };
      } catch {
        return {
          status: "ok",
          run_id: "run_tiny_s20260827_193f7897_40997ab",
          is_fixture: false,
          artifacts_loaded: true,
          detail: "Static Bundle Mode",
        };
      }
    }
    return getJson<Health>("/api/health");
  },

  async config(): Promise<AppConfig> {
    if (DATA_MODE === "static") {
      return {
        scale: "tiny",
        families: ["velocity_spike", "amount_drift", "geo_hop", "agent_subversion"],
        hidden_from_blue: ["cross_merchant_fanout", "slow_siphon"],
        query_budgets: [1, 5, 20, 100],
        config_hash: "193f789727f6",
      };
    }
    return getJson<AppConfig>("/api/config");
  },

  async runs(): Promise<{ runs: string[] }> {
    if (DATA_MODE === "static") {
      return { runs: ["run_tiny_s20260827_193f7897_40997ab"] };
    }
    return getJson<{ runs: string[] }>("/api/runs");
  },

  async stream(offset = 0, limit = 100): Promise<StreamPage> {
    if (DATA_MODE === "static") {
      const sample = await this.loadArtifact<{ samples?: any[]; rows?: any[] }>("sample_transactions.json");
      const rows = sample.rows || sample.samples || [];
      return {
        run_id: "run_tiny_s20260827_193f7897_40997ab",
        is_fixture: false,
        offset,
        limit,
        total: rows.length,
        rows: rows.slice(offset, offset + limit),
      };
    }
    return getJson<StreamPage>(`/api/stream?offset=${offset}&limit=${limit}`);
  },

  async transaction(id: string): Promise<InspectResult> {
    return getJson<InspectResult>(`/api/transaction/${encodeURIComponent(id)}`);
  },

  async coevolution(): Promise<{ run_id: string; is_fixture: boolean; rounds: RoundResult[] }> {
    if (DATA_MODE === "static") {
      const ev = await this.loadArtifact<EvaluationResult>("evaluation.json");
      return {
        run_id: ev.manifest?.run_id ?? "run_tiny_s20260827_193f7897_40997ab",
        is_fixture: ev.manifest?.is_fixture ?? false,
        rounds: ev.rounds ?? [],
      };
    }
    return getJson<{ run_id: string; is_fixture: boolean; rounds: RoundResult[] }>("/api/coevolution");
  },

  async evidence(): Promise<EvaluationResult> {
    if (DATA_MODE === "static") {
      return this.loadArtifact<EvaluationResult>("evaluation.json");
    }
    return getJson<EvaluationResult>("/api/evidence");
  },

  async artifacts(): Promise<{ run_id: string; is_fixture: boolean; artifacts: string[] }> {
    if (DATA_MODE === "static") {
      return {
        run_id: "run_tiny_s20260827_193f7897_40997ab",
        is_fixture: false,
        artifacts: [
          "manifest.json",
          "evaluation.json",
          "scoreboard.json",
          "promotion_history.json",
          "weakness_profile.json",
          "failures.json",
          "experiment_register.json",
          "three_world_evaluation.json",
          "attack_summary.json",
          "intent_ablation.json",
          "latency_benchmark.json",
          "external_anchor.json",
          "blue_metrics.json",
          "red_metrics.json",
          "world_summary.json",
          "sample_transactions.json",
          "provenance.json",
        ],
      };
    }
    return getJson<{ run_id: string; is_fixture: boolean; artifacts: string[] }>("/api/artifacts");
  },

  async loadArtifact<T = unknown>(name: string): Promise<T> {
    const cleanName = name.replace(/^artifacts\//, "").replace(/\.json$/, "");
    if (DATA_MODE === "static") {
      try {
        return await getJson<T>(`/data/${cleanName}.json`);
      } catch {
        return await getJson<T>(`./data/${cleanName}.json`);
      }
    }
    return getJson<T>(`/api/artifact/${encodeURIComponent(cleanName)}`);
  },

  async score(req: ScoreRequest): Promise<ScoreResponse> {
    return postJson<ScoreResponse>("/api/score", req);
  },

  async attack(payload: Record<string, unknown>): Promise<RedAttackResult> {
    return postJson<RedAttackResult>("/api/attack", payload);
  },
};
