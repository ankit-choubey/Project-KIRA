Yes. Before HF deployment, we should lock down the **entire runtime story**. Otherwise we risk deploying something that technically works but doesn't actually communicate what KIRA does.

The key is to separate **three things**:

1. **The research pipeline** — what produced the evidence.
2. **The deployed closed-loop simulation** — what the judge interacts with.
3. **The evidence layer** — what proves every displayed result.

And one important correction: **the frontend should not pretend to rerun the entire V7 research experiment live.** V7 is the measured research run. The frontend should provide a **deterministic interactive replay/simulation using the measured artifacts**, while clearly distinguishing live API/model decisions from artifact-backed measured results.

---

# 1. What KIRA actually is

The clean mental model is:

```text
                    KIRA
                     │
                     ▼
              PAYMENT EVENT
                     │
                     ▼
             FEATURE ENGINEERING
                     │
                     ▼
             BLUE DETECTOR
                     │
              ┌──────┴──────┐
              │             │
           ALLOW          BLOCK
              │
              ▼
       ATTACKER OBSERVES
              │
              ▼
       RED / ADVERSARY
              │
              ▼
       PROBE / PERTURB
              │
              ▼
       BLUE DETECTOR AGAIN
              │
        ┌─────┴─────┐
        │           │
     BLOCK        ALLOW
        │           │
        │           ▼
        │      ATTACK SUCCEEDS
        │
        ▼
   ADAPT / HARDEN
        │
        ▼
  NEW DEFENSIVE POLICY
        │
        └──────────────► next round
```

That is the **closed-loop story** the frontend needs to make understandable.

The research experiments then sit around this loop:

```text
                 ┌───────────────────────┐
                 │    CLOSED-LOOP KIRA    │
                 └───────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
      DETECTION          ATTACKING           HARDENING
          │                  │                  │
          ▼                  ▼                  ▼
       Blue              Red/ADV            Co-evolution
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                       EVALUATION
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
       S-02/G-03          S-03              Real-world
     graph fusion       zero-day              transfer
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                       EVIDENCE REGISTRY
                             │
                             ▼
                         FRONTEND
```

---

# 2. What the judge sees first

I would make the frontend a **single scrolling research instrument**, not a conventional dashboard.

The judge lands on:

## KIRA — Adversarial Fraud Detection

Something like:

```text
KIRA
Adversarial Fraud Detection & Adaptive Defense

MEASURED RESEARCH SYSTEM
V7 · 47,501 transactions · 3 model seeds

────────────────────────────────────────────

MISSION CONTROL

     TRANSACTIONS        ATTACKS        DEFENSE
       47,501             10,000          ACTIVE

              ┌───────────────┐
              │ BLUE DETECTOR │
              └───────┬───────┘
                      │
                  decision
                      │
              ┌───────▼───────┐
              │ RED ATTACKER  │
              └───────┬───────┘
                      │
                   probe
                      │
              ┌───────▼───────┐
              │ BLUE RESPONSE │
              └───────┬───────┘
                      │
                 harden / block
                      │
                      └──────►
```

Then immediately show the **measured headline evidence**, not marketing claims.

For example:

| Evidence                    |        Result |
| --------------------------- | ------------: |
| Synthetic → Real ROC-AUC    |    **0.7597** |
| Causal fusion PR-AUC        |    **0.9805** |
| Tabular reference PR-AUC    |    **0.9607** |
| Fusion uplift               |    **+1.98%** |
| Paired bootstrap            | **p = 0.046** |
| Graph topology contribution |    **+0.85%** |
| Temporal leakage violations |         **0** |
| Baseline held-out ASR       |    **14.55%** |
| Hardened held-out ASR       |     **0.00%** |
| ADV-001 attacks             |    **10,000** |
| ADV-001 success             |     **6.00%** |

Every one gets its provenance tag.

---

# 3. Then the frontend explains the closed loop

This is probably the most important interactive section.

## Section: "See KIRA Think"

The judge selects a transaction.

