# GEMINI.md — Antigravity-specific

@AGENTS.md

Everything in `AGENTS.md` and `.agents/rules/` applies. Antigravity-only notes:

- **Plan before editing.** Post the file list you intend to touch, then execute.
  Blocks in this project are deliberately narrow; a plan touching files outside
  your block is a signal you have misread the task.
- **Save artifacts to disk**, not into chat. Reports, profiles and metrics belong
  in `docs/` or `artifacts/` where `tools/gates.py` can read them.
- **Verify, then claim.** After implementing a block, run `make gate N` and paste
  the real output. Do not describe a gate as passing that you have not run.
- **Rule files are capped at 12,000 characters.** If you add to `.agents/rules/`,
  split rather than exceed the cap — content past it is silently dropped.
- The repo is deployed to a Hugging Face Space from `main`. Anything you commit
  to `frontend/dist/` ships to the live demo, so build before you commit.
