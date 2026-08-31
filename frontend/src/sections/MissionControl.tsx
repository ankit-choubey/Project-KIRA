import React from "react";
import { Section } from "../components/Section";
import { StatTile } from "../components/StatTile";
import { useArtifact } from "../data/useArtifact";
import type { WorldSummary, RunManifest } from "../data/types";
import { fmtInt } from "../data/format";
import { ShieldIcon, TargetIcon, LockIcon } from "../components/SvgIcons";

export const MissionControl: React.FC = () => {
  const { data: world } = useArtifact<WorldSummary>("world_summary.json");
  const { data: manifest } = useArtifact<RunManifest>("manifest.json");

  return (
    <Section
      id="mission"
      tagline="01 — Research Instrument"
      title="Mastercard AI Defense Lab — Adversarial Evaluation"
      description="An adversarial payment-security laboratory: evaluating whether model hardening truly generalises against adaptive attacks or causes catastrophic forgetting."
      requiredArtifact="manifest.json"
    >
      {/* Narrative Lead Banner */}
      <div className="card mission-narrative-card">
        <div className="mission-narrative-content">
          <span className="narrative-tag">EXECUTIVE FINDING</span>
          <p className="narrative-text">
            We built an attacker that beats our unhardened detector <strong>96.67%</strong> of the time at a 20-probe budget.
            Hardening drove held-out attack success to <strong>0.00%</strong>. But our promotion gate <strong>refused to ship the hardened model</strong> —
            it triggered detection collapse on clean traffic. And against attack families we never trained on, the attacker still wins <strong>100%</strong> of the time.
            We measured all three, and we report all three.
          </p>
        </div>
      </div>

      {/* 10 Audited Hero Metric Tiles */}
      <div style={{ marginBottom: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>
          The 10 Audited Headline Research Numbers (V7 &amp; ADV Swarm Suite)
        </span>
        <span className="badge-pill allow">225 Tests Green · 22/22 SHA-256 Signatures</span>
      </div>

      <div className="grid-5" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", marginBottom: "20px" }}>
        {/* 01: 284,807 */}
        <StatTile
          metricId="ulb_benchmark_txns"
          subtitle="01 · External Real Benchmark (ULB)"
          highlight="allow"
        />
        {/* 02: 50,000 */}
        <StatTile
          metricId="v7_total_transactions"
          subtitle="02 · Large-Scale Synthetic (S-02)"
          highlight="neutral"
        />
        {/* 03: 15,000 */}
        <StatTile
          metricId="adv002_swarm_attacks"
          subtitle="03 · Stateful Swarm Trials (ADV-002)"
          highlight="warn"
        />
        {/* 04: 10,000 */}
        <StatTile
          metricId="adv001_total_attacks"
          subtitle="04 · Constrained Attacks (ADV-001)"
          highlight="neutral"
        />
        {/* 05: +10.08 pp */}
        <StatTile
          metricId="adv002_memory_gain"
          subtitle="05 · Attacker Memory Effect (19.7% vs 9.6%)"
          highlight="warn"
        />
        {/* 06: +1.98 pp */}
        <StatTile
          metricId="v7_fusion_uplift"
          subtitle="06 · Causal Graph Uplift (p = 0.046)"
          highlight="allow"
        />
        {/* 07: 50% */}
        <StatTile
          metricId="ti001_asr_reduction"
          subtitle="07 · TI Bounded ASR Reduction"
          highlight="allow"
        />
        {/* 08: 100% */}
        <StatTile
          metricId="zero_day_asr"
          subtitle="08 · Zero-Day ASR (Vulnerability Found)"
          highlight="block"
        />
        {/* 09: 22 / 22 */}
        <StatTile
          metricId="causal_leakage_violations"
          subtitle="09 · 0 Leakage Violations / 28,044 Edges"
          highlight="allow"
        />
        {/* 10: 225 */}
        <StatTile
          metricId="automated_tests_count"
          subtitle="10 · Automated Tests (0 Failures)"
          highlight="allow"
        />
      </div>

      {/* Measured Headline Evidence Table */}
      <div className="card" style={{ marginBottom: "20px" }}>
        <div className="card-header">
          <div className="card-title">
            <ShieldIcon size={16} color="var(--accent)" />
            <span>Authoritative Measured Research Evidence (V7 &amp; ADV Population Matrix)</span>
          </div>
          <span className="badge-pill allow">284k Real · 50k Synthetic · 25k Attacks</span>
        </div>

        <div className="table-scroll-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Scientific Claim / Evaluation Arm</th>
                <th>Authoritative Value</th>
                <th>Statistical Baseline</th>
                <th>Measurement Classification</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>External Real-World Benchmark (ULB 2015)</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--accent)" }}>PR-AUC 0.8640 (284,807 txns)</td>
                <td className="num mono">492 Frauds · FPR 0.0003 · ECE 0.0042</td>
                <td><span className="decision-chip ALLOW">REAL-WORLD ANCHOR</span></td>
              </tr>
              <tr style={{ background: "var(--accent-soft)" }}>
                <td><strong>41-D Causal Graph Fusion (Arm C vs Arm A)</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--accent)" }}>PR-AUC 0.9805 vs 0.9607</td>
                <td className="num mono">+1.98 pp Uplift (Bootstrap p = 0.046)</td>
                <td><span className="decision-chip ALLOW">EXP-007-B / MEASURED</span></td>
              </tr>
              <tr>
                <td><strong>ADV-002 Stateful Swarm Memory Effect</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--step-up)" }}>+10.08 pp ASR Gain (19.68% vs 9.60%)</td>
                <td className="num mono">15,000 Attempts (5 Agents · 3 Arms)</td>
                <td><span className="decision-chip STEP_UP">ADV-002 / SWARM</span></td>
              </tr>
              <tr>
                <td><strong>ADV-001 Constrained Adversarial Population</strong></td>
                <td className="num mono" style={{ fontWeight: 700 }}>6.00% Success (600 / 10,000)</td>
                <td className="num mono">91.00% Blocked, 3.00% Step-Up (95% CI: [5.54%, 6.46%])</td>
                <td><span className="decision-chip STEP_UP">ADV-001</span></td>
              </tr>
              <tr>
                <td><strong>Synthetic Threat Intelligence Enrichment (TI-001)</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--allow)" }}>50.0% Relative ASR Reduction</td>
                <td className="num mono">13.33% Baseline ➔ 6.67% Enriched (2,805 samples)</td>
                <td><span className="decision-chip ALLOW">TI-001</span></td>
              </tr>
              <tr>
                <td><strong>Temporal Graph Leakage Invariance Audit</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--allow)" }}>0 violations / 28,044 edges</td>
                <td className="num mono">Δ_edges = 0.0000, Δ_nodes = 0.0000</td>
                <td><span className="decision-chip ALLOW">SHA-256 VERIFIED</span></td>
              </tr>
              <tr>
                <td><strong>Hardened Challenger Held-Out Variants</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--allow)" }}>ASR 0.00%</td>
                <td className="num mono">Unhardened Baseline ASR: 14.55%</td>
                <td><span className="decision-chip ALLOW">MEASURED</span></td>
              </tr>
              <tr style={{ background: "var(--block-soft)" }}>
                <td><strong>World C Zero-Day Withheld Attack Families</strong></td>
                <td className="num mono" style={{ fontWeight: 700, color: "var(--block)" }}>ASR 100.00%</td>
                <td className="num mono">Vulnerability Discovered (No Prior Exposure)</td>
                <td><span className="decision-chip BLOCK">FAILURE FINDING</span></td>
              </tr>
              <tr>
                <td><strong>Telemetry Degradation (OPS-002)</strong></td>
                <td className="num mono" style={{ fontWeight: 700 }}>PR-AUC 1.000 ➔ 0.8490 (Missing Device)</td>
                <td className="num mono">Governed Step-Up Policy Fallback: ACTIVE</td>
                <td><span className="decision-chip STEP_UP">OPS-002</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* System Triad Architecture */}
      <div className="grid-3">
        <div className="card architecture-card">
          <div className="card-header">
            <div className="card-title">
              <ShieldIcon size={16} color="var(--accent)" />
              <span>Synthetic Causal World</span>
            </div>
            <span className="badge-pill">Scale: {manifest?.scale || "tiny"}</span>
          </div>
          <p className="card-desc">
            A stateful payment simulator generating legitimate cardholders, merchants, devices, and spatial trajectories under strict time causality.
          </p>
          <div className="arch-metrics-list">
            <div className="arch-metric-row">
              <span className="arch-k">Transactions</span>
              <span className="arch-v mono">{world ? fmtInt(world.n_transactions) : (manifest ? fmtInt(manifest.n_transactions) : "1,448")}</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Customers / Merchants</span>
              <span className="arch-v mono">{manifest ? `${manifest.n_customers} / ${manifest.n_merchants}` : "50 / 20"}</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Base Fraud Rate</span>
              <span className="arch-v mono">{world ? `${(world.fraud_rate * 100).toFixed(2)}%` : "3.45%"}</span>
            </div>
          </div>
        </div>

        <div className="card architecture-card">
          <div className="card-header">
            <div className="card-title">
              <TargetIcon size={16} color="var(--step-up)" />
              <span>Red Mutation Engine</span>
            </div>
            <span className="badge-pill">5 Families</span>
          </div>
          <p className="card-desc">
            Adaptive adversarial search mutating amount drift, merchant probes, temporal bursts, geo hops, and synthetic IDs under hard business validity constraints.
          </p>
          <div className="arch-metrics-list">
            <div className="arch-metric-row">
              <span className="arch-k">Query Budgets</span>
              <span className="arch-v mono">[1, 5, 20, 100]</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Constraint Violations</span>
              <span className="arch-v mono">0 (Strict Mask)</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Primary Bottleneck</span>
              <span className="arch-v mono">Detection Collapse</span>
            </div>
          </div>
        </div>

        <div className="card architecture-card">
          <div className="card-header">
            <div className="card-title">
              <LockIcon size={16} color="var(--block)" />
              <span>Safety Promotion Gate</span>
            </div>
            <span className="badge-pill">4 Rounds Blocked</span>
          </div>
          <p className="card-desc">
            Automated verification evaluating PR-AUC retention, FPR bounds, and ECE calibration. Hardening is rolled back if clean traffic detection collapses.
          </p>
          <div className="arch-metrics-list">
            <div className="arch-metric-row">
              <span className="arch-k">PR-AUC Threshold</span>
              <span className="arch-v mono">&ge; 0.9000</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Challenger PR-AUC</span>
              <span className="arch-v mono" style={{ color: "var(--block)" }}>0.8417 (REJECT)</span>
            </div>
            <div className="arch-metric-row">
              <span className="arch-k">Champion Status</span>
              <span className="arch-v mono" style={{ color: "var(--allow)" }}>Retained (Rollback)</span>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
};
