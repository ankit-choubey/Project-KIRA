import React, { useState } from "react";
import { ShieldIcon, SunIcon, MoonIcon, InfoIcon } from "./SvgIcons";
import { Tag } from "./Tag";
import type { Health } from "../data/types";
import { DATA_MODE } from "../data/source";

interface HeaderProps {
  health: Health | null;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  activeSection: string;
}

const NAV_ITEMS = [
  { href: "#mission", label: "01 Mission" },
  { href: "#simulation", label: "02 See KIRA Think" },
  { href: "#loop", label: "03 The Loop" },
  { href: "#graph-fusion", label: "04 Graph Fusion" },
  { href: "#attack-console", label: "05 Attack Engine" },
  { href: "#weakness", label: "06 Weaknesses" },
  { href: "#three-worlds", label: "07 Three Worlds" },
  { href: "#real-world", label: "08 Real-World & Invariance" },
  { href: "#experiments", label: "09 Experiments" },
  { href: "#monitor", label: "10 Monitor" },
  { href: "#evidence", label: "11 Evidence" },
];

export const Header: React.FC<HeaderProps> = ({
  health,
  theme,
  onToggleTheme,
  activeSection,
}) => {
  const [showLegend, setShowLegend] = useState(false);

  return (
    <header className="masthead-container">
      <div className="masthead-main">
        {/* Brand */}
        <a href="#mission" className="brand-group">
          <div className="brand-shield-wrapper">
            <ShieldIcon size={20} className="brand-shield-icon" />
          </div>
          <div className="brand-text-wrapper">
            <span className="brand-title">KIRA <span className="brand-sub">AI Defense Lab</span></span>
            <span className="brand-subtitle">Mastercard Adversarial Security</span>
          </div>
        </a>

        {/* Navigation */}
        <nav className="masthead-nav" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => {
            const isActive = activeSection === item.href.slice(1);
            return (
              <a
                key={item.href}
                href={item.href}
                className={`nav-link ${isActive ? "active" : ""}`}
              >
                {item.label}
              </a>
            );
          })}
        </nav>

        {/* Actions & Provenance Status */}
        <div className="masthead-actions">
          {/* Legend toggle */}
          <button
            type="button"
            className={`btn-icon-toggle ${showLegend ? "active" : ""}`}
            onClick={() => setShowLegend(!showLegend)}
            title="Toggle Provenance Tag Legend"
            aria-label="Toggle Provenance Legend"
          >
            <InfoIcon size={15} />
          </button>

          {/* Mode Pill */}
          <span className={`status-pill ${DATA_MODE === "live" ? "status-live" : "status-static"}`}>
            {DATA_MODE === "live" ? "LIVE API" : "STATIC REPLAY"}
          </span>

          {/* Run ID Chip */}
          <div className="run-id-badge" title={health?.detail || "Run ID"}>
            <span className="run-id-dot" />
            <code className="run-id-text">
              {health?.run_id ? health.run_id.slice(0, 16) + "…" : "run_authoritative"}
            </code>
          </div>

          {/* Theme Toggle */}
          <button
            type="button"
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
            aria-label="Toggle theme"
          >
            {theme === "light" ? <MoonIcon size={16} /> : <SunIcon size={16} />}
          </button>
        </div>
      </div>

      {/* Ecosystem Global Navigation Links */}
      <div className="masthead-ecosystem-bar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 20px", background: "rgba(0, 0, 0, 0.35)", borderTop: "1px solid rgba(255, 255, 255, 0.06)", fontSize: "11px", overflowX: "auto" }}>
        <div style={{ display: "flex", gap: "14px", alignItems: "center", whiteSpace: "nowrap" }}>
          <span style={{ color: "var(--muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Verified Ecosystem:</span>
          <a href="https://kaleidoscopic-quokka-251564.netlify.app" target="_blank" rel="noopener" style={{ color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>
            🌐 Netlify Live UI
          </a>
          <a href="https://project-kira-api.onrender.com/docs" target="_blank" rel="noopener" style={{ color: "var(--allow)", textDecoration: "none", fontWeight: 600 }}>
            ⚡ Render FastAPI Docs
          </a>
          <a href="https://huggingface.co/spaces/ankit-choubey/Project-KIRA" target="_blank" rel="noopener" style={{ color: "var(--step-up)", textDecoration: "none", fontWeight: 600 }}>
            🤗 HF Showcase (Project-KIRA)
          </a>
          <a href="https://github.com/ankit-choubey/Project-KIRA/tree/main/notebooks/kaggle" target="_blank" rel="noopener" style={{ color: "var(--ink)", textDecoration: "none", fontWeight: 600 }}>
            🔬 Kaggle CPU Notebooks (5)
          </a>
          <a href="https://github.com/ankit-choubey/Project-KIRA" target="_blank" rel="noopener" style={{ color: "var(--ink)", textDecoration: "none", fontWeight: 600 }}>
            💻 GitHub Source
          </a>
        </div>
        <div style={{ display: "flex", gap: "8px", alignItems: "center", whiteSpace: "nowrap" }}>
          <span className="badge-pill allow" style={{ fontSize: "10px", padding: "2px 6px" }}>22/22 SHA-256</span>
          <span className="badge-pill" style={{ fontSize: "10px", padding: "2px 6px" }}>225 Tests Passed</span>
        </div>
      </div>

      {/* Expandable Provenance Legend */}
      {showLegend && (
        <div className="masthead-legend-drawer">
          <div className="legend-items">
            <span className="legend-label">PROVENANCE VOCABULARY:</span>
            <div className="legend-chip-item">
              <Tag classification="MEASURED" clickable={false} />
              <span>Verified pipeline run metric</span>
            </div>
            <div className="legend-chip-item">
              <Tag classification="EXP-007-A" clickable={false} />
              <span>Controlled hypothesis test</span>
            </div>
            <div className="legend-chip-item">
              <Tag classification="FAILURE FINDING" clickable={false} />
              <span>Reported negative result / vulnerability boundary</span>
            </div>
            <div className="legend-chip-item">
              <Tag classification="REAL-WORLD DATA" clickable={false} />
              <span>284k ULB real cardholder dataset</span>
            </div>
            <div className="legend-chip-item">
              <Tag classification="LOOPBACK BENCHMARK" clickable={false} />
              <span>In-process HTTP loopback timing</span>
            </div>
          </div>
        </div>
      )}

      {/* Fixture Alert Banner if run is fixture */}
      {health?.is_fixture && (
        <div className="fixture-warning-bar">
          <strong>FIXTURE DATA ACTIVE</strong> — values are synthetic development placeholders from fixtures.py, not measured research runs.
        </div>
      )}
    </header>
  );
};
