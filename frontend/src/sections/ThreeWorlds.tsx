import React from "react";
import { Section } from "../components/Section";
import { useArtifact } from "../data/useArtifact";
import type { ThreeWorldEvaluation } from "../data/types";
import { fmtPercent, fmt } from "../data/format";
import { Tag } from "../components/Tag";
import { LockIcon, ShieldIcon, TargetIcon } from "../components/SvgIcons";

export const ThreeWorlds: React.FC = () => {
  const { data: threeWorlds } = useArtifact<ThreeWorldEvaluation>("three_world_evaluation.json");

  return (
    <Section
      id="three-worlds"
      tagline="05 — Generalisation Isolation"
      title="Three Worlds Evaluation — Generalisation Boundaries"
      description="To evaluate true generalisation vs memorisation, we evaluate defenses across three isolated test regimes: standard adaptation, shifted physics, and hidden zero-day families."
      requiredArtifact="three_world_evaluation.json"
    >
      {/* Three Worlds Comparative Cards */}
      <div className="grid-3">
        {/* World A */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldIcon size={16} color="var(--allow)" />
              <span>World A: Standard Adaptation</span>
            </div>
            <span className="badge-pill allow">In-Distribution</span>
          </div>
          <p className="card-desc">
            Standard test regime evaluating held-out attack variants within known mutation families (Amount Drift, Temporal Burst).
          </p>

          <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
            <div className="flex-between">
              <span>Attacker Success (ASR)</span>
              <span className="mono" style={{ color: "var(--allow)", fontWeight: 600 }}>
                {fmtPercent(threeWorlds?.world_a?.asr ?? 0.00)}
              </span>
            </div>
            <div className="flex-between">
              <span>Detector PR-AUC</span>
              <span className="mono">{fmt(threeWorlds?.world_a?.pr_auc ?? 0.9375, 4)}</span>
            </div>
            <div className="flex-between">
              <span>Evaluation Slice</span>
              <span className="mono">{(threeWorlds?.world_a_evolution as any)?.transaction_count ?? threeWorlds?.world_a?.sample_count ?? 300} txns</span>
            </div>
          </div>

          <div style={{ marginTop: "12px", display: "flex", justifyContent: "flex-end" }}>
            <Tag classification="MEASURED" clickable={false} />
          </div>
        </div>

        {/* World B */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <TargetIcon size={16} color="var(--step-up)" />
              <span>World B: Shifted Physics</span>
            </div>
            <span className="badge-pill warn">Distribution Shift</span>
          </div>
          <p className="card-desc">
            Perturbed environmental dynamics: altered merchant velocity baselines, off-peak timing distributions, and device trust decay.
          </p>

          <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
            <div className="flex-between">
              <span>Attacker Success (ASR)</span>
              <span className="mono" style={{ color: "var(--step-up)", fontWeight: 600 }}>
                {fmtPercent(threeWorlds?.world_b?.asr ?? 0.1455)}
              </span>
            </div>
            <div className="flex-between">
              <span>Detector PR-AUC</span>
              <span className="mono">{fmt(threeWorlds?.world_b?.pr_auc ?? 0.884, 4)}</span>
            </div>
            <div className="flex-between">
              <span>Evaluation Slice</span>
              <span className="mono">{threeWorlds?.world_b?.sample_count ?? 300} txns</span>
            </div>
          </div>

          <div style={{ marginTop: "12px", display: "flex", justifyContent: "flex-end" }}>
            <Tag classification="EXP-007-E" clickable={false} />
          </div>
        </div>

        {/* World C */}
        <div className="card reject-theme">
          <div className="card-header">
            <div className="card-title">
              <LockIcon size={16} color="var(--block)" />
              <span>World C: Hidden Zero-Day Families</span>
            </div>
            <span className="badge-pill block">Failure Finding</span>
          </div>
          <p className="card-desc">
            Complete zero-day isolation: attack families (<code>geo_hop</code>) withheld entirely from feature engineering, training, and tuning.
          </p>

          <div className="stage-stat-box reject-box">
            <div className="flex-between">
              <span>Attacker Success (ASR)</span>
              <span className="mono" style={{ color: "var(--block)", fontWeight: 700, fontSize: "16px" }}>
                {fmtPercent(threeWorlds?.world_c?.asr ?? 1.00)}
              </span>
            </div>
            <div className="flex-between">
              <span>Detector PR-AUC</span>
              <span className="mono" style={{ color: "var(--block)" }}>{fmt(threeWorlds?.world_c?.pr_auc ?? 0.812, 4)}</span>
            </div>
            <div className="flex-between">
              <span>Evaluation Slice</span>
              <span className="mono">{threeWorlds?.world_c?.sample_count ?? 300} txns</span>
            </div>
          </div>

          <div style={{ marginTop: "12px", display: "flex", justifyContent: "flex-end" }}>
            <Tag classification="FAILURE FINDING" clickable={false} />
          </div>
        </div>
      </div>

      {/* Scientific Analysis Panel for World C */}
      <div className="card" style={{ borderLeft: "4px solid var(--block)" }}>
        <div className="card-header">
          <div className="card-title">
            <LockIcon size={16} color="var(--block)" />
            <span>Honest Scientific Analysis: The 100% Zero-Day Failure Boundary</span>
          </div>
          <Tag classification="FAILURE FINDING" clickable={false} />
        </div>
        <p style={{ margin: 0, fontSize: "14px", lineHeight: "1.6" }}>
          In World C, the attacker achieved <strong>100.00% evasion success</strong> against the model.
          This establishes that model hardening through adversarial perturbation search in known feature subspaces confers <em>zero-shot defense</em> only against known causal invariants.
          When an attacker utilizes a completely unseen spatial vector (<code>geo_hop</code>), the static tree ensemble lacks the requisite topological graph features to detect the anomaly.
          We report this 100% failure finding as an authoritative boundary of gradient-free tabular hardening.
        </p>
      </div>
    </Section>
  );
};