```text
TRANSACTION #KIRA-004281

Amount              ₹8,421
Merchant            M-0042
Customer            C-0193
Device               D-0831
Time                 14:37:21
Velocity             4 transactions / 90 sec
```

Then the UI animates:

### Step 1 — Feature extraction

```text
RAW TRANSACTION
       ↓
25 TABULAR FEATURES
       +
16-D GRAPH EMBEDDING
       ↓
41-D FUSED REPRESENTATION
```

Then:

### Step 2 — Blue

```text
BLUE DETECTOR

Risk score: 0.982

DECISION
████████████████ BLOCK
```

Then the adversary gets to act.

### Step 3 — Red

```text
RED OBSERVES RESPONSE

Probe budget: 20

Probe #01
Probe #02
Probe #03
...
Probe #20
```

The judge sees what the attacker is doing conceptually:

```text
Amount          −
Velocity        −
Merchant        unchanged
Device          unchanged
Temporal gap    +
```

Then each probe goes back through Blue.

```text
RED PROBE
   ↓
FEATURE UPDATE
   ↓
BLUE
   ↓
BLOCK / ALLOW
   ↓
RED LEARNS
```

That's the actual closed-loop concept.

---

# 4. But we must distinguish simulation from measured experiment

This is extremely important.

If the frontend says:

> "Watch KIRA train itself live"

but it is actually replaying precomputed JSON, a technical judge can expose that immediately.

Instead:

### The UI should say

**Interactive replay**

> Replaying an experimentally measured attack/defense trajectory from the authoritative evidence package.

Then:

**LIVE API**

> This request is being evaluated by the deployed KIRA API.

And:

**MEASURED**

> This value comes from the V7 research run.

Those are different things.

That distinction actually makes the project **more credible**, not less.

---

# 5. What HF actually does

Think of Hugging Face as the **public backend brain/interface**, not the place where the entire research notebook runs again.

Architecture:

```text
                  INTERNET
                     │
                     ▼
              FRONTEND WEBSITE
              Netlify / HF Pages
                     │
             HTTPS API requests
                     │
                     ▼
          ┌──────────────────────┐
          │ HUGGING FACE SPACE   │
          │      FastAPI         │
          └──────────┬───────────┘
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
       /health    /score     /evidence
          │          │           │
          │          │           ▼
          │          │       Evidence JSON
          │          │
          │          ▼
          │     authoritative
          │       artifact
          │
          ▼
        status
```

The frontend doesn't need to know where the files physically live.

It asks the API:

```text
GET /api/health
GET /api/evidence
GET /api/artifacts
GET /api/artifact/scoreboard
GET /api/artifact/experiment_register
GET /api/score
```

The API supplies the evidence.

---

# 6. What happens when someone clicks "Analyze"

For example:

```text
[ Analyze Transaction ]
```

Frontend sends:

```text
POST /api/score
```

The HF backend determines whether that transaction is:

### A. Known measured transaction

Return:

```text
decision: BLOCK
risk: ...
served_by:
artifact-backed (<run_id>)
```

That is an **empirical artifact-backed result**.

### B. Unknown transaction

It must **not fabricate a measured result**.

Your hardened API already addresses this:

```text
served_by:
artifact-fallback-unmeasured

reason:
UNMEASURED_TRANSACTION_FALLBACK
```

That is exactly the behaviour we want.

---

# 7. Evidence section

This should be one of the strongest sections.

Not:

> "Our model is 98% accurate."

Instead:

```text
EVIDENCE

CLAIM
Causal graph fusion improves PR-AUC.

RESULT
+1.98%

p = 0.046

PRIMARY SEED
20260827

DATASET
47,501 synthetic transactions

BASELINE
Arm A — LightGBM

CHALLENGER
Arm C — Causal Fusion
```

Then:

**[ Inspect provenance ]**

opens:

```text
SOURCE
S02/seed_20260827/arm_C/metrics.json

JSON PATH
metrics.pr_auc

RAW VALUE
0.9805

RUN
<V7 authoritative run>

WORLD SEED
20260827

MODEL SEED
20260827

GIT SHA
...

CLASSIFICATION
MEASURED
```

