# Project KIRA — Video Presentation & Demo Recording Master Plan

Here is a complete, step-by-step video storyboard, screen-recording guide, and voiceover script designed to make Project KIRA look institutional, scientifically rigorous, and clearly superior to typical hackathon projects.

---

## 🎯 Video Strategy & Target Specs

- **Recommended Length:** 3 to 4.5 minutes
- **Core Message:** *"Traditional fraud systems train static models on stationary datasets and pretend they are 99% accurate. KIRA is a closed-loop adversarial payment-security laboratory that tests whether defenses generalize or memorize when attacked by stateful, memory-enabled adversarial swarms."*
- **Tone:** Technical, confident, evidence-backed (like an institutional research demonstration by DeepMind / Mastercard Cyber & Intelligence).

---

## 🎬 Act-by-Act Storyboard & Screen Recording Plan

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 0:00 - 0:40 │ THE HOOK: Static Fraud Models Fail in the Real World                      │
│ 0:40 - 1:20 │ ACT 1: Stateful Payment Universe & Zero-Leakage Causal Feature Engine    │
│ 1:20 - 2:20 │ ACT 2: The Red Adversarial Swarm (10K Attacks & 15K Stateful Trials)     │
│ 2:20 - 3:20 │ ACT 3: Closed-Loop Challenger Defense & Anti-Forgetting Governance       │
│ 3:20 - 4:00 │ ACT 4: Empirical Evidence, Real-World ULB Anchor & 225 Automated Tests   │
│ 4:00 - 4:20 │ CONCLUSION: The Scientific Takeaway & Ready for Submission               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Act 0: The Hook (0:00 – 0:40)
**What to show on screen:**
1. Show the **KIRA Live Architecture Diagram** or the live Web Dashboard ([https://ankit-choubey-project-kira.hf.space](https://ankit-choubey-project-kira.hf.space)).
2. Briefly show a split slide comparing **Traditional Fraud AI** vs. **Project KIRA**.

**Voiceover Script:**
> *"Most fraud detection projects train a static gradient-boosted tree or neural network on an offline CSV, report a 99% accuracy score, and claim production readiness. In the real world, fraud is an active, adversarial game. Attackers probe decision boundaries, learn through shared memory, and coordinate across merchant rails.*
> 
> *Welcome to **Project KIRA — the Mastercard AI Defense Lab**. KIRA is a closed-loop adversarial payment security laboratory built to answer one fundamental question: **When defenses are hardened against known attacks, do they genuinely generalize, or do they simply memorize perturbations while remaining vulnerable to novel zero-day threats?**"*

---

### Act 1: The Synthetic World & Causal Streaming (0:40 – 1:20)
**What to show on screen:**
1. Navigate to the **Transaction Stream & Inspector** view in the live UI.
2. Scroll through the live transaction feed ($N=9,348$ transactions).
3. Click on a specific transaction (e.g. `tx_00000000`) to show the **Counterfactual Explanation** and latency breakdown.

**Voiceover Script:**
> *"KIRA starts with a stateful synthetic payment world generating authentic consumer-merchant graph topologies with realistic class imbalance, velocity bursts, and a 7-day chargeback label delay.*
> 
> *Crucially, our feature engine enforces strict temporal causality. Every feature reads state strictly at time $t \le t_0$. We verified zero future leakage ($\Delta = 0.0000$) even under malicious post-transaction database mutations. On our streaming endpoint, decisions are resolved with sub-3-millisecond in-process latency alongside deterministic counterfactual perturbations."*

---

### Act 2: The Red Adversarial Swarm (1:20 – 2:20)
**What to show on screen:**
1. Navigate to the **Red Console / Adversarial Evaluation** view.
2. Show the **10,000 Attack Surface (ADV-001)** and the **15,000 Swarm Experiment (ADV-002)**.
3. Highlight the 3 controlled arms: **Adaptive Memory (19.68%) vs. Static Control (9.60%)**.

**Voiceover Script:**
> *"Unlike standard benchmark evaluations that test isolated perturbations, KIRA deploys a budget-constrained Red Engine executing 5 distinct attack families: burst drains, slow siphons, geo-hops, agent credential subversions, and cross-merchant fanouts under strict physical action masks.*
> 
> *In our 15,000-attempt cloud swarm experiment across 100 rounds, we compared three controlled arms. When attacker agents shared an associative episodic attack memory, their evasion rate surged from 9.60% to 19.68% — an empirical **+10.08 percentage-point attacker adaptation effect**. This proves that multi-agent attackers rapidly coordinate to bypass static detection surfaces."*

---

### Act 3: Closed-Loop Challenger Defense & Governance Gate (2:20 – 3:20)
**What to show on screen:**
1. Navigate to the **Co-Evolution / Adaptive Defense** page.
2. Show the **Challenger Model Progression** across rounds.
3. Highlight the **Anti-Forgetting Status (`NO_FORGETTING`)** and the **Promotion Gate Decisions** (showing 4/4 overfitted challengers rejected).

**Voiceover Script:**
> *"When attacks succeed, KIRA doesn't blindly retrain production models in an unmonitored loop. Weakness profiles are synthesized into defensive knowledge records and fed to a challenger model.*
> 
> *Every challenger must pass our automated Governance Gate: it must maintain legacy detection, prevent false-positive inflation, and prove generalizability on held-out variant lineages with a strict Anti-Forgetting invariant. In our evaluations, the gate correctly rejected overfitted models, preserving baseline integrity while catching 100% of adaptation variants."*

---

### Act 4: Honest Scientific Findings & Real-World Reality Anchor (3:20 – 4:00)
**What to show on screen:**
1. Open the **Evidence Page** ([/evidence](https://ankit-choubey-project-kira.hf.space/evidence)).
2. Show the **External Reality Anchor** (ULB European Credit Card Benchmark: PR-AUC = 0.8640, 284,807 transactions).
3. Point out the honest **Negative Findings**: World C Zero-Day (100% ASR on withheld families) and unmeasured metrics rendered as muted badges (never coerced to zero).
4. Briefly switch to the terminal and show `225 passed in pytest` and `22/22 Authoritative Artifact Integrity PASS`.

**Voiceover Script:**
> *"What sets KIRA apart is our strict adherence to scientific evidence over vanity metrics:*
> 
> *First, we anchored our synthetic world against **284,807 real-world European cardholder transactions**, demonstrating an external PR-AUC of 0.8640 with an FPR of 0.03%.*
> 
> *Second, we openly report critical limitations: in our World C zero-day evaluation, unadapted baseline models exhibited 100% vulnerability to novel topological and agent subversion attacks. We do not claim perfect defense; we experimentally expose where defenses break.*
> 
> *Finally, every number in this project is cryptographically bound to 22 SHA-256 baseline artifacts, backed by 225 passing unit and invariant tests, and fully reproducible."*

---

### Act 5: Conclusion & Live Handoff (4:00 – 4:20)
**What to show on screen:**
1. Show the **Live Public Hugging Face Space** and Swagger OpenAPI docs.
2. Display the concluding summary card with the top 5 numbers.

**Voiceover Script:**
> *"Project KIRA is fully deployed, reproducible on Kaggle and Hugging Face, and ready for institutional verification. Thank you."*

---

## 📊 The "Kill Sheet": Why KIRA Beats Competitors

Use this comparison table as a full-screen graphic or slide in your video:

| Feature / Dimension | Typical Competition Submissions | Project KIRA (Mastercard AI Defense Lab) |
| :--- | :--- | :--- |
| **Data Realism** | Static CSV with artificial rows | Stateful agent universe with velocity bursts & 7-day label lag |
| **Temporal Integrity** | Future leakage ignored; shuffle CV | Strictly causal streaming state ($\Delta = 0.0000$ verified) |
| **Adversarial Evaluation** | Random noise / unconstrained flips | 10k constrained attacks + 15k stateful swarm trials across 5 families |
| **Attacker Adaptation** | Static single-step attacks | Memory-enabled swarms proving +10.08 pp attacker adaptation |
| **Defensive Hardening** | Naive retraining (catastrophic forgetting) | Closed-loop challenger replay with automated Anti-Forgetting Gate |
| **Metric Honesty** | 99% accuracy claimed; nulls hidden | Negative findings preserved (100% Zero-Day ASR) & 22/22 SHA-256 audit |
| **Real-World Reality Anchor** | Synthetic only | Grounded on 284,807 real-world European cardholder transactions |
| **Engineering Rigor** | Notebook script only | 225 automated unit/invariant tests + live public FastAPI/React app |

---

## 🛠️ Practical Recording Tips

1. **Resolution:** Record in **1080p (1920x1080) at 60fps** (OBS Studio, QuickTime, or Loom).
2. **Browser Setup:** Use Dark Mode in Chrome on [https://ankit-choubey-mastercard-ai-defense-lab.static.hf.space](https://ankit-choubey-mastercard-ai-defense-lab.static.hf.space), zoom to 110% or 125% for high readability on laptop screens.
3. **Cursor Highlights:** Enable a subtle cursor click highlight so judges can follow your clicks on the Inspector, Red Console, and Evidence tabs.
4. **Audio:** Use a clean microphone with noise suppression. Speak at a deliberate, measured pace — this makes the technical depth feel authoritative.