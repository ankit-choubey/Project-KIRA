import React, { useState, useEffect } from "react";
import { Section } from "../components/Section";
import { ShieldIcon, TargetIcon, ActivityIcon, PlayIcon, PauseIcon, CheckIcon, LockIcon } from "../components/SvgIcons";
import { Tag } from "../components/Tag";

interface TxnScenario {
  id: string;
  name: string;
  amount: string;
  merchant: string;
  category: string;
  customer: string;
  velocity: string;
  speed: string;
  initialScore: number;
  evadedScore: number;
  initialDecision: "BLOCK" | "STEP_UP";
  evasionProbe: number;
  mutationSummary: string;
}

const SCENARIOS: TxnScenario[] = [
  {
    id: "TX-004281",
    name: "High-Speed Transit Flight Booking",
    amount: "₹8,421.00",
    merchant: "M-0042 (SkyAirlines Intl)",
    category: "4511 (Airlines)",
    customer: "C-0193 (Gold Tier)",
    velocity: "4 transactions in 90s",
    speed: "842.1 km/h (Impossible Velocity)",
    initialScore: 0.982,
    evadedScore: 0.142,
    initialDecision: "BLOCK",
    evasionProbe: 14,
    mutationSummary: "Amount -50.96% (₹4,128) + MCC Shift 5411 (Grocery)",
  },
  {
    id: "TX-009142",
    name: "Split Velocity Electronics Purchase",
    amount: "₹14,200.00",
    merchant: "M-0891 (ElectroMega Hub)",
    category: "5732 (Electronics)",
    customer: "C-0588 (Standard Tier)",
    velocity: "3 rapid attempts across 2 devices",
    speed: "42.0 km/h (Plausible Transit)",
    initialScore: 0.915,
    evadedScore: 0.218,
    initialDecision: "BLOCK",
    evasionProbe: 8,
    mutationSummary: "Amount Split ₹6,800 + Delay +25m Nocturnal Window",
  },
  {
    id: "TX-001055",
    name: "New Device Rapid Mandate Probe",
    amount: "₹5,000.00",
    merchant: "M-0120 (QuickStream Pay)",
    category: "4899 (Cable & Streaming)",
    customer: "C-0077 (Silver Tier)",
    velocity: "First transaction from Device D-9901",
    speed: "0.0 km/h (Static)",
    initialScore: 0.884,
    evadedScore: 0.195,
    initialDecision: "BLOCK",
    evasionProbe: 18,
    mutationSummary: "Amount -40% (₹3,000) + Replayed Recurring Mandate Token",
  },
];

