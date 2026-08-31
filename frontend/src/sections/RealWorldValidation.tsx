import React from "react";
import { Section } from "../components/Section";
import { Metric } from "../components/Metric";
import { Tag } from "../components/Tag";
import { DatabaseIcon, ShieldIcon } from "../components/SvgIcons";

export const RealWorldValidation: React.FC = () => {
  return (
    <Section
      id="real-world"
      tagline="08 — External Benchmarking & Invariance"
      title="Real-World Transfer & Causal Leakage Invariance"
      description="We benchmark synthetic model representations against an independent real-world dataset (Sparkov 50k transactions) and verify strict temporal graph causal isolation."
    >
      {/* 2-Column Suite: Sparkov Benchmark + Causal Graph Leakage */}
      <div className="grid-2" style={{ marginBottom: "24px" }}>
        {/* Card 1: Independent Sparkov Real-World Benchmark */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <DatabaseIcon size={16} color="var(--accent)" />
              <span>Independent Public Benchmark (Sparkov)</span>
            </div>
            <Tag classification="REAL-WORLD DATA" clickable={false} />
          </div>

          <p className="card-desc">
            Evaluated on 50,000 real-world payment transactions (199 frauds, 0.398% prevalence, CC0 1.0) to measure distribution fidelity and cross-domain transfer.
          </p>

          <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
            <div className="flex-between">
              <span>Classifier Two-Sample Test (C2ST)</span>
              <span className="mono" style={{ fontWeight: 600 }}>
                <Metric id="sparkov_c2st_auc" /> (95% CI: [0.7641, 0.7918])
              </span>
            </div>
            <div className="flex-between">
              <span>TSTR Real-World Transfer ROC-AUC</span>
              <span className="mono" style={{ fontWeight: 700, color: "var(--accent)" }}>
                <Metric id="sparkov_tstr_roc_auc" />
              </span>
            </div>
            <div className="flex-between">
              <span>In-Domain TRTR Reference ROC-AUC</span>
              <span className="mono">0.9708 (Transfer Gap: -0.2111)</span>
            </div>
          </div>

          <div style={{ marginTop: "14px", padding: "10px 12px", background: "var(--surface-2)", borderRadius: "4px", fontSize: "12px", lineHeight: "1.5" }}>
            <strong>Honest Scientific Finding:</strong> C2ST AUC of 0.7780 confirms synthetic and real transactions remain distinguishable. Synthetic training transfers meaningful ranking signal (ROC-AUC 0.7597) without claiming synthetic perfection.
          </div>
        </div>

        {/* Card 2: Causal Graph Leakage & Temporal Invariance */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldIcon size={16} color="var(--allow)" />
              <span>Causal Graph Temporal Invariance Audit</span>
            </div>
            <span className="badge-pill allow">0 Violations</span>
          </div>

          <p className="card-desc">
            Rigorous chronological graph partitioning (t_train &lt; t_valid &lt; t_test) verifying zero future entity edge or feature leakage.
          </p>

          <div className="stage-stat-box" style={{ background: "var(--allow-soft)" }}>
            <div className="flex-between">
              <span>Temporal Graph Leakage Violations</span>
              <span className="mono" style={{ color: "var(--allow)", fontWeight: 700, fontSize: "16px" }}>
                <Metric id="causal_leakage_violations" /> / 28,044 edges
              </span>
            </div>
            <div className="flex-between">
              <span>Future Edge Invariance (Δ_edges)</span>
              <span className="mono" style={{ color: "var(--allow)", fontWeight: 600 }}>
                Δ = 0.0000 (Strictly Invariant)
              </span>
            </div>
            <div className="flex-between">
              <span>Future Node Feature Invariance (Δ_nodes)</span>
              <span className="mono" style={{ color: "var(--allow)", fontWeight: 600 }}>
                Δ = 0.0000 (Strictly Invariant)
              </span>
            </div>
          </div>

          <div style={{ marginTop: "14px", padding: "10px 12px", background: "var(--surface-2)", borderRadius: "4px", fontSize: "12px", lineHeight: "1.5" }}>
            <strong>Causal Guarantee:</strong> No node embedding or rolling aggregation computed at time $t$ has access to any transaction or relationship timestamped after $t$.
          </div>
        </div>
      </div>

      {/* Operational Resilience Suite (TI-001, OPS-002, DRIFT) */}
      <div className="card" style={{ background: "var(--surface-2)" }}>
        <div className="card-header">
          <div className="card-title">
            <ShieldIcon size={16} color="var(--accent)" />
            <span>Operational Resilience &amp; Threat Intelligence Suite (TI-001, OPS-002, DRIFT)</span>
          </div>
          <span className="badge-pill allow">Active Runtime Governance</span>
        </div>

        <div className="grid-3" style={{ margin: "16px 0" }}>
          {/* TI-001 */}
          <div className="stage-stat-box" style={{ background: "var(--surface-1)" }}>
            <span style={{ fontSize: "11px", color: "var(--accent)", textTransform: "uppercase", fontWeight: 700 }}>
              TI-001: Threat Intelligence Enrichment
            </span>
            <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "4px" }}>
              <div className="flex-between">
                <span>Relative ASR Reduction</span>
                <span className="mono" style={{ color: "var(--allow)", fontWeight: 700, fontSize: "16px" }}>
                  -50.0% (-6.66 pp)
                </span>
              </div>
              <div className="flex-between">
                <span>Baseline vs Enriched ASR</span>
                <span className="mono">13.33% ➔ 6.67%</span>
              </div>
              <div className="flex-between">
                <span>Evaluation Slice</span>
                <span className="mono">2,805 samples (42 frauds)</span>
              </div>
            </div>
          </div>

          {/* OPS-002 */}
          <div className="stage-stat-box" style={{ background: "var(--surface-1)" }}>
            <span style={{ fontSize: "11px", color: "var(--step-up)", textTransform: "uppercase", fontWeight: 700 }}>
              OPS-002: Telemetry Degradation
            </span>
            <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "4px" }}>
              <div className="flex-between">
                <span>Full Telemetry PR-AUC</span>
                <span className="mono" style={{ fontWeight: 600 }}>1.0000</span>
              </div>
              <div className="flex-between">
                <span>Missing Device PR-AUC</span>
                <span className="mono" style={{ color: "var(--step-up)", fontWeight: 700 }}>0.8490 (Drop)</span>
              </div>
              <div className="flex-between">
                <span>Governed Policy Fallback</span>
                <span className="mono" style={{ color: "var(--allow)", fontWeight: 700 }}>STEP-UP (Active)</span>
              </div>
            </div>
          </div>

          {/* DRIFT */}
          <div className="stage-stat-box" style={{ background: "var(--surface-1)" }}>
            <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 700 }}>
              DRIFT: Distribution Shift Monitor
            </span>
            <div style={{ marginTop: "8px", display: "flex", flexDirection: "column", gap: "4px" }}>
              <div className="flex-between">
                <span>Amount KS-Statistic</span>
                <span className="mono" style={{ fontWeight: 600 }}>0.1119 (p &lt; 0.05)</span>
              </div>
              <div className="flex-between">
                <span>Evaluated Observations</span>
                <span className="mono">4,674 transactions</span>
              </div>
              <div className="flex-between">
                <span>Automated Workflow</span>
                <span className="mono" style={{ color: "var(--accent)", fontWeight: 600 }}>Challenger Triggered</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ padding: "10px 12px", background: "var(--surface-1)", borderRadius: "4px", fontSize: "12px", lineHeight: "1.5" }}>
          <strong>Resilience Guarantee:</strong> When telemetry signals fail (missing device/IP headers), KIRA does not guess or drop protection; it automatically escalates to governed multi-factor authentication (Step-Up). When statistical distribution drift is detected ($p &lt; 0.05$), the system triggers an asynchronous Challenger evaluation cycle.
        </div>
      </div>
    </Section>
  );
};
