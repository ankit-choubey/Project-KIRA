import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, type StreamPage } from "../api";

/** Replayed transaction stream with a speed control.
 *
 *  The stream is replayed from an artifact, never computed live. That is what
 *  makes the demo unable to fail the way live scoring fails.
 */
export default function Monitor() {
  const [page, setPage] = useState<StreamPage | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [cursor, setCursor] = useState(0);
  const [speed, setSpeed] = useState(8); // rows revealed per second
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    api.stream(0, 400).then(setPage).catch((e) => setErr(e.message));
  }, []);

  useEffect(() => {
    if (!playing || !page) return;
    const id = setInterval(() => {
      setCursor((c) => Math.min(c + 1, page.rows.length));
    }, 1000 / speed);
    return () => clearInterval(id);
  }, [playing, speed, page]);

  const shown = useMemo(() => (page ? page.rows.slice(0, cursor) : []), [page, cursor]);

  const tally = useMemo(() => {
    const t = { ALLOW: 0, STEP_UP: 0, BLOCK: 0, fraudSeen: 0, fraudBlocked: 0, fpBlocked: 0 };
    for (const r of shown) {
      const d = r.decision?.decision;
      if (d) t[d] += 1;
      if (r.transaction.is_fraud) {
        t.fraudSeen += 1;
        if (d === "BLOCK") t.fraudBlocked += 1;
      } else if (d === "BLOCK") {
        t.fpBlocked += 1;
      }
    }
    return t;
  }, [shown]);

  if (err) return <div className="pending">Could not load the stream: {err}</div>;
  if (!page) return <div className="pending">Loading stream…</div>;

  const recall = tally.fraudSeen ? tally.fraudBlocked / tally.fraudSeen : null;
  const legit = shown.length - tally.fraudSeen;
  const fpr = legit ? tally.fpBlocked / legit : null;

  return (
    <>
      <h2>Live Monitor</h2>
      <p className="lede">
        Transactions replayed from run <code>{page.run_id}</code>. Recall and false-positive
        rate are computed over what has been revealed so far, so they move as the
        stream plays.
      </p>

      <div className="controls">
        <button onClick={() => setPlaying((p) => !p)}>{playing ? "Pause" : "Play"}</button>
        <button
          onClick={() => {
            setCursor(0);
            setPlaying(true);
          }}
        >
          Restart
        </button>
        <div>
          <label htmlFor="speed">Speed — {speed}/s</label>
          <input
            id="speed"
            type="range"
            min={1}
            max={60}
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
          />
        </div>
        <div className="stat">
          <span>revealed</span>
          <b>
            {shown.length}
            <span style={{ opacity: 0.5 }}> / {page.rows.length}</span>
          </b>
        </div>
      </div>

      <div className="grid" style={{ marginBottom: 16 }}>
        {[
          ["allow", tally.ALLOW],
          ["step up", tally.STEP_UP],
          ["block", tally.BLOCK],
        ].map(([k, v]) => (
          <div className="panel stat" key={k as string}>
            <span>{k as string}</span>
            <b>{v as number}</b>
          </div>
        ))}
        <div className="panel stat">
          <span>recall (blocked fraud)</span>
          <b>{recall === null ? <em className="unmeasured">no fraud yet</em> : recall.toFixed(2)}</b>
        </div>
        <div className="panel stat">
          <span>false-positive rate</span>
          <b>{fpr === null ? <em className="unmeasured">—</em> : fpr.toFixed(4)}</b>
        </div>
      </div>

      <div className="panel">
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Txn</th>
                <th>Time</th>
                <th>Customer</th>
                <th className="num">Amount</th>
                <th>Channel</th>
                <th className="num">Risk</th>
                <th>Decision</th>
                <th>Truth</th>
                <th className="num">Latency</th>
              </tr>
            </thead>
            <tbody>
              {shown
                .slice(-40)
                .reverse()
                .map(({ transaction: t, decision: d }) => (
                  <tr key={t.txn_id}>
                    <td>
                      <Link to={`/inspect/${t.txn_id}`}>
                        <code>{t.txn_id}</code>
                      </Link>
                    </td>
                    <td className="mono">{t.timestamp.slice(5, 16).replace("T", " ")}</td>
                    <td className="mono">{t.customer_id}</td>
                    <td className="num">{t.amount.toFixed(2)}</td>
                    <td>{t.channel}</td>
                    <td className="num">{d ? d.risk_score.toFixed(3) : "—"}</td>
                    <td>
                      {d ? <span className={`dec ${d.decision}`}>{d.decision}</span> : "—"}
                    </td>
                    <td>
                      {t.is_fraud ? (
                        <span className="pill bad">{t.attack_family ?? "fraud"}</span>
                      ) : t.hard_negative !== "none" ? (
                        <span className="pill warn">{t.hard_negative}</span>
                      ) : (
                        <span style={{ color: "var(--muted)" }}>legit</span>
                      )}
                    </td>
                    <td className="num">{d ? `${d.latency_ms.toFixed(2)} ms` : "—"}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <p className="note">
          The <strong>Truth</strong> column is hidden evaluation metadata — it is shown here
          for the demo and is never available to the model as a feature. Amber rows are
          hard negatives: legitimate behaviour that looks fraudulent.
        </p>
      </div>
    </>
  );
}
