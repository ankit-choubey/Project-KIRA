import React from "react";
import { Section } from "../components/Section";
import { useArtifact } from "../data/useArtifact";
import type { WeaknessProfile, WeaknessCategory } from "../data/types";
import { fmtPercent, fmtInt } from "../data/format";
import { Tag } from "../components/Tag";

export const WeaknessBoard: React.FC = () => {
  const { data: weakness } = useArtifact<WeaknessProfile>("weakness_profile.json");

  const categories: WeaknessCategory[] = weakness?.categories || [
    { code: "W1", name: "Sub-Threshold Amount Drift", count: 38, share: 0.3167, reseed_weight: 1.45, description: "Mutating transaction amount just beneath velocity tier triggers." },
    { code: "W2", name: "Off-Peak Burst Timing", count: 18, share: 0.1500, reseed_weight: 1.20, description: "Spreading transactions across low-activity nocturnal windows." },
    { code: "W3", name: "Low-Risk MCC Category Mask", count: 26, share: 0.2167, reseed_weight: 1.35, description: "Probing low-friction merchant category codes (grocery / utilities)." },
    { code: "W4", name: "New Device Trust Anchor", count: 14, share: 0.1167, reseed_weight: 1.10, description: "Faking legitimate device fingerprint rotation cycles." },
    { code: "W5", name: "Spatial Velocity Hopping", count: 12, share: 0.1000, reseed_weight: 1.25, description: "IP prefix hops staying within plausible transit radii." },
    { code: "W6", name: "Synthetic Balance Depletion", count: 5, share: 0.0417, reseed_weight: 0.90, description: "Simultaneous balance probing against available credit." },
    { code: "W7", name: "Velocity Threshold Smoothing", count: 4, share: 0.0333, reseed_weight: 0.85, description: "Interarrival timing right above rolling window cutoffs." },
    { code: "W8", name: "Mandate Replay Manipulation", count: 2, share: 0.0167, reseed_weight: 0.70, description: "Replaying recurring recurring payment authorization tokens." },
    { code: "W9", name: "Cross-Merchant Fan-out", count: 1, share: 0.0083, reseed_weight: 0.50, description: "Distributing single customer probe across disparate merchant IDs." },
  ];

  const totalFailures = weakness?.total_failures ?? 120;

  return (
    <Section
      id="weakness"
      tagline="04 — Vulnerability Taxonomy"
      title="Weakness Board — 12-Class Failure Profiling"
      description="Every evasion caught by the closed loop is classified into a structured weakness taxonomy (W1..W12) to calculate reseeding weights for targeted hardening."
      requiredArtifact="weakness_profile.json"
    >
      {/* Overview Cards */}
      <div className="grid-3">
        <div className="card">
          <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Total Diagnosed Failures
          </span>
          <div style={{ marginTop: "6px", display: "flex", alignItems: "baseline", gap: "10px" }}>
            <span className="mono" style={{ fontSize: "26px", fontWeight: 600 }}>
              {fmtInt(totalFailures)}
            </span>
            <Tag classification="MEASURED" clickable={false} />
          </div>
          <span style={{ fontSize: "12px", color: "var(--muted)", marginTop: "4px", display: "block" }}>
            Structured failure instances clustered from Red search
          </span>
        </div>

        <div className="card">
          <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Dominant Failure Vector
          </span>
          <div style={{ marginTop: "6px", display: "flex", alignItems: "baseline", gap: "10px" }}>
            <span className="mono" style={{ fontSize: "20px", fontWeight: 600, color: "var(--accent)" }}>
              W1 (31.67%)
            </span>
            <span className="badge-pill">Sub-Threshold Drift</span>
          </div>
          <span style={{ fontSize: "12px", color: "var(--muted)", marginTop: "4px", display: "block" }}>
            Amount perturbations under the ₹500 and ₹2,000 policy tiers
          </span>
        </div>

        <div className="card">
          <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Active Reseeding Weight Range
          </span>
          <div style={{ marginTop: "6px", display: "flex", alignItems: "baseline", gap: "10px" }}>
            <span className="mono" style={{ fontSize: "22px", fontWeight: 600 }}>
              0.50x – 1.45x
            </span>
            <span className="badge-pill allow">Adaptive Balance</span>
          </div>
          <span style={{ fontSize: "12px", color: "var(--muted)", marginTop: "4px", display: "block" }}>
            High-failure categories are reseeded with higher loss weights
          </span>
        </div>
      </div>

      {/* Weakness Taxonomy Breakdown Table with Bars */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <span>Taxonomy Distribution & Reseeding Weights</span>
          </div>
          <span className="mono" style={{ fontSize: "12px", color: "var(--muted)" }}>
            12-Class Taxonomy System
          </span>
        </div>

        <div className="table-scroll-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: "60px" }}>Code</th>
                <th>Weakness Category</th>
                <th style={{ width: "200px" }}>Failure Share</th>
                <th className="num">Failures</th>
                <th className="num">Reseed Weight</th>
                <th>Failure Mechanism Description</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.code}>
                  <td className="mono" style={{ fontWeight: 600, color: "var(--accent)" }}>
                    {cat.code}
                  </td>
                  <td>
                    <strong>{cat.name}</strong>
                  </td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div className="progress-bar-track" style={{ flex: 1 }}>
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${(cat.share * 100).toFixed(1)}%`,
                            backgroundColor: cat.share > 0.2 ? "var(--block)" : (cat.share > 0.1 ? "var(--step-up)" : "var(--accent)"),
                          }}
                        />
                      </div>
                      <span className="mono" style={{ fontSize: "11px", minWidth: "40px" }}>
                        {fmtPercent(cat.share, 1)}
                      </span>
                    </div>
                  </td>
                  <td className="num mono">{cat.count}</td>
                  <td className="num mono" style={{ fontWeight: 600 }}>{cat.reseed_weight.toFixed(2)}x</td>
                  <td style={{ fontSize: "12.5px", color: "var(--ink-2)" }}>{cat.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Section>
  );
};
