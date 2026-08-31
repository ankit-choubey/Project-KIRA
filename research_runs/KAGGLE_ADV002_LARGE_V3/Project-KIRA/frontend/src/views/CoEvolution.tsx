import { useEffect, useState } from "react";
import { api, fmt, type RoundResult } from "../api";

/** The central result: does hardening actually generalise?
 *
 *  Seen-variant and held-out-variant success rates are shown as separate columns
 *  on purpose. Collapsing them is how a project reports memorisation as hardening.
 */
export default function CoEvolution() {
  const [rounds, setRounds] = useState<RoundResult[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    api
      .coevolution()
      .then((r) => {
        setRounds(r.rounds);
        setIdx(Math.max(0, r.rounds.length - 1));
      })
      .catch((e) => setErr(e.message));
  }, []);

  if (err) return <div className="pending">Could not load rounds: {err}</div>;
  if (!rounds) return <div className="pending">Loading…</div>;
  if (!rounds.length)
    return (
      <div className="pending">
        <strong>No rounds yet</strong>
        The closed loop arrives with BLOCK 5.
      </div>
    );

  const r = rounds[idx];
  const first = rounds[0];

  return (
    <>
      <h2>Co-Evolution</h2>
      <p className="lede">
        Each round: Red attacks the champion, successful evasions are analysed and
        replayed, a challenger is trained, and the promotion gate decides. Drag the
        scrubber to move through rounds.
      </p>

      <div className="panel">
        <div className="controls">
          <div style={{ flex: 1, minWidth: 220 }}>
            <label htmlFor="round">
              Round {r.round_index} of {rounds.length - 1}
            </label>
            <input
              id="round"
              type="range"
              min={0}
              max={rounds.length - 1}
              value={idx}
              onChange={(e) => setIdx(Number(e.target.value))}
              style={{ width: "100%" }}
            />
          </div>
          <div className="stat">
            <span>champion</span>
            <b className="mono" style={{ fontSize: 14 }}>
              {r.champion_version}
            </b>
          </div>
          <div className="stat">
            <span>promoted</span>
            <b>
              <span className={`pill ${r.promoted ? "ok" : "warn"}`}>
                {r.promoted ? "yes" : "no"}
              </span>
            </b>
          </div>
        </div>

        <div className="grid">
          <div className="stat">
            <span>ASR — held-out variants</span>
            <b>{fmt(r.red.asr_heldout_variants)}</b>
          </div>
          <div className="stat">
            <span>ASR — seen variants</span>
            <b>{fmt(r.red.asr_seen_variants)}</b>
          </div>
          <div className="stat">
            <span>ASR — unseen family</span>
            <b>{fmt(r.red.asr_unseen_family)}</b>
          </div>
          <div className="stat">
            <span>min evasion distance</span>
            <b>{fmt(r.red.mean_evasion_distance, 1)}</b>
          </div>
          <div className="stat">
            <span>PR-AUC (no regression)</span>
            <b>{fmt(r.blue.pr_auc)}</b>
          </div>
          <div className="stat">
            <span>FPR</span>
            <b>{fmt(r.blue.fpr, 4)}</b>
          </div>
        </div>

        {r.promotion_reasons.length > 0 && (
          <p className="note">
            Promotion gate: {r.promotion_reasons.map((x) => x.replace(/_/g, " ")).join(" · ")}
          </p>
        )}
      </div>

      <div className="panel">
        <h3>All rounds</h3>
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>Round</th>
                <th className="num">ASR held-out</th>
                <th className="num">ASR seen</th>
                <th className="num">ASR unseen family</th>
                <th className="num">Min evasion dist.</th>
                <th className="num">PR-AUC</th>
                <th className="num">FPR</th>
                <th className="num">ECE</th>
                <th>Promoted</th>
              </tr>
            </thead>
            <tbody>
              {rounds.map((x, i) => (
                <tr
                  key={x.round_index}
                  onClick={() => setIdx(i)}
                  style={{ cursor: "pointer", background: i === idx ? "var(--panel-2)" : undefined }}
                >
                  <td className="mono">{x.round_index}</td>
                  <td className="num">{fmt(x.red.asr_heldout_variants)}</td>
                  <td className="num">{fmt(x.red.asr_seen_variants)}</td>
                  <td className="num">{fmt(x.red.asr_unseen_family)}</td>
                  <td className="num">{fmt(x.red.mean_evasion_distance, 1)}</td>
                  <td className="num">{fmt(x.blue.pr_auc)}</td>
                  <td className="num">{fmt(x.blue.fpr, 4)}</td>
                  <td className="num">{fmt(x.blue.ece, 4)}</td>
                  <td>{x.promoted ? <span className="pill ok">yes</span> : <span className="pill">no</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">
          <strong>Held-out variants is the honest headline.</strong> Blue hardens on the
          first few variants of each family; success against the remaining variants
          measures generalisation. Seen-variant success measures memorisation and is shown
          only for comparison.
          {first.red.mean_evasion_distance !== null && r.red.mean_evasion_distance !== null && (
            <>
              {" "}Evasion distance moved from {fmt(first.red.mean_evasion_distance, 1)} to{" "}
              {fmt(r.red.mean_evasion_distance, 1)} — an attacker has to change more to get
              through.
            </>
          )}
        </p>
      </div>
    </>
  );
}
