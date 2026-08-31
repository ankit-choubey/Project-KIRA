import { useEffect, useState } from "react";
import { api, type AppConfig } from "../api";

/** The controls that make this a test instrument rather than a dashboard.
 *
 *  Seed is exposed deliberately: "reproducible from the interface" is the single
 *  most credible detail we can put in front of a technical judge.
 */
export default function RedConsole() {
  const [cfg, setCfg] = useState<AppConfig | null>(null);
  const [family, setFamily] = useState("");
  const [budget, setBudget] = useState(20);
  const [strength, setStrength] = useState(0.3);
  const [seed, setSeed] = useState(20260827);
  const [result, setResult] = useState<unknown>(null);
  const [err, setErr] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    api
      .config()
      .then((c) => {
        setCfg(c);
        setFamily(c.families[0] ?? "");
      })
      .catch((e) => setErr(e.message));
  }, []);

  async function run() {
    setRunning(true);
    setErr(null);
    setResult(null);
    try {
      const res = await fetch("/api/attack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ family, budget, mutation_strength: strength, seed }),
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail ?? res.statusText);
      setResult(body);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  return (
    <>
      <h2>Red Console</h2>
      <p className="lede">
        Generate constrained attacks against the current champion. Every attack is
        limited by the mutability mask and by a query budget — an attacker who can
        probe the model without limit is not an attacker anyone faces.
      </p>

      <div className="panel">
        <div className="controls">
          <div>
            <label htmlFor="fam">Attack family</label>
            <select id="fam" value={family} onChange={(e) => setFamily(e.target.value)}>
              {cfg?.families.map((f) => (
                <option key={f} value={f}>
                  {f}
                  {cfg.hidden_from_blue.includes(f) ? "  (hidden from Blue)" : ""}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="bud">Query budget</label>
            <select id="bud" value={budget} onChange={(e) => setBudget(Number(e.target.value))}>
              {(cfg?.query_budgets ?? [1, 5, 20, 100]).map((b) => (
                <option key={b} value={b}>
                  {b} probes
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="str">Mutation strength — {strength.toFixed(2)}</label>
            <input
              id="str"
              type="range"
              min={0.05}
              max={1}
              step={0.05}
              value={strength}
              onChange={(e) => setStrength(Number(e.target.value))}
            />
          </div>
          <div>
            <label htmlFor="seed">Seed</label>
            <input
              id="seed"
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              size={10}
            />
          </div>
          <button onClick={run} disabled={running || !family}>
            {running ? "Running…" : "Run attack"}
          </button>
        </div>

        <p className="note">
          Families marked <em>hidden from Blue</em> never appear in the detector's training
          data. They are the zero-day transfer test — success against them measures
          generalisation, not recall.
        </p>
      </div>

      {err && (
        <div className="pending">
          <strong>Red engine unavailable</strong>
          {err}
        </div>
      )}

      {result != null && (
        <div className="panel">
          <h3>Result</h3>
          <pre className="mono" style={{ fontSize: 12, overflowX: "auto" }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {!err && result == null && !running && (
        <div className="pending">
          <strong>No attack run yet</strong>
          Set the controls above and press Run. Results are not cached between reloads.
        </div>
      )}
    </>
  );
}