That is the difference between a **pretty dashboard** and a **research instrument**.

---

# 8. Graph fusion section

We should visually explain:

```text
TABULAR ONLY

25 features
      │
      ▼
LightGBM
      │
      ▼
PR-AUC 0.9607
```

versus:

```text
TABULAR                 GRAPH

25 features             customer
    │                   merchant
    │                   device
    │                   agent
    │                      │
    └────────┐       ┌─────┘
             ▼       ▼
          16-D GRAPH
          EMBEDDING
               │
               ▼
          41-D FUSION
               │
               ▼
            LightGBM
               │
               ▼
          PR-AUC 0.9805
```

Then:

```text
+1.98% vs tabular
p = 0.046
```

And separately:

```text
Shuffled topology control
PR-AUC = 0.9721

Causal topology contribution
+0.85%
```

But we must also show the **secondary seeds**, because otherwise a judge can ask why the result isn't universal.

```text
SEED STABILITY

20260827    +1.98%   p=.046
42          −0.24%   p=.485
12345       +3.68%   p=.055
```

Then explicitly:

> Primary-seed uplift is statistically significant; effect magnitude varies across model seeds.

That is much more defensible.

---

# 9. Co-evolution section

This should be visually dramatic but scientifically honest.

Show:

```text
ATTACK ROUND 01

RED
████████████████████  96.67% ASR

        ↓ HARDENING

BLUE
████████████████████  0.00% residual ASR
```

But label the two values correctly.

The **96.67%** is the **unhardened static attacker budget result**.

The **0.00%** is the hardened residual result.

Do **not** make it look like:

```text
96.67 → 0
```

without explaining the experimental conditions.

Instead:

```text
UNHARDENED BASELINE
20-probe attack budget
ASR = 96.67%

        ↓
     HARDENING

HELD-OUT EVALUATION
ASR = 0.00%
```

And then:

```text
GENERALISATION RETENTION
1.3071
```

if that remains part of the authoritative claim registry.

---

# 10. Adversarial attack console

This is where the 10,000 ADV-001 attacks become useful.

Show:

```text
ADV-001

10,000 ATTACK ATTEMPTS

SUCCESS
6.00%

FAILURE
94.00%

DOMINANT SUCCESS FAMILY
geo_hop

MEDIAN MINIMUM EVASION DISTANCE
1.2032
```

Then show the attack distribution.

The important point:

**Don't hide the 6%.**

A system claiming zero attacks ever succeed looks less credible.

The stronger story is:

> KIRA was attacked 10,000 times. 6% succeeded, concentrated in a specific attack family. The failure modes are measurable and therefore actionable.

That's research.

---

# 11. Real-world validation section

This needs to be clearly separated from synthetic experiments.

## Independent public benchmark

Sparkov:

```text
50,000 real transactions
199 frauds
0.398% prevalence
```

Then:

### C2ST

```text
Can a classifier distinguish
KIRA synthetic from Sparkov real?

AUC
0.7780

95% CI
[0.7641, 0.7918]
```

Interpretation:

> The distributions remain distinguishable.

Do **not** spin 0.778 as "nearly identical."

That would be scientifically weak.

Then TSTR:

```text
TRAIN
KIRA SYNTHETIC

        ↓

TEST
SPARKOV REAL

ROC-AUC
0.7597
```

And:

```text
REAL → REAL reference
ROC-AUC 0.9708
```

This tells the judge:

> Synthetic data transfers meaningful ranking signal to an independent real-world benchmark, but it does not reproduce the real distribution perfectly.

That's a much stronger scientific story.

---

# 12. Causal leakage section

This deserves a dedicated visual.

```text
TIME
──────────────────────────────────────►

TRAIN              VALID              TEST
───────             ─────              ─────
 t < 70%           70–85%             >85%

      │                 │                  │
      ▼                 ▼                  ▼
   graph              graph              graph
   edges              edges              edges
```

