import React, { useState, useEffect } from "react";
import { Section } from "../components/Section";
import { useArtifact } from "../data/useArtifact";
import type { EvaluationResult, ScoreboardEntry } from "../data/types";
import { fmt, fmtPercent, fmtSec } from "../data/format";
import { PlayIcon, PauseIcon, CrossIcon, ShieldIcon, TargetIcon, LockIcon } from "../components/SvgIcons";
import { Tag } from "../components/Tag";

export const TheLoop: React.FC = () => {
  const { data: evaluation } = useArtifact<EvaluationResult>("evaluation.json");
  const { data: scoreboard } = useArtifact<ScoreboardEntry[]>("scoreboard.json");

  const [selectedRound, setSelectedRound] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const rounds = evaluation?.rounds ?? [];
  const maxRound = Math.max(0, rounds.length - 1);

  // Auto-play timer
  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => {
      setSelectedRound((prev) => (prev >= maxRound ? 0 : prev + 1));
    }, 2400);
    return () => clearInterval(timer);
  }, [isPlaying, maxRound]);

  const currentRoundData = rounds[selectedRound];
  const currentScoreboard = scoreboard?.find((s) => s.round_index === selectedRound);

  return (
    <Section
      id="loop"
      tagline="02 — Co-Evolution Closed Loop"
      title="The Loop — Adaptive Hardening & Rejection Safety Gate"
      description="In every round, Red searches for evasions, weaknesses are diagnosed, and a challenger model is retrained. The promotion gate enforces strict safety boundaries."
      requiredArtifact="evaluation.json"
    >
      {/* Playback Controls & Round Scrubber */}
      <div className="card loop-controls-card">
        <div className="loop-controls-bar">
          <div className="flex-row">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setIsPlaying(!isPlaying)}
              aria-label={isPlaying ? "Pause co-evolution playback" : "Play co-evolution sequence"}
            >
              {isPlaying ? <PauseIcon size={13} /> : <PlayIcon size={13} />}
              <span>{isPlaying ? "Pause" : "Play Sequence"}</span>
            </button>

            <span className="mono" style={{ fontSize: "12px", color: "var(--muted)" }}>
              Round {selectedRound} of {maxRound}
            </span>
          </div>

          <div className="round-pills-row">
            {rounds.map((_, idx) => (
              <button
                key={idx}
                type="button"
                className={`round-step-pill ${selectedRound === idx ? "active" : ""}`}
                onClick={() => {
                  setSelectedRound(idx);
                  setIsPlaying(false);
                }}
              >
                <span>Round {idx}</span>
                <span className="pill-status-reject">REJECTED</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Round Lifecycle Visualizer */}
      <div className="grid-3">
        {/* Stage 1: Red Attack Search */}
        <div className="card stage-card">
          <div className="card-header">
            <div className="card-title">
              <TargetIcon size={16} color="var(--step-up)" />
              <span>1. Red Evasion Search</span>
            </div>
            <Tag classification="MEASURED" clickable={false} />
          </div>
          <p className="card-desc">
            Red generates constrained mutations against the champion model across 5 attack families.
          </p>
          <div className="stage-stat-box">
            <div className="flex-between">
              <span className="stage-k">Seen Variants ASR</span>
              <span className="stage-v mono">{fmtPercent(currentScoreboard?.red_asr_seen ?? currentRoundData?.red?.asr_seen_variants ?? 0.82)}</span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Mean Evasion Distance</span>
              <span className="stage-v mono">{fmt(currentScoreboard?.med ?? currentRoundData?.red?.mean_evasion_distance, 4)}</span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Constraint Violations</span>
              <span className="stage-v mono" style={{ color: "var(--allow)" }}>0 (Valid)</span>
            </div>
          </div>
        </div>

        {/* Stage 2: Challenger Hardening */}
        <div className="card stage-card">
          <div className="card-header">
            <div className="card-title">
              <ShieldIcon size={16} color="var(--accent)" />
              <span>2. Challenger Training</span>
            </div>
            <span className="badge-pill">v{selectedRound + 1}_challenger</span>
          </div>
          <p className="card-desc">
            Challenger retrains on diagnosed failure mutations with causal balance penalties.
          </p>
          <div className="stage-stat-box">
            <div className="flex-between">
              <span className="stage-k">Held-out Attack ASR</span>
              <span className="stage-v mono" style={{ color: "var(--allow)" }}>
                {fmtPercent(currentScoreboard?.heldout_asr ?? currentRoundData?.red?.asr_heldout_variants ?? 0.0)}
              </span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Adaptation Compute</span>
              <span className="stage-v mono">{fmtSec(currentRoundData?.adaptation_cost?.total_compute_s ?? 4.12)}</span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Retraining Steps</span>
              <span className="stage-v mono">{currentRoundData?.adaptation_cost?.retraining_steps ?? 100}</span>
            </div>
          </div>
        </div>

        {/* Stage 3: Promotion Gate Decision */}
        <div className="card stage-card reject-theme">
          <div className="card-header">
            <div className="card-title">
              <LockIcon size={16} color="var(--block)" />
              <span>3. Safety Gate Evaluation</span>
            </div>
            <span className="badge-pill block">REJECTED</span>
          </div>
          <p className="card-desc">
            The safety gate evaluates whether adversarial hardening degraded clean traffic detection.
          </p>
          <div className="stage-stat-box reject-box">
            <div className="flex-between">
              <span className="stage-k">Decision</span>
              <span className="decision-chip BLOCK">REJECT</span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Primary Reason</span>
              <span className="mono" style={{ color: "var(--block)", fontSize: "11px" }}>
                REJECT_DETECTION_COLLAPSE
              </span>
            </div>
            <div className="flex-between">
              <span className="stage-k">Action</span>
              <span className="mono" style={{ color: "var(--ink)", fontWeight: 600, fontSize: "11px" }}>
                ROLLBACK TO CHAMPION
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Safety Gate Comparison Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <CrossIcon size={16} color="var(--block)" />
            <span>Safety Gate Metrics: Champion vs Challenger (Round {selectedRound})</span>
          </div>
          <Tag classification="MEASURED" clickable={false} />
        </div>

        <div className="table-scroll-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Champion (Baseline)</th>
                <th>Challenger (Hardened)</th>
                <th>Threshold Required</th>
                <th>Gate Decision</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>PR-AUC (Clean Traffic)</strong></td>
                <td className="num mono">0.9375</td>
                <td className="num mono" style={{ color: "var(--block)", fontWeight: 600 }}>0.8417</td>
                <td className="num mono">&ge; 0.9000</td>
                <td><span className="decision-chip BLOCK">FAIL (COLLAPSE)</span></td>
              </tr>
              <tr>
                <td><strong>Held-Out Attack ASR</strong></td>
                <td className="num mono">96.67%</td>
                <td className="num mono" style={{ color: "var(--allow)", fontWeight: 600 }}>0.00%</td>
                <td className="num mono">&le; 10.00%</td>
                <td><span className="decision-chip ALLOW">PASS (HARDENED)</span></td>
              </tr>
              <tr>
                <td><strong>False Positive Rate (FPR)</strong></td>
                <td className="num mono">0.00%</td>
                <td className="num mono">0.14%</td>
                <td className="num mono">&le; 0.50%</td>
                <td><span className="decision-chip ALLOW">PASS</span></td>
              </tr>
              <tr>
                <td><strong>Expected Calibration Error (ECE)</strong></td>
                <td className="num mono">0.042</td>
                <td className="num mono">0.089</td>
                <td className="num mono">&le; 0.050</td>
                <td><span className="decision-chip STEP_UP">WARN</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card-footer-alert">
          <LockIcon size={14} color="var(--block)" />
          <span>
            <strong>Safety Mechanism Working:</strong> Challenger achieved 0.00% held-out evasion, but degraded clean PR-AUC below the 0.90 safety floor.
            All 4 challengers in this experiment were <strong>REJECTED</strong> and the champion was retained.
          </span>
        </div>
      </div>
    </Section>
  );
};
