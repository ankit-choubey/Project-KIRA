import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, type Health } from "./api";
import Monitor from "./views/Monitor";
import Inspector from "./views/Inspector";
import RedConsole from "./views/RedConsole";
import CoEvolution from "./views/CoEvolution";
import Evidence from "./views/Evidence";

const NAV = [
  { to: "/monitor", label: "Monitor" },
  { to: "/inspect", label: "Inspector" },
  { to: "/red", label: "Red Console" },
  { to: "/coevolution", label: "Co-Evolution" },
  { to: "/evidence", label: "Evidence" },
];

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api
      .health()
      .then(setHealth)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div className="app">
      <header className="mast">
        <div className="mast-title">
          <span className="shield" aria-hidden="true" />
          <div>
            <h1>AI Defense Lab</h1>
            <p className="sub">Adversarial payment security</p>
          </div>
        </div>

        <nav className="nav">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} className={({ isActive }) => (isActive ? "on" : "")}>
              {n.label}
            </NavLink>
          ))}
        </nav>

        {/* Provenance is always visible. Every number on screen belongs to this run. */}
        <div className="provenance">
          {err ? (
            <span className="pill bad">api unreachable</span>
          ) : health ? (
            <>
              <span className={`pill ${health.status === "ok" ? "ok" : "warn"}`}>
                {health.status}
              </span>
              <code>{health.run_id ?? "no run"}</code>
            </>
          ) : (
            <span className="pill">connecting…</span>
          )}
        </div>
      </header>

      {health?.is_fixture && (
        <div className="banner">
          <strong>FIXTURE DATA</strong> — these are placeholder values from{" "}
          <code>fixtures.py</code>, not measurements. They must never be cited in the
          report or a slide.
        </div>
      )}

      {err && (
        <div className="banner bad">
          <strong>API unreachable</strong> — {err}. Start it with <code>make api</code>.
        </div>
      )}

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/monitor" replace />} />
          <Route path="/monitor" element={<Monitor />} />
          <Route path="/inspect" element={<Inspector />} />
          <Route path="/inspect/:txnId" element={<Inspector />} />
          <Route path="/red" element={<RedConsole />} />
          <Route path="/coevolution" element={<CoEvolution />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="*" element={<div className="pad">Not found.</div>} />
        </Routes>
      </main>
    </div>
  );
}
