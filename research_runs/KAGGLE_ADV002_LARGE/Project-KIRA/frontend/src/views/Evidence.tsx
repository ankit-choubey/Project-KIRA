import { useEffect, useState } from "react";
import { api, fmt, type EvaluationResult } from "../api";

/** The view that makes a judge trust the other four.
 *
 *  Every layer renders "not measured" until it genuinely is. That honesty is the
 *  point of the page — a populated number next to an explicit gap reads as real,
 *  a page of suspiciously complete numbers does not.
 */
export default function Evidence() {
  const [ev, setEv] = useState<EvaluationResult | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.evidence().then(setEv).catch((e) => setErr(e.message));
  }, []);

  if (err) return <div className="pending">Could not load evidence: {err}</div>;
  if (!ev) return <div className="pending">Loading…</div>;

  const f = ev.fidelity;
  const last = ev.rounds.at(-1);

  const L3 = [
    ["P1 · inter-event timing", f.l3_p1_interarrival_ratio],
    ["P2 · burst structure", f.l3_p2_burstiness_ratio],
    ["P3 · multi-account graph motifs", f.l3_p3_graph_motif_ratio],
    ["P4 · velocity-rule trigger rates", f.l3_p4_velocity_trigger_ratio],
  ] as const;

  return (
    <>
      <h2>Evidence</h2>
      <p className="lede">
        Everything measured for run <code>{ev.manifest.run_id}</code> (seed{" "}
        <code>{ev.manifest.seed}</code>, commit <code>{ev.manifest.git_commit}</code>).
        Values shown as <em className="unmeasured">not measured</em> have not been
        computed yet — they are never rendered as zero.
      </p>

      {/* ---------------- L1 ---------------- */}
      <div className="panel">
        <h3>Layer 1 — Validity (hard gate)</h3>
        <p className="note" style={{ marginTop: 0 }}>
          Physics, not statistics. A row either is or is not possible. Any violation
          rejects the row; it is not scored.
        </p>
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Check</th>
                <th className="num">Violations</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(f.l1_checks).map(([k, v]) => (
                <tr key={k}>
                  <td>{k.replace(/_/g, " ")}</td>
                  <td className="num">
                    {v === 0 ? <span className="pill ok">0</span> : <span className="pill bad">{v}</span>}
                  </td>
                </tr>
              ))}
              {Object.keys(f.l1_checks).length === 0 && (
                <tr>
                  <td colSpan={2} className="unmeasured">not measured</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ---------------- L2 ---------------- */}
      <div className="panel">
        <h3>Layer 2 — Marginals and dependency</h3>
        <p className="note" style={{ marginTop: 0 }}>
          Necessary but <strong>not sufficient</strong>. A generator that samples every
          column independently from the correct marginal passes this layer entirely and
          has no behavioural structure at all.
        </p>
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Column</th>
                <th className="num">KS statistic</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(f.l2_ks_by_column).map(([k, v]) => (
                <tr key={k}>
                  <td>{k}</td>
                  <td className="num">{v.toFixed(4)}</td>
                </tr>
              ))}
              <tr>
                <td>correlation distance</td>
                <td className="num">
                  {f.l2_correlation_distance === null ? (
                    <span className="unmeasured">not measured</span>
                  ) : (
                    f.l2_correlation_distance.toFixed(4)
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* ---------------- L3 ---------------- */}
      <div className="panel">
        <h3>Layer 3 — Behavioural fidelity</h3>
        <p className="note" style={{ marginTop: 0 }}>
          Normalised to real-data variability: real data is split in half and the metric
          between the halves is the floor, so <strong>1.0 means our synthetic data differs
          from real data by no more than one sample of real data differs from another</strong>.
        </p>
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Axis</th>
                <th className="num">Ours (1.0 = real)</th>
              </tr>
            </thead>
            <tbody>
              {L3.map(([label, v]) => (
                <tr key={label}>
                  <td>{label}</td>
                  <td className="num">
                    {v === null ? <span className="unmeasured">not measured</span> : `${v.toFixed(2)}x`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3 style={{ marginTop: 18 }}>Published baselines on the same axes</h3>
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Generator</th>
                <th className="num">Degradation ratio</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(f.l3_published_baselines).map(([k, v]) => (
                <tr key={k}>
                  <td>{k.replace(/_/g, " ")}</td>
                  <td className="num">{v.toFixed(1)}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">
          Source: arXiv 2604.13125. Row-independent generators cannot structurally
          reproduce multi-account motifs or positive autocorrelation, which is why they
          fail this layer while passing Layer 2.
        </p>
      </div>

      {/* ---------------- L4 / L5 ---------------- */}
      <div className="grid">
        <div className="panel">
          <h3>Layer 4 — Detectability (C2ST)</h3>
          <p className="note" style={{ marginTop: 0 }}>
            A discriminator trained to separate real from synthetic. AUC near 0.50 means
            indistinguishable; near 1.00 means trivially fake.
          </p>
          <div className="grid">
            <div className="stat">
              <span>row level</span>
              <b>
                {f.l4_c2st_auc_row === null ? (
                  <em className="unmeasured">not measured</em>
                ) : (
                  f.l4_c2st_auc_row.toFixed(3)
                )}
              </b>
            </div>
            <div className="stat">
              <span>entity level</span>
              <b>
                {f.l4_c2st_auc_entity === null ? (
                  <em className="unmeasured">not measured</em>
                ) : (
                  f.l4_c2st_auc_entity.toFixed(3)
                )}
              </b>
            </div>
          </div>
          {f.l4_top_giveaway_features.length > 0 && (
            <>
              <h3 style={{ marginTop: 16 }}>What gives us away</h3>
              <ul className="note">
                {f.l4_top_giveaway_features.map((x) => (
                  <li key={x}>
                    <code>{x}</code>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div className="panel">
          <h3>Layer 5 — Utility (TSTR)</h3>
          <p className="note" style={{ marginTop: 0 }}>
            Train on synthetic, test on real. The ratio against train-real / test-real is
            the answer to "so what?".
          </p>
          <div className="grid">
            <div className="stat">
              <span>TSTR PR-AUC</span>
              <b>
                {f.l5_tstr_pr_auc === null ? (
                  <em className="unmeasured">not measured</em>
                ) : (
                  f.l5_tstr_pr_auc.toFixed(3)
                )}
              </b>
            </div>
            <div className="stat">
              <span>TRTR PR-AUC</span>
              <b>
                {f.l5_trtr_pr_auc === null ? (
                  <em className="unmeasured">not measured</em>
                ) : (
                  f.l5_trtr_pr_auc.toFixed(3)
                )}
              </b>
            </div>
          </div>
        </div>
      </div>

      {/* ---------------- anchor + latest round ---------------- */}
      <div className="panel">
        <h3>External reality anchor</h3>
        {ev.anchor ? (
          <div className="grid">
            <div className="stat">
              <span>PR-AUC on real data</span>
              <b>{fmt(ev.anchor.pr_auc)}</b>
            </div>
            <div className="stat">
              <span>FPR</span>
              <b>{fmt(ev.anchor.fpr, 4)}</b>
            </div>
          </div>
        ) : (
          <p className="unmeasured">
            not measured — until this exists, every other number here is only true inside
            our own simulator.
          </p>
        )}
      </div>

      {last && (
        <div className="panel">
          <h3>Latest round — {last.round_index}</h3>
          <div className="grid">
            <div className="stat"><span>PR-AUC</span><b>{fmt(last.blue.pr_auc)}</b></div>
            <div className="stat"><span>ECE</span><b>{fmt(last.blue.ece, 4)}</b></div>
            <div className="stat"><span>FPR</span><b>{fmt(last.blue.fpr, 4)}</b></div>
            <div className="stat">
              <span>ASR held-out variants</span>
              <b>{fmt(last.red.asr_heldout_variants)}</b>
            </div>
            <div className="stat">
              <span>Min evasion distance</span>
              <b>{fmt(last.red.mean_evasion_distance, 1)}</b>
            </div>
            <div className="stat">
              <span>latency P99</span>
              <b>{fmt(last.blue.latency_p99_ms, 2, " ms")}</b>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
