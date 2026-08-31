# COMPETITION — verified brief

> **STATUS: TEMPLATE — NOT YET VERIFIED.**
> Owner: either person, **first 30 minutes of BLOCK 0**.
>
> Every requirement in this project traces back to competition material pasted into
> a conversation. That material could **not be located or verified independently**.
> Until somebody opens the real competition page and fills this in, everything
> downstream is built on an unverified premise.
>
> This is the cheapest possible task and the most expensive one to skip.

---

## 1. Identification

| | |
|---|---|
| Competition name | TBD |
| URL | TBD |
| Host / sponsor | TBD |
| Platform | TBD (Kaggle?) |
| Verified by | TBD |
| Verified on | TBD |

## 2. Deadline

| | |
|---|---|
| Submission closes | TBD |
| **Timezone** | **TBD — this is the field people get wrong** |
| Equivalent in IST | TBD |
| Any earlier team-formation deadline? | TBD |

Kaggle deadlines are typically **23:59 UTC**, which is 05:29 IST the following
morning. Read the other way, "31 August EOD" can mean you lose five and a half
hours you thought you had. Get this exact and write both timezones.

## 3. Format — the contradiction to resolve

The original spec says two incompatible things:

- P16: *"the private leaderboard determines final Kaggle standing"*
- Step 8: a **Writeup** submission with DOCX and GitHub

A writeup hackathon has no leaderboard. **These need very different work.** If you
build for a leaderboard that does not exist, a day is gone.

| Question | Answer |
|---|---|
| Is there a scored leaderboard? | TBD |
| If yes: what is the metric? | TBD |
| If yes: submission file format? | TBD |
| If yes: daily submission limit? | TBD |
| Is a Writeup required? | TBD |
| Writeup word limit? | TBD |
| Is there a track to select? | TBD |

**If a leaderboard exists**, the 2-hour escape hatch is: fit the provided data (or
Sparkov), emit `submission.csv`, submit early to confirm the format works, then
return to the main build. Do not let it consume more than that.

## 4. Deliverables

Tick each off against the actual rules page, not against this project's assumptions.

- [ ] Public GitHub repository — naming convention? TBD
- [ ] `TeamName.docx` — required sections? Page limit? TBD
- [ ] Kaggle Writeup — required sections? TBD
- [ ] Working web prototype — is a public URL required, or is a video acceptable? TBD
- [ ] Video / presentation — required? Length limit? TBD
- [ ] Anything else the rules mention TBD

## 5. Team

| | |
|---|---|
| Team formed on the platform? | TBD |
| Max team size | TBD |
| All members registered with correct emails? | TBD |
| Eligibility restrictions (region, student status)? | TBD |

Registered emails are a common failure point — a member registered with a different
address than the one listed in the writeup can invalidate a submission.

## 6. Data rules

| Question | Answer |
|---|---|
| Is a competition dataset provided? | TBD |
| Is external data allowed? | TBD |
| Are pretrained models allowed? | TBD |
| Are there licence constraints on what we publish? | TBD |

This matters directly: we plan to use **Sparkov (CC0)** as the external reality
anchor. If external data is prohibited, that anchor moves to the provided dataset
instead and [EVALUATION.md](EVALUATION.md) §3 changes. We already excluded BAF over
its CC BY-NC-ND licence — see [RESEARCH.md](RESEARCH.md) §1.

## 7. Judging

| | |
|---|---|
| Published criteria and weights | TBD |
| Who judges | TBD |
| Is there a live demo or Q&A round? | TBD |

If criteria are published, map each one to a section of the report and to a view in
the app. Judging against stated criteria is a much easier target than judging
against a guess.

## 8. Prohibitions

Anything the rules forbid — write it here verbatim rather than paraphrasing.

TBD

---

## 9. Impact on the build

Fill this in after the rest. What changes now that we know the truth?

| Finding | What it changes |
|---|---|
| TBD | TBD |

---

## 10. Submission audit — gate 7

Run through this before clicking submit, not after.

- [ ] Team formed, all members registered, emails correct
- [ ] GitHub repository **public** and it actually clones
- [ ] README works from a clean clone
- [ ] Live demo URL loads (and the Space is awake)
- [ ] `TeamName.docx` uploaded
- [ ] Writeup complete
- [ ] **Writeup actually submitted, not saved as a draft**
- [ ] Confirmation visible on screen
- [ ] No secrets anywhere — check git **history**, not just the working tree
- [ ] Every number in the report has a `run_id` in `brain/CLAIMS.md`
- [ ] `docs/LIMITATIONS.md` is honest and complete
- [ ] Screenshot or recording of the confirmation, kept as proof
