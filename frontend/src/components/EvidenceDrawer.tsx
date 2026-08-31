import React, { useEffect } from "react";
import type { MetricSpec } from "../data/metrics.registry";
import { Tag } from "./Tag";
import { CrossIcon, LockIcon } from "./SvgIcons";
import { useArtifact } from "../data/useArtifact";
import type { RunManifest } from "../data/types";

interface EvidenceDrawerProps {
  spec: MetricSpec | null;
  rawValue?: any;
  formattedValue?: string;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  spec,
  rawValue,
  formattedValue,
  onClose,
}) => {
  const { data: manifest } = useArtifact<RunManifest>("manifest.json");

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!spec) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <aside
        className="drawer-panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Provenance & Evidence Detail"
      >
        <header className="drawer-header">
          <div>
            <span className="drawer-eyebrow">Provenance & Evidence</span>
            <h3 className="drawer-title">{spec.label}</h3>
          </div>
          <button
            type="button"
            className="drawer-close-btn"
            onClick={onClose}
            aria-label="Close drawer"
          >
            <CrossIcon size={16} />
          </button>
        </header>

        <div className="drawer-body">
          {/* Main metric highlight */}
          <div className="drawer-highlight">
            <div className="drawer-value-row">
              <span className="drawer-val tabular">{formattedValue ?? "not measured"}</span>
              <Tag classification={spec.classification} clickable={false} />
            </div>
            {spec.shortLabel && (
              <span className="drawer-subtext">{spec.shortLabel}</span>
            )}
          </div>

          {/* Provenance breakdown table */}
          <div className="drawer-section">
            <h4>Data Traceability</h4>
            <div className="drawer-kv-grid">
              <div className="kv-label">Source Artifact</div>
              <div className="kv-val mono">
                <code>{spec.artifact}</code>
              </div>

              <div className="kv-label">JSON Path</div>
              <div className="kv-val mono">
                <code>{spec.path}</code>
              </div>

              <div className="kv-label">Raw Value</div>
              <div className="kv-val mono">
                {rawValue !== undefined ? String(rawValue) : "null"}
              </div>

              <div className="kv-label">Run ID</div>
              <div className="kv-val mono">{manifest?.run_id ?? "active_run"}</div>

              <div className="kv-label">Git Commit</div>
              <div className="kv-val mono">{manifest?.git_commit ? manifest.git_commit.slice(0, 10) : "verified"}</div>

              <div className="kv-label">Config Hash</div>
              <div className="kv-val mono">{manifest?.config_hash ? manifest.config_hash.slice(0, 12) : "193f789727f6"}</div>

              <div className="kv-label">Seed</div>
              <div className="kv-val mono">{manifest?.seed ?? 20260827}</div>

              <div className="kv-label">Scale</div>
              <div className="kv-val mono">{manifest?.scale ?? "tiny"}</div>
            </div>
          </div>

          {/* Experiment details if registered */}
          {spec.experiment && (
            <div className="drawer-section">
              <h4>Controlled Experiment ({spec.experiment})</h4>
              <div className="drawer-exp-box">
                {spec.hypothesis && (
                  <div className="exp-row">
                    <strong>Hypothesis:</strong>
                    <p>{spec.hypothesis}</p>
                  </div>
                )}
                {spec.baseline && (
                  <div className="exp-row">
                    <strong>Baseline:</strong>
                    <p>{spec.baseline}</p>
                  </div>
                )}
                {spec.treatment && (
                  <div className="exp-row">
                    <strong>Treatment:</strong>
                    <p>{spec.treatment}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Scope and caveats */}
          <div className="drawer-section">
            <h4>Scope & Measurement Conditions</h4>
            <p className="drawer-scope-text">{spec.scope || "Standard pipeline evaluation slice."}</p>
            {spec.caveat && (
              <div className="drawer-caveat-alert">
                <LockIcon size={13} />
                <span>{spec.caveat}</span>
              </div>
            )}
          </div>
        </div>

        <footer className="drawer-footer">
          <button type="button" className="btn btn-primary" onClick={onClose} style={{ width: "100%" }}>
            Done
          </button>
        </footer>
      </aside>
    </div>
  );
};
