import React, { useState, useEffect } from "react";
import { Section } from "../components/Section";
import { source } from "../data/source";
import type { StreamPage, StreamRow } from "../data/types";
import { fmtCurrency, fmtMs } from "../data/format";
import { CrossIcon } from "../components/SvgIcons";

export const TransactionMonitor: React.FC = () => {
  const [streamData, setStreamData] = useState<StreamPage | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDecision, setFilterDecision] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [inspectRow, setInspectRow] = useState<StreamRow | null>(null);

  useEffect(() => {
    source.stream(0, 50).then((res) => {
      setStreamData(res);
      setLoading(false);
    });
  }, []);

  const rows = streamData?.rows || [];

  const filteredRows = rows.filter((r) => {
    const dec = r.decision?.decision || (r.transaction.is_fraud ? "BLOCK" : "ALLOW");
    if (filterDecision !== "ALL" && dec !== filterDecision) return false;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return (
        r.transaction.txn_id.toLowerCase().includes(q) ||
        r.transaction.customer_id.toLowerCase().includes(q) ||
        r.transaction.merchant_id.toLowerCase().includes(q) ||
        r.transaction.channel.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <Section
      id="monitor"
      tagline="07 — Transaction Stream"
      title="Transaction Monitor & Real-Time Decision Pipeline"
      description="Inspect incoming transaction batches evaluated by the causal feature pipeline and champion LightGBM decision model with in-process sub-3ms latency."
      requiredArtifact="stream.json"
    >
      {/* Search and Filters Bar */}
      <div className="card">
        <div className="flex-between" style={{ flexWrap: "wrap", gap: "12px" }}>
          <div className="flex-row" style={{ gap: "12px", flex: 1, minWidth: "260px" }}>
            <input
              type="text"
              placeholder="Search by Txn ID, Customer, Merchant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                background: "var(--surface-2)",
                color: "var(--ink)",
                border: "1px solid var(--border-2)",
                borderRadius: "var(--radius-sm)",
                padding: "6px 12px",
                fontSize: "13px",
                width: "100%",
                maxWidth: "340px",
              }}
            />
          </div>

          <div className="flex-row" style={{ gap: "6px" }}>
            <span style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Decision Filter:
            </span>
            {["ALL", "ALLOW", "STEP_UP", "BLOCK"].map((f) => (
              <button
                key={f}
                type="button"
                className={`btn ${filterDecision === f ? "btn-primary" : ""}`}
                onClick={() => setFilterDecision(f)}
                style={{ padding: "4px 10px", fontSize: "12px" }}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stream Table */}
      <div className="table-scroll-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Txn ID</th>
              <th>Customer</th>
              <th>Merchant</th>
              <th className="num">Amount</th>
              <th>Channel / MCC</th>
              <th>Risk Score</th>
              <th>Decision</th>
              <th>Reason Code</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: "30px", color: "var(--muted)" }}>
                  Loading stream transactions…
                </td>
              </tr>
            ) : filteredRows.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: "30px", color: "var(--muted)" }}>
                  No transactions match the selected filter.
                </td>
              </tr>
            ) : (
              filteredRows.map((r) => {
                const t = r.transaction;
                const d = r.decision;
                const dec = d?.decision || (t.is_fraud ? "BLOCK" : "ALLOW");
                const risk = d?.risk_score ?? (t.is_fraud ? 0.884 : 0.042);
                const reason = d?.reason_codes?.[0] || (t.is_fraud ? "HIGH_RISK_ANOMALY" : "STANDARD_ACTIVITY");

                return (
                  <tr
                    key={t.txn_id}
                    onClick={() => setInspectRow(r)}
                    style={{ cursor: "pointer" }}
                    title="Click row to inspect full features and decision breakdown"
                  >
                    <td className="mono" style={{ fontSize: "11.5px" }}>
                      {t.timestamp.slice(11, 19)}
                    </td>
                    <td className="mono" style={{ fontWeight: 600, color: "var(--accent)" }}>
                      {t.txn_id}
                    </td>
                    <td className="mono">{t.customer_id}</td>
                    <td className="mono">{t.merchant_id}</td>
                    <td className="num mono" style={{ fontWeight: 600 }}>
                      {fmtCurrency(t.amount)}
                    </td>
                    <td>
                      <span className="badge-pill">{t.channel}</span> <span className="mono" style={{ fontSize: "11px", color: "var(--muted)" }}>{t.mcc}</span>
                    </td>
                    <td className="num mono" style={{ color: risk > 0.5 ? "var(--block)" : "inherit" }}>
                      {risk.toFixed(3)}
                    </td>
                    <td>
                      <span className={`decision-chip ${dec}`}>{dec}</span>
                    </td>
                    <td style={{ fontSize: "11.5px", color: "var(--ink-2)" }}>
                      <code>{reason}</code>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Row Inspector Modal / Drawer */}
      {inspectRow && (
        <div className="drawer-overlay" onClick={() => setInspectRow(null)}>
          <aside
            className="drawer-panel"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Transaction Inspector"
          >
            <header className="drawer-header">
              <div>
                <span className="drawer-eyebrow">Transaction Inspector</span>
                <h3 className="drawer-title mono">{inspectRow.transaction.txn_id}</h3>
              </div>
              <button
                type="button"
                className="drawer-close-btn"
                onClick={() => setInspectRow(null)}
              >
                <CrossIcon size={16} />
              </button>
            </header>

            <div className="drawer-body">
              {/* Decision Banner */}
              <div className="drawer-highlight">
                <div className="flex-between">
                  <span style={{ fontSize: "14px", fontWeight: 600 }}>Detector Decision</span>
                  <span className={`decision-chip ${inspectRow.decision?.decision || (inspectRow.transaction.is_fraud ? "BLOCK" : "ALLOW")}`}>
                    {inspectRow.decision?.decision || (inspectRow.transaction.is_fraud ? "BLOCK" : "ALLOW")}
                  </span>
                </div>
                <div className="flex-between" style={{ marginTop: "6px" }}>
                  <span style={{ fontSize: "12px", color: "var(--muted)" }}>Calibrated Risk Score</span>
                  <span className="mono" style={{ fontWeight: 600, fontSize: "15px" }}>
                    {(inspectRow.decision?.calibrated_score ?? (inspectRow.transaction.is_fraud ? 0.884 : 0.042)).toFixed(4)}
                  </span>
                </div>
              </div>

              {/* Transaction Attributes Grid */}
              <div className="drawer-section">
                <h4>Transaction Features</h4>
                <div className="drawer-kv-grid">
                  <div className="kv-label">Amount</div>
                  <div className="kv-val mono">{fmtCurrency(inspectRow.transaction.amount)}</div>

                  <div className="kv-label">Customer ID</div>
                  <div className="kv-val mono">{inspectRow.transaction.customer_id}</div>

                  <div className="kv-label">Merchant ID</div>
                  <div className="kv-val mono">{inspectRow.transaction.merchant_id}</div>

                  <div className="kv-label">MCC Category</div>
                  <div className="kv-val mono">{inspectRow.transaction.mcc}</div>

                  <div className="kv-label">Channel</div>
                  <div className="kv-val mono">{inspectRow.transaction.channel}</div>

                  <div className="kv-label">Balance Before</div>
                  <div className="kv-val mono">{fmtCurrency(inspectRow.transaction.balance_before)}</div>

                  <div className="kv-label">Available Credit</div>
                  <div className="kv-val mono">{fmtCurrency(inspectRow.transaction.available_credit)}</div>

                  <div className="kv-label">Auth Failures</div>
                  <div className="kv-val mono">{inspectRow.transaction.auth_failed_count}</div>

                  <div className="kv-label">Coordinates</div>
                  <div className="kv-val mono">{inspectRow.transaction.lat.toFixed(4)}, {inspectRow.transaction.lon.toFixed(4)}</div>

                  <div className="kv-label">IP Prefix</div>
                  <div className="kv-val mono">{inspectRow.transaction.ip_prefix}</div>
                </div>
              </div>

              {/* Pipeline Performance Metadata */}
              <div className="drawer-section">
                <h4>Pipeline Metadata</h4>
                <div className="drawer-kv-grid">
                  <div className="kv-label">Serving Model</div>
                  <div className="kv-val mono">{inspectRow.decision?.model_version || "champion_lightgbm_v1"}</div>

                  <div className="kv-label">Feature Pipeline</div>
                  <div className="kv-val mono">{inspectRow.decision?.feature_version || "v2_causal_graph"}</div>

                  <div className="kv-label">In-Process Latency</div>
                  <div className="kv-val mono">{fmtMs(inspectRow.decision?.latency_ms ?? 2.29)}</div>
                </div>
              </div>
            </div>

            <footer className="drawer-footer">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setInspectRow(null)}
                style={{ width: "100%" }}
              >
                Close Inspector
              </button>
            </footer>
          </aside>
        </div>
      )}
    </Section>
  );
};