Then:

```text
FUTURE EDGE INVARIANCE
Δ = 0

FUTURE NODE FEATURE INVARIANCE
Δ = 0

VIOLATIONS
0 / 28,044 edges
```

This is one of your cleanest claims.

---

# 13. Zero-day section — be extremely careful

This is where the frontend must **not oversell**.

Current evidence says:

```text
HIDDEN FAMILIES

agent_subversion
cross_merchant_fanout

TRAIN CONTAMINATION
0

VALIDATION CONTAMINATION
0

TEST INSTANCES
0

STATUS
LOW SAMPLE

ROBUSTNESS DELTA
NOT MEASURED
```

The UI should actually make this visible.

For example:

> **Zero-day robustness: not measured in this run.**

Then:

> The hidden families were excluded from training and validation, but the generated test population contained zero qualifying instances. No robustness score is reported.

A judge will respect this much more than seeing an invented "100% robust."

---

# 14. What the complete frontend becomes

I'd structure the single page roughly like this:

```text
01  MISSION CONTROL
    ↓
02  CLOSED-LOOP SIMULATION
    ↓
03  CO-EVOLUTION
    ↓
04  GRAPH FUSION
    ↓
05  ADVERSARIAL EVALUATION
    ↓
06  REAL-WORLD VALIDATION
    ↓
07  CAUSALITY & LEAKAGE
    ↓
08  ZERO-DAY BOUNDARY
    ↓
09  EVIDENCE / PROVENANCE
    ↓
10  RESEARCH LIMITATIONS
```

Sticky navigation:

```text
MISSION
LOOP
DEFENSE
GRAPH
ATTACK
REAL-WORLD
CAUSALITY
LIMITS
EVIDENCE
```

---

# 15. The data flow behind that frontend

This is the crucial part.

There should be **one data source**, not numbers manually copied into React.

```text
                 V7 ARTIFACTS
                      │
                      ▼
             Evidence Adapter
                      │
                      ▼
              Metric Registry
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
       FRONTEND              HF API
           │                     │
           ▼                     ▼
       displayed              live/replay
        metrics                requests
```

For example:

```text
Metric:
  s02_arm_c_pr_auc

Source:
  S02/seed_20260827/arm_C/metrics.json

JSON path:
  metrics.pr_auc

Value:
  0.9805

Classification:
  MEASURED

Experiment:
  S02

Seed:
  20260827

Dataset:
  47,501 transactions
```

The component simply does:

```text
<Metric id="s02_arm_c_pr_auc" />
```

It should **never** do:

```text
<span>0.9805</span>
```

That architectural decision is important because it prevents the frontend from becoming a second, manually maintained research database.

---

# 16. What happens when the project is deployed

The final public system should look like:

```text
                   JUDGE
                     │
                     ▼
             PUBLIC WEBSITE
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   INTERACTIVE UI          EVIDENCE UI
          │                     │
          └──────────┬──────────┘
                     │
                  HTTPS
                     │
                     ▼
             HUGGING FACE
                FASTAPI
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     /score      /evidence    /artifact
        │            │            │
        ▼            ▼            ▼
      KIRA       evidence      V7 JSON
      logic       adapter       files
                     │
                     ▼
               provenance
```

And separately:

```text
GitHub
  │
  ├── source
  ├── research artifacts
  ├── tests
  ├── claims
  └── provenance

Kaggle
  │
  └── V7 execution evidence

Hugging Face
  │
  └── public runtime/API

Frontend host
  │
  └── judge-facing interface
```

This gives you a very clean separation.

---

# 17. What is actually "live"?

We should use three explicit states throughout the UI:

### `LIVE`

A request has actually gone through the deployed API/model.

### `MEASURED`

A number came from the authoritative V7 experiment.

### `REPLAY`

The UI is replaying a recorded experimental trajectory.

And:

### `NOT MEASURED`

Never turn it into a number.

That gives us:

```text
LIVE
MEASURED
REPLAY
NOT MEASURED
```

