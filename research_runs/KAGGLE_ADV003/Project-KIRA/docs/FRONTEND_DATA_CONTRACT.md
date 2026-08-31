# Frontend Data Contract & Typed Adapter Architecture

**Status**: Active Architecture Standard  
**Data Modes Supported**: `DATA_MODE="static"` (local JSONs) and `DATA_MODE="live"` (Render/FastAPI API)

---

## 1. Unified Layer Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    UI Presentation Layer                │
│    (Dashboard, Scoreboard, Provenance Drawer, Console)  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 Typed Data Adapter Layer                │
│     (Transforms internal representations into ViewModels)│
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
  [DATA_MODE="static"]            [DATA_MODE="live"]
               │                           │
               ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│    Static JSON Loader     │ │      Live API Client      │
│  (Reads shipped /data/*.json)│ │  (Calls /api/* endpoints) │
└───────────────────────────┘ └───────────────────────────┘
```

---

## 2. Shared TypeScript Interfaces

```typescript
export type ClaimClassification =
  | "MEASURED"
  | "MEASURED_WITH_CAVEAT"
  | "INCONCLUSIVE"
  | "LOW_SAMPLE"
  | "NOT_MEASURED"
  | "FAILURE_FINDING"
  | "NOT_RUN";

export interface ProvenanceRecord {
  claim_id: string;
  experiment_id: string;
  dataset_id: string;
  run_id: string;
  scale: "tiny" | "small" | "medium" | "full";
  world_seed: number;
  model_seed?: number | null;
  sample_count?: number | null;
  positive_count?: number | null;
  metric: string;
  value: number | null;
  confidence_interval_95?: [number, number] | null;
  p_value?: number | null;
  artifact_path: string;
  json_path: string;
  git_sha: string;
  classification: ClaimClassification;
}

export interface MetricDisplayViewModel {
  label: string;
  formattedValue: string; // e.g. "14.55%", "2.8488", or "Not measured" (italic)
  isMeasured: boolean;
  provenance: ProvenanceRecord;
}
```

---

## 3. Rendering Invariants
1. **Never coerce `null` to `0` or `0.0%`**: A missing or unmeasured value must render as `Not measured` in muted italic style.
2. **Never hide caveats**: If `classification === "MEASURED_WITH_CAVEAT"`, the UI must display a caveat badge linking to the provenance drawer.
3. **No Direct JSON parsing in Components**: Components only bind to `MetricDisplayViewModel` provided by the typed adapter.
