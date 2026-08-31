import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type InspectResult } from "../api";

/** One transaction, end to end. This view does the work of three: it carries the
 *  score, the explanation, the intent breakdown, and the counterfactual — which
 *  is the line people actually remember. */
export default function Inspector() {
  const { txnId } = useParams();
  const navigate = useNavigate();
  const [query, setQuery] = useState(txnId ?? "");
  const [data, setData] = useState<InspectResult | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!txnId) {
      // Land on something real rather than an empty form.
      api
        .stream(0, 1)
        .then((p) => p.rows[0] && navigate(`/inspect/${p.rows[0].transaction.txn_id}`, { replace: true }))
        .catch((e) => setErr(e.message));
      return;
    }
    setQuery(txnId);
    setLoading(true);
    setErr(null);
    api
      .transaction(txnId)
      .then(setData)
      .catch((e) => {
        setData(null);
        setErr(e.message);
      })
      .finally(() => setLoading(false));
  }, [txnId, navigate]);

  return (
    <>
      <h2>Transaction Inspector</h2>
      <p className="lede">
        Features, score, explanation, intent drift, and the minimum change that would
        flip the decision.
      </p>

      <form
        className="controls"
        onSubmit={(e) => {
          e.preventDefault();
          if (query.trim()) navigate(`/inspect/${query.trim()}`);
        }}
      >
        <div>
          <label htmlFor="txn">Transaction id</label>
          <input id="txn" value={query} onChange={(e) => setQuery(e.target.value)} size={16} />
        </div>
        <button type="submit">Inspect</button>
      </form>

      {loading && <div className="pending">Loading…</div>}
      {err && <div className="pending">{err}</div>}

      {data && (
        <>
          <div className="grid">
            <div className="panel">
              <h3>Transaction</h3>
              <div className="tw">
                <table>
                  <tbody>
                    {(
                      [
                        ["amount", data.transaction.amount.toFixed(2)],
                        ["timestamp", data.transaction.timestamp.replace("T", " ").slice(0, 19)],
                        ["customer", data.transaction.customer_id],
                        ["merchant", data.transaction.merchant_id],
                        ["mcc", data.transaction.mcc],
                        ["channel", data.transaction.channel],
                        ["device", data.transaction.device_id],
                        ["new device", String(data.transaction.is_new_device)],
                        ["auth failures", String(data.transaction.auth_failed_count)],
                        ["balance before", data.transaction.balance_before.toFixed(2)],
                      ] as const
                    ).map(([k, v]) => (
                      <tr key={k}>
                        <td style={{ color: "var(--muted)" }}>{k}</td>
                        <td className="mono">{v}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="panel">
              <h3>Decision</h3>
              {data.decision ? (
                <>
                  <div className="grid">
                    <div className="stat">
                      <span>risk</span>
                      <b>{data.decision.risk_score.toFixed(3)}</b>
                    </div>
                    <div className="stat">
                      <span>calibrated</span>
                      <b>{data.decision.calibrated_score.toFixed(3)}</b>
                    </div>
                    <div className="stat">
                      <span>outcome</span>
                      <b>
                        <span className={`dec ${data.decision.decision}`}>
                          {data.decision.decision}
                        </span>
                      </b>
                    </div>
                    <div className="stat">
                      <span>latency</span>
                      <b>{data.decision.latency_ms.toFixed(2)} ms</b>
                    </div>
                  </div>
                  <h3 style={{ marginTop: 16 }}>Reason codes</h3>
                  {data.decision.reason_codes.length ? (
                    <ul className="note">
                      {data.decision.reason_codes.map((r) => (
                        <li key={r}>
                          <code>{r}</code>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="unmeasured">none recorded</p>
                  )}
                </>
              ) : (
                <p className="unmeasured">no decision recorded for this transaction</p>
              )}
            </div>
          </div>

          <div className="grid">
            <div className="panel">
              <h3>Feature attribution (SHAP)</h3>
              {data.shap ? (
                <div className="tw">
                  <table>
                    <tbody>
                      {Object.entries(data.shap)
                        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                        .slice(0, 10)
                        .map(([k, v]) => (
                          <tr key={k}>
                            <td>{k}</td>
                            <td className="num mono">{v.toFixed(4)}</td>
                            <td style={{ width: "40%" }}>
                              <div className="bar">
                                <i style={{ width: `${Math.min(100, Math.abs(v) * 100)}%` }} />
                              </div>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="unmeasured">not measured — arrives with BLOCK 3</p>
              )}
            </div>

            <div className="panel">
              <h3>Intent drift</h3>
              {data.intent_breakdown ? (
                <div className="tw">
                  <table>
                    <tbody>
                      {Object.entries(data.intent_breakdown).map(([k, v]) => (
                        <tr key={k}>
                          <td>{k.replace(/_/g, " ")}</td>
                          <td className="num mono">{v.toFixed(3)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="unmeasured">
                  not measured — arrives with BLOCK 5. Only applies to agent-initiated
                  transactions carrying a mandate.
                </p>
              )}
            </div>
          </div>

          <div className="panel">
            <h3>Counterfactual — minimum evasion distance</h3>
            {data.counterfactual?.found ? (
              <>
                <p style={{ fontSize: 16, margin: "6px 0 12px" }}>
                  {data.counterfactual.human_readable}
                </p>
                <div className="grid">
                  <div className="stat">
                    <span>field</span>
                    <b className="mono" style={{ fontSize: 15 }}>
                      {data.counterfactual.changed_field}
                    </b>
                  </div>
                  <div className="stat">
                    <span>original</span>
                    <b>{data.counterfactual.original_value?.toFixed(2)}</b>
                  </div>
                  <div className="stat">
                    <span>evading</span>
                    <b>{data.counterfactual.evading_value?.toFixed(2)}</b>
                  </div>
                  <div className="stat">
                    <span>distance</span>
                    <b>{data.counterfactual.distance?.toFixed(2)}</b>
                  </div>
                </div>
                <p className="note">
                  This is the headline security metric. Unlike attack success rate it does
                  not move when the decision threshold moves, and it should grow after each
                  hardening round.
                </p>
              </>
            ) : (
              <p className="unmeasured">
                not measured for this transaction — arrives with BLOCK 4
              </p>
            )}
          </div>
        </>
      )}
    </>
  );
}