instead of misleading everything as "real-time."

---

# 18. What the judge can understand in 3 minutes

If the frontend is built correctly, a judge can do:

### 0:00–0:30

See:

> KIRA is an adversarial fraud detection system.

And immediately understand:

```text
BLUE
  ↓
RED
  ↓
PROBE
  ↓
BLUE
  ↓
HARDEN
  ↓
REPEAT
```

### 0:30–1:15

Click an attack.

Watch:

```text
transaction
→ detector
→ attacker
→ probe
→ detector
→ defense
```

### 1:15–2:00

See the evidence:

```text
96.67% baseline attack success
↓
0.00% hardened held-out ASR

+1.98% graph-fusion uplift
p=.046

10,000 adversarial attacks
6.00% success
```

### 2:00–2:30

See:

```text
Sparkov
C2ST 0.7780
TSTR ROC-AUC 0.7597
```

### 2:30–3:00

See:

```text
0 causal leakage violations
22/22 SHA-256 baseline integrity

BUT

Zero-day robustness
NOT MEASURED
```

At that point the judge understands both **what KIRA accomplished and where it does not yet claim more than the evidence supports.**

---

# 19. What we should NOT put on the frontend

I would explicitly prohibit these:

* ❌ "98% accurate"
* ❌ "100% zero-day protection"
* ❌ "production-ready fraud detection"
* ❌ "real-time training"
* ❌ "Sparkov Mastercard data"
* ❌ PR-AUC 1.0 as headline
* ❌ graph fusion universally improves performance
* ❌ latency benchmark presented as production latency
* ❌ `null → 0`
* ❌ hidden/unmeasured results represented as success
* ❌ manually typed duplicate metrics

And especially:

> **Do not turn the limitations section into a tiny footnote.**

Make the limitations part of the product.

---

# 20. Where HF deployment fits in the final architecture

So the final system is:

```text
                         ┌──────────────┐
                         │   GITHUB     │
                         │ source/evid. │
                         └──────┬───────┘
                                │
                         deployment build
                                │
               ┌────────────────┴────────────────┐
               │                                 │
               ▼                                 ▼
        FRONTEND HOST                     HUGGING FACE
          React/Vite                         FastAPI
               │                                 │
               │          HTTPS                  │
               └────────────────►───────────────┘
                                                  │
                                ┌─────────────────┼───────────────┐
                                │                 │               │
                                ▼                 ▼               ▼
                             SCORE            EVIDENCE        ARTIFACTS
                                │                 │               │
                                └─────────────────┼───────────────┘
                                                  ▼
                                      AUTHORITATIVE V7 EVIDENCE
                                                  │
                                                  ▼
                                         PROVENANCE / CLAIMS
```

And the **research provenance chain** remains:

```text
Kaggle V7
    ↓
47,501 transaction experiment
    ↓
JSON artifacts
    ↓
SHA-256 / provenance
    ↓
Evidence registry
    ↓
HF API
    ↓
Frontend
    ↓
Judge
```

That is the system I would deploy.

## The most important thing before HF

**Do not deploy yet until we verify the actual V7 artifacts against the frontend data contract one final time.**

We already know the backend contract is hardened. What we need now is a **deployment rehearsal**:

1. Map every frontend metric → exact V7 artifact → JSON path.
2. Verify every claim has an actual source.
3. Verify every displayed number matches the source.
4. Verify `null`/`LOW_SAMPLE` behavior.
5. Verify the closed-loop replay has no invented experimental results.
6. Verify HF can serve the exact same artifact schema.
7. Test the complete chain:

```text
Browser
 → HF API
 → artifact
 → metric
 → provenance drawer
```

8. Only then deploy.

**No more Kaggle notebook is needed for this architecture.** V7 is our scientific execution record; HF is the public runtime; the frontend is the judge-facing interpretation layer.

That gives us a project where the demo, backend, research evidence, and claims all point to the **same underlying source of truth**, which is exactly what we want before putting the public URL in front of judges.