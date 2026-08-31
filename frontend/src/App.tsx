import { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { MissionControl } from "./sections/MissionControl";
import { ClosedLoopSimulation } from "./sections/ClosedLoopSimulation";
import { TheLoop } from "./sections/TheLoop";
import { GraphFusion } from "./sections/GraphFusion";
import { AttackConsole } from "./sections/AttackConsole";
import { WeaknessBoard } from "./sections/WeaknessBoard";
import { ThreeWorlds } from "./sections/ThreeWorlds";
import { RealWorldValidation } from "./sections/RealWorldValidation";
import { ExperimentRegister } from "./sections/ExperimentRegister";
import { TransactionMonitor } from "./sections/TransactionMonitor";
import { EvidenceProvenance } from "./sections/EvidenceProvenance";
import { source } from "./data/source";
import type { Health } from "./data/types";

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    return (localStorage.getItem("kira-theme") as "light" | "dark") || "light";
  });
  const [activeSection, setActiveSection] = useState<string>("mission");

  // Sync theme
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("kira-theme", theme);
  }, [theme]);

  // Load health
  useEffect(() => {
    source.health().then(setHealth).catch(() => {
      setHealth({
        status: "degraded",
        run_id: null,
        is_fixture: false,
        artifacts_loaded: false,
        detail: "API unreachable",
      });
    });
  }, []);

  // Track active section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const sections = [
        "mission",
        "simulation",
        "loop",
        "graph-fusion",
        "attack-console",
        "weakness",
        "three-worlds",
        "real-world",
        "experiments",
        "monitor",
        "evidence",
      ];
      const scrollPos = window.scrollY + 120;

      for (let i = sections.length - 1; i >= 0; i--) {
        const el = document.getElementById(sections[i]);
        if (el && el.offsetTop <= scrollPos) {
          setActiveSection(sections[i]);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <div className="app-container">
      <Header
        health={health}
        theme={theme}
        onToggleTheme={toggleTheme}
        activeSection={activeSection}
      />

      <main className="main-content">
        <MissionControl />
        <ClosedLoopSimulation />
        <TheLoop />
        <GraphFusion />
        <AttackConsole />
        <WeaknessBoard />
        <ThreeWorlds />
        <RealWorldValidation />
        <ExperimentRegister />
        <TransactionMonitor />
        <EvidenceProvenance />
      </main>

      <footer style={{ borderTop: "1px solid var(--border)", background: "var(--surface)", padding: "24px var(--space-4)" }}>
        <div style={{ maxWidth: "var(--content-max-width)", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", fontSize: "12.5px", color: "var(--muted)" }}>
          <div>
            <strong>Mastercard AI Defense Lab (Project KIRA)</strong> — Adversarial Payment Security Research
          </div>
          <div className="mono">
            Deterministic Evaluation · Seed 20260827 · Pure Tabular Causal Model
          </div>
        </div>
      </footer>
    </div>
  );
}