export const ClosedLoopSimulation: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<TxnScenario>(SCENARIOS[0]);
  const [activeStep, setActiveStep] = useState<number>(1);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentProbe, setCurrentProbe] = useState<number>(1);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1); // 1x or 2x

  useEffect(() => {
    let timer: any;
    if (isPlaying) {
      const stepDuration = 2200 / playbackSpeed;
      timer = setTimeout(() => {
        if (activeStep < 4) {
          setActiveStep((prev) => prev + 1);
        } else {
          setIsPlaying(false);
        }
      }, stepDuration);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, activeStep, playbackSpeed]);

  // Stepped Probe Animation when Step 3 is active
  useEffect(() => {
    let probeTimer: any;
    if (activeStep === 3) {
      setCurrentProbe(1);
      const target = selectedScenario.evasionProbe;
      const intervalMs = (80 / playbackSpeed);

      let p = 1;
      probeTimer = setInterval(() => {
        p += 1;
        if (p <= target) {
          setCurrentProbe(p);
        } else {
          clearInterval(probeTimer);
        }
      }, intervalMs);
    }
    return () => clearInterval(probeTimer);
  }, [activeStep, selectedScenario, playbackSpeed]);

  const handlePlayToggle = () => {
    if (isPlaying) {
      setIsPlaying(false);
    } else {
      if (activeStep === 4) setActiveStep(1);
      setIsPlaying(true);
    }
  };

  return (
    <Section
      id="simulation"
      tagline="02 — Interactive Replay Instrument"
      title="See KIRA Think — The Closed-Loop Adversarial Cycle"
      description="Follow a suspicious payment event through 41-D causal representation, blue detector risk scoring, red adversary mutation probing, and safety gate rollback."
    >
      {/* Top Interactive Scenario Bar */}
      <div className="card" style={{ marginBottom: "20px", background: "var(--surface-2)" }}>
        <div className="flex-between" style={{ flexWrap: "wrap", gap: "16px" }}>
          <div>
            <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>
              Select Live Payment Event Scenario
            </span>
            <div style={{ display: "flex", gap: "8px", marginTop: "8px", flexWrap: "wrap" }}>
              {SCENARIOS.map((sc) => (
                <button
                  key={sc.id}
                  className={`btn ${selectedScenario.id === sc.id ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => {
                    setSelectedScenario(sc);
                    setActiveStep(1);
                    setIsPlaying(false);
                  }}
                  style={{ fontSize: "12px", padding: "6px 12px" }}
                >
                  <strong>{sc.id}</strong>: {sc.name} ({sc.amount})
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ display: "flex", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "4px", padding: "2px" }}>
              <button
                className={`btn btn-icon-toggle ${playbackSpeed === 1 ? "active" : ""}`}
                onClick={() => setPlaybackSpeed(1)}
                style={{ fontSize: "11px", padding: "4px 8px" }}
              >
                1x Speed
              </button>
              <button
                className={`btn btn-icon-toggle ${playbackSpeed === 2 ? "active" : ""}`}
                onClick={() => setPlaybackSpeed(2)}
                style={{ fontSize: "11px", padding: "4px 8px" }}
              >
                2x Fast
              </button>
            </div>

            <button
              className="btn btn-primary"
              onClick={handlePlayToggle}
              style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: "140px", justifyContent: "center" }}
            >
              {isPlaying ? <PauseIcon size={14} color="#FFF" /> : <PlayIcon size={14} color="#FFF" />}
              <span>{isPlaying ? "Pause Replay" : "▶ Run Simulation"}</span>
            </button>

            <Tag classification="MEASURED" clickable={false} />
          </div>
        </div>
      </div>

      {/* 4 Spacious Connected Pipeline Step Cards */}
      <div className="pipeline-track">
        {/* Step 1 */}
        <div
          className={`pipeline-step-card ${activeStep === 1 ? "active" : ""}`}
          onClick={() => { setActiveStep(1); setIsPlaying(false); }}
        >
          <div className="flex-between">
            <span className="pipeline-step-num">STAGE 01</span>
            {activeStep > 1 && <CheckIcon size={14} color="var(--allow)" />}
          </div>
          <span className="pipeline-step-title">41-D Causal Representation</span>
          <span className="pipeline-step-badge" style={{ background: "var(--accent-soft)", color: "var(--accent)" }}>
            25 Tabular + 16 Graph
          </span>
        </div>

        {/* Step 2 */}
        <div
          className={`pipeline-step-card ${activeStep === 2 ? "active" : ""}`}
          onClick={() => { setActiveStep(2); setIsPlaying(false); }}
        >
          <div className="flex-between">
            <span className="pipeline-step-num">STAGE 02</span>
            {activeStep > 2 && <CheckIcon size={14} color="var(--allow)" />}
          </div>
          <span className="pipeline-step-title">Blue Champion Detector</span>
          <span className="pipeline-step-badge" style={{ background: "var(--block-soft)", color: "var(--block)" }}>
            Initial Decision: BLOCK
          </span>
        </div>

        {/* Step 3 */}
        <div
          className={`pipeline-step-card ${activeStep === 3 ? "active" : ""}`}
          onClick={() => { setActiveStep(3); setIsPlaying(false); }}
        >
          <div className="flex-between">
            <span className="pipeline-step-num">STAGE 03</span>
            {activeStep > 3 && <CheckIcon size={14} color="var(--allow)" />}
          </div>
          <span className="pipeline-step-title">Red Adversarial Probing</span>
          <span className="pipeline-step-badge" style={{ background: "var(--step-up-soft)", color: "var(--step-up)" }}>
            20 Probes · Budget 20
          </span>
        </div>

        {/* Step 4 */}
        <div
          className={`pipeline-step-card ${activeStep === 4 ? "active" : ""}`}
          onClick={() => { setActiveStep(4); setIsPlaying(false); }}
        >
          <div className="flex-between">
            <span className="pipeline-step-num">STAGE 04</span>
            {activeStep === 4 && <CheckIcon size={14} color="var(--allow)" />}
          </div>
          <span className="pipeline-step-title">Safety Gate &amp; Rollback</span>
          <span className="pipeline-step-badge" style={{ background: "var(--allow-soft)", color: "var(--allow)" }}>
            Reject Collapse ➔ Rollback
          </span>
        </div>
      </div>

      {/* Main Dynamic Stage Display */}
      <div className="card" style={{ padding: "24px" }}>
        {/* ================= STAGE 1: 41-D CAUSAL REPRESENTATION ================= */}
        {activeStep === 1 && (
          <div>
            <div className="card-header">
              <div className="card-title">
                <ActivityIcon size={20} color="var(--accent)" />
                <span>Stage 1: Dual Causal Feature Engineering (Strictly Causal t &le; t_event)</span>
              </div>
              <span className="badge-pill allow">0 Temporal Leakage Violations</span>
            </div>

            <p style={{ margin: "6px 0 16px", fontSize: "13.5px", color: "var(--text)" }}>
              The raw transaction from <strong>{selectedScenario.customer}</strong> for <strong>{selectedScenario.amount}</strong> at <strong>{selectedScenario.merchant}</strong> is projected into a 41-dimensional representation. Historical features exclude the current transaction to prevent self-leakage, and no future graph relationships are observable.
            </p>

            {/* Tensor Fusion Diagram */}
            <div className="tensor-fusion-container">
              {/* Tabular Branch */}
              <div className="tensor-card">
                <div className="tensor-title">25 Historical Tabular Features</div>
                <div className="tensor-pill-list">
                  <span className="tensor-pill">velocity_1h: 4</span>
                  <span className="tensor-pill">velocity_24h: 7</span>
                  <span className="tensor-pill">speed_kmh: 842.1</span>
                  <span className="tensor-pill">dist_home_km: 1,420</span>
                  <span className="tensor-pill">amt_to_avg_ratio: 4.82x</span>
                  <span className="tensor-pill">auth_failed_count: 0</span>
                </div>
              </div>

              <div className="mono" style={{ fontSize: "20px", fontWeight: 700, color: "var(--accent)" }}>+</div>

              {/* Graph Branch */}
              <div className="tensor-card">
                <div className="tensor-title">16-D Graph Topological Embeddings</div>
                <div className="tensor-pill-list">
                  <span className="tensor-pill">emb_cust_dim0..3</span>
                  <span className="tensor-pill">emb_merch_dim4..7</span>
                  <span className="tensor-pill">emb_device_dim8..11</span>
                  <span className="tensor-pill">emb_agent_dim12..15</span>
                  <span className="tensor-pill">bipartite_clustering: 0.88</span>
                </div>
              </div>

              <div className="mono" style={{ fontSize: "20px", fontWeight: 700, color: "var(--accent)" }}>➔</div>

              {/* Fused Output */}
              <div className="tensor-card" style={{ border: "1.5px solid var(--accent)", background: "var(--accent-soft)" }}>
                <div className="tensor-title" style={{ color: "var(--accent)" }}>41-D Fused Input Vector</div>
                <div className="mono" style={{ fontSize: "12px", fontWeight: 700, color: "var(--ink)" }}>
                  X[41] = [T_1..25 || G_1..16]
                </div>
                <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "4px" }}>
                  Ready for LightGBM Champion Scoring
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= STAGE 2: BLUE DETECTOR RISK SCORING ================= */}
        {activeStep === 2 && (
          <div>
            <div className="card-header">
              <div className="card-title">
                <ShieldIcon size={20} color="var(--block)" />
                <span>Stage 2: Blue Champion Model Evaluation &amp; Policy Routing</span>
              </div>
              <span className="badge-pill block">Decision: BLOCK</span>
            </div>

            <p style={{ margin: "6px 0 16px", fontSize: "13.5px", color: "var(--text)" }}>
              The Champion LightGBM detector scores the 41-D feature vector. Isotonic calibration maps raw margin output to calibrated posterior probability p(fraud | x) = 0.9820.
            </p>

            <div className="grid-2" style={{ gap: "20px" }}>
              {/* Left: Risk Meter Gauge */}
              <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
                <div className="flex-between">
                  <span style={{ fontSize: "12px", textTransform: "uppercase", fontWeight: 700, color: "var(--muted)" }}>
                    Calibrated Posterior Risk Score
                  </span>
                  <span className="mono" style={{ fontSize: "22px", fontWeight: 700, color: "var(--block)" }}>
                    {selectedScenario.initialScore.toFixed(3)}
                  </span>
                </div>

                <div className="risk-meter-bar-track">
                  <div
                    className="risk-meter-bar-fill"
                    style={{ width: `${selectedScenario.initialScore * 100}%`, background: "var(--block)" }}
                  />
                </div>

                <div className="flex-between" style={{ fontSize: "11px", color: "var(--muted)" }}>
                  <span>0.000 (ALLOW)</span>
                  <span>Threshold: 0.500 (STEP_UP)</span>
                  <span>1.000 (BLOCK)</span>
                </div>

                <div style={{ marginTop: "16px", padding: "10px", background: "var(--surface)", borderRadius: "4px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>Cost-Sensitive Policy Action:</span>
                  <span className="decision-chip BLOCK" style={{ fontSize: "13px", padding: "4px 12px" }}>
                    BLOCK TRANSACTION
                  </span>
                </div>
              </div>

              {/* Right: TreeSHAP Feature Attributions */}
              <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
                <span style={{ fontSize: "12px", textTransform: "uppercase", fontWeight: 700, color: "var(--muted)" }}>
                  Primary TreeSHAP Risk Explanations
                </span>

                <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div>
                    <div className="flex-between" style={{ fontSize: "12px" }}>
                      <span>1. speed_kmh ({selectedScenario.speed})</span>
                      <span className="mono" style={{ color: "var(--block)", fontWeight: 600 }}>+0.420 SHAP</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", background: "var(--surface)", borderRadius: "3px", overflow: "hidden", marginTop: "3px" }}>
                      <div style={{ width: "84%", height: "100%", background: "var(--block)" }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex-between" style={{ fontSize: "12px" }}>
                      <span>2. amt_to_avg_ratio (High Spending Spike)</span>
                      <span className="mono" style={{ color: "var(--block)", fontWeight: 600 }}>+0.285 SHAP</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", background: "var(--surface)", borderRadius: "3px", overflow: "hidden", marginTop: "3px" }}>
                      <div style={{ width: "57%", height: "100%", background: "var(--block)" }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex-between" style={{ fontSize: "12px" }}>
                      <span>3. velocity_1h (4 attempts in 90s)</span>
                      <span className="mono" style={{ color: "var(--block)", fontWeight: 600 }}>+0.190 SHAP</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", background: "var(--surface)", borderRadius: "3px", overflow: "hidden", marginTop: "3px" }}>
                      <div style={{ width: "38%", height: "100%", background: "var(--block)" }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= STAGE 3: RED ADVERSARY PROBING ================= */}
        {activeStep === 3 && (
          <div>
            <div className="card-header">
              <div className="card-title">
                <TargetIcon size={20} color="var(--step-up)" />
                <span>Stage 3: Red Team Black-Box Perturbation Search (Probe #{currentProbe} / 20)</span>
              </div>
              <span className="badge-pill warn">
                {currentProbe >= selectedScenario.evasionProbe ? "Evasion Found (Decision Flipped)" : "Searching..."}
              </span>
            </div>

            <p style={{ margin: "6px 0 16px", fontSize: "13.5px", color: "var(--text)" }}>
              The adversary executes query-budgeted gradient-free mutations against the black-box detector while respecting physical constraint masks (customer ID and baseline balances cannot be forged).
            </p>

            <div className="grid-2" style={{ gap: "20px" }}>
              {/* Left: Terminal Console Stream */}
              <div>
                <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 700 }}>
                  Adversarial Query Console
                </span>
                <div className="probe-terminal-box" style={{ marginTop: "6px" }}>
                  <div className="probe-log-line">
                    <span className="probe-log-time">[00:00.12]</span>
                    <span>Target: {selectedScenario.id} | Initial Score: {selectedScenario.initialScore} [BLOCK]</span>
                  </div>
                  {Array.from({ length: currentProbe }).map((_, idx) => {
                    const probeNum = idx + 1;
                    const isEvasion = probeNum === selectedScenario.evasionProbe;
                    return (
                      <div key={probeNum} className={`probe-log-line ${isEvasion ? "evaded" : (probeNum === currentProbe ? "active" : "")}`}>
                        <span className="probe-log-time">[00:0{Math.floor(probeNum / 2)}.{probeNum * 4}]</span>
                        <span>
                          Probe #{probeNum}: {probeNum < selectedScenario.evasionProbe ? `Mutating Amount -> Score: ${(selectedScenario.initialScore - (probeNum * 0.045)).toFixed(3)} [BLOCK]` : `Applying ${selectedScenario.mutationSummary} -> Score: ${selectedScenario.evadedScore} [ALLOW]`}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right: Counterfactual Mutation Diff */}
              <div className="stage-stat-box" style={{ background: "var(--surface-2)" }}>
                <span style={{ fontSize: "12px", textTransform: "uppercase", fontWeight: 700, color: "var(--muted)" }}>
                  Counterfactual Mutation Delta
                </span>

                <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div className="flex-between" style={{ padding: "6px 8px", background: "var(--surface)", borderRadius: "4px" }}>
                    <span>Original Amount (Blocked):</span>
                    <span className="mono" style={{ color: "var(--block)", fontWeight: 700 }}>{selectedScenario.amount}</span>
                  </div>
                  <div className="flex-between" style={{ padding: "6px 8px", background: "var(--surface)", borderRadius: "4px" }}>
                    <span>Mutated Amount (Evaded):</span>
                    <span className="mono" style={{ color: "var(--allow)", fontWeight: 700 }}>
                      {currentProbe >= selectedScenario.evasionProbe ? (selectedScenario.id === "TX-004281" ? "₹4,128.00 (-50.96%)" : "₹6,800.00 (-52.1%)") : "Probing…"}
                    </span>
                  </div>
                  <div className="flex-between" style={{ padding: "6px 8px", background: "var(--surface)", borderRadius: "4px" }}>
                    <span>Minimum Evasion Distance (MED):</span>
                    <span className="mono" style={{ fontWeight: 600 }}>2.8488 (Normalized L2)</span>
                  </div>
                  <div className="flex-between" style={{ padding: "6px 8px", background: "var(--allow-soft)", borderRadius: "4px" }}>
                    <span>Constraint Mask Verification:</span>
                    <span className="mono" style={{ color: "var(--allow)", fontWeight: 700 }}>
                      0 Violations (Customer Immutable)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= STAGE 4: SAFETY GATE & ROLLBACK ================= */}
        {activeStep === 4 && (
          <div>
            <div className="card-header">
              <div className="card-title">
                <LockIcon size={20} color="var(--block)" />
                <span>Stage 4: Automated Safety Promotion Gate &amp; Champion Rollback</span>
              </div>
              <span className="badge-pill block">REJECT_DETECTION_COLLAPSE</span>
            </div>

            <p style={{ margin: "6px 0 16px", fontSize: "13.5px", color: "var(--text)" }}>
              The evasion is captured in the Prioritized Replay Buffer to train a Challenger model. The safety gate evaluates the Challenger across 7 multi-objective criteria. When the Challenger causes clean traffic detection to collapse, it is <strong>automatically rejected and rolled back</strong>.
            </p>

            <div className="grid-2" style={{ gap: "20px" }}>
              {/* Left: Gate Verification Criteria Table */}
              <div className="table-scroll-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Gate Verification Metric</th>
                      <th>Threshold Required</th>
                      <th>Challenger Value</th>
                      <th>Gate Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ background: "var(--block-soft)" }}>
                      <td><strong>Clean PR-AUC Floor</strong></td>
                      <td className="num mono">&ge; 0.9000</td>
                      <td className="num mono" style={{ color: "var(--block)", fontWeight: 700 }}>0.8417 (Drop)</td>
                      <td><span className="decision-chip BLOCK">FAIL (COLLAPSE)</span></td>
                    </tr>
                    <tr>
                      <td><strong>Held-Out Attack ASR</strong></td>
                      <td className="num mono">&le; 10.0%</td>
                      <td className="num mono" style={{ color: "var(--allow)", fontWeight: 700 }}>0.00%</td>
                      <td><span className="decision-chip ALLOW">PASS</span></td>
                    </tr>
                    <tr>
                      <td><strong>False Positive Rate (FPR)</strong></td>
                      <td className="num mono">&le; 0.50%</td>
                      <td className="num mono">0.00%</td>
                      <td><span className="decision-chip ALLOW">PASS</span></td>
                    </tr>
                    <tr>
                      <td><strong>Anti-Forgetting Retention</strong></td>
                      <td className="num mono">&ge; 0.950</td>
                      <td className="num mono">0.9680</td>
                      <td><span className="decision-chip ALLOW">PASS</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Right: Security Rollback Decision Banner */}
              <div className="stage-stat-box reject-box" style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
                <span style={{ fontSize: "11px", color: "var(--block)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.06em" }}>
                  Automated Security Rollback Enforced
                </span>

                <h3 style={{ margin: "8px 0", fontSize: "18px", color: "var(--block)" }}>
                  Challenger Rejected: Champion Baseline Retained
                </h3>

                <p style={{ fontSize: "13px", lineHeight: "1.5", margin: 0, color: "var(--ink)" }}>
                  The model successfully suppressed known attack variants, but lost statistical sensitivity on subtle edge-case transactions (PR-AUC dropped from 0.9375 to 0.8417). KIRA refused to deploy the compromised model.
                </p>

                <div style={{ marginTop: "14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="mono" style={{ fontSize: "11.5px", color: "var(--muted)" }}>
                    Rule: Strict Pareto Safety Invariant
                  </span>
                  <span className="decision-chip ALLOW" style={{ fontWeight: 700 }}>
                    ACTIVE CHAMPION SECURED
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Section>
  );
};
