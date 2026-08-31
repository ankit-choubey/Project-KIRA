# DEPLOYMENT — runbook

Written assuming no prior experience with Hugging Face Spaces or Kaggle notebooks.
Follow it top to bottom.

> **Do this on day 1, in BLOCK 0, with a hello-world.** Deployment discovered on
> day 3 is how projects die. Deploy something trivial first, then keep pushing to
> the same Space as the app grows.

---

## 0. What you need

| | |
|---|---|
| GitHub account | the repo must be **public** — the competition requires it, and Kaggle needs to clone it |
| Hugging Face account | free. huggingface.co/join |
| Kaggle account | free. Phone-verify it or notebooks cannot use the internet |
| Node + npm | to build the frontend locally |
| Python 3.10+ | to run the gates |

No paid accounts. No API keys beyond a Hugging Face write token.

---

## 1. The moving parts

```
GitHub (public)  --->  Kaggle CPU notebook  --->  HF Dataset repo  --->  HF Space
   source code          runs the pipeline          artifact store       live demo
```

Three separate things on Hugging Face, easy to confuse:

| | What it is | Ours |
|---|---|---|
| **Space** | a hosted app | the live demo |
| **Dataset repo** | a git-LFS store | where run artifacts live |
| Model repo | not used | — |

---

## 2. Create the Space

1. Go to **huggingface.co/new-space**
2. **Owner** — your username. **Space name** — e.g. `mastercard-ai-defense-lab`
3. **License** — choose one (MIT is fine)
4. **Select the SDK** — pick **Docker**, then **Blank** template
5. **Hardware** — `CPU basic · 2 vCPU · 16 GB · FREE`
6. **Visibility** — **Public**
7. Click **Create Space**

You now have an empty git repo at
`https://huggingface.co/spaces/<user>/<space-name>`.

### The YAML header that makes it work

The Space reads configuration from a YAML block at the very top of `README.md`.
Ours already has it:

```
---
title: Mastercard AI Defense Lab
emoji: shield
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
---
```

`sdk: docker` and `app_port: 7860` are the two lines that matter. Without them the
Space shows **"Configuration error"**.

GitHub renders this block as a small table at the top of the README. That is
expected and harmless.

---

## 3. Push to the Space

The Space is a git remote. Add it alongside `origin`:

```bash
git remote add space https://huggingface.co/spaces/<user>/<space-name>
```

Before every deploy:

```bash
cd frontend && npm run build && cd ..
git add -f frontend/dist
git commit -m "deploy"
git push space main
```

`make frontend` does the build and the force-add in one step. `frontend/dist` is in
`.gitignore` — the `-f` is deliberate, so it is only committed when you mean to deploy.

When prompted for a password, use a **Hugging Face access token**, not your
password: Settings → Access Tokens → New token → **write** scope.

Watch the build in the Space's **Logs** tab. A successful build takes about two
minutes.

### Why npm never runs inside Docker

The Dockerfile is pure Python and just copies `frontend/dist`. npm inside a Space
build is slow, occasionally flaky, and fails at the worst possible moment.
Building locally removes an entire failure class from the last day. This is
decision D-005.

---

## 4. Artifacts — getting real numbers into the Space

Two options. Use A on day 1, move to B once the pipeline is real.

### Option A — bake them into the image (simplest)

The Dockerfile copies `artifacts/demo/` into the image. Keep that directory under
about 200 MB, downsample the replay stream to ~20k rows, and commit it. No token,
no network call at startup.

### Option B — pull from a Dataset repo (for the real run)

1. **huggingface.co/new-dataset** → name it e.g. `mcdl-artifacts` → Public → Create
2. In the **Space** → Settings → **Variables and secrets** → **New secret**
   → name `HF_TOKEN`, value = your write token
3. The Space downloads the artifacts at startup with `snapshot_download`
4. Kaggle uploads to it at the end of the run with `upload_folder`

**Free Spaces have ephemeral disk.** Anything written at runtime is lost on
restart. Never treat the Space filesystem as storage — the Dataset repo is the
store.

---

## 5. Verify the deployment

```bash
curl https://<user>-<space-name>.hf.space/api/health
```

Expect `{"status":"ok", "run_id":"...", "is_fixture":true, ...}`.

Then, in a browser, check all four:

- [ ] `/` loads the app
- [ ] `/evidence` loads **directly** — type it in the address bar and press enter.
      This tests the SPA fallback. A 404 here means a judge refreshing the page sees
      an error.
- [ ] `/api/health` returns JSON, not HTML
- [ ] **Open it on a phone on mobile data.** Not on your laptop, not on your wifi.
      This is the only test that proves it works for someone else.

To wire the live URL into gate 0:

```bash
export MCDL_SPACE_URL=https://<user>-<space-name>.hf.space
make gate 0
```

---

## 6. Kaggle — the full run

### Set up

1. **kaggle.com** → Settings → **Phone verify** your account.
   Without this, notebooks cannot access the internet and cannot clone the repo.
2. Create a notebook: **Code → New Notebook**
3. In the right sidebar: **Accelerator = None (CPU)**, **Internet = On**
4. Confirm the session: 4 CPU cores, ~30 GB RAM, 12 h limit

> **Accelerator must be None.** This project needs no GPU, and CPU sessions draw
> from a **separate allocation** — they do not consume the ~30 h/week GPU quota.
> Your other projects keep their GPU hours.

### Get the reference dataset

In the notebook sidebar: **Add Input → Datasets → search
`kartik2112/fraud-detection`** → Add. It mounts read-only at
`/kaggle/input/fraud-detection/`. Licence is CC0, so there is nothing to worry about.

### Run

`notebooks/kaggle/README.md` has the exact cells. In outline: clone the public
repo, install the package with the `heavy` extras, set `MCDL_SCALE=full`, run the
pipeline, then upload `artifacts/<run_id>/` to the Dataset repo.

Store the HF token via **Add-ons → Secrets**, never pasted into a cell — a token in
notebook output is a leaked credential.

### Survive the 12-hour limit

Checkpoint after every stage and make the notebook resumable. If a session dies,
the run must not restart from zero.

---

## 7. Local development

```bash
make setup            # install (uv if present, else pip)
make gate 0           # contracts, fixtures, tests
make api              # FastAPI on :8000
make dev              # FastAPI :8000 + Vite :5173 with /api proxied
```

Work against `:5173`. Before deploying, build and check `:8000` — that is the path
the Space uses, and it is where `base: './'` and route-ordering problems appear.

Optional: `make docker` builds and runs the exact image the Space will run. If it
works locally on port 7860, it will work on the Space.

---

## 8. Before the judging session

- [ ] **Visit the Space URL once.** Free Spaces sleep after 48 h idle and take
      about 30 s to wake. Do not let a judge be the one who wakes it.
- [ ] Click through all five views and confirm the FIXTURE banner is **gone**
      (i.e. real artifacts are loaded)
- [ ] Confirm a number in the UI matches `artifacts/<run_id>/evaluation.json`
- [ ] Have the 90-second demo video in the repo as a fallback

---

## 9. When it breaks

| Symptom | Cause | Fix |
|---|---|---|
| "Configuration error" | missing YAML header | `sdk: docker` + `app_port: 7860` at the top of `README.md` |
| Build fails on permissions | files copied as root | Dockerfile needs `useradd -m -u 1000 user`, `USER user`, `COPY --chown=user` |
| Blank page on the Space, fine locally | absolute asset paths | `base: './'` in `vite.config.ts`; rebuild and recommit `dist` |
| `/evidence` 404s on refresh | no SPA fallback | catch-all must serve `index.html` for non-API paths |
| `/api/*` returns HTML | static mounted before the API | mount static **last** |
| Space OOM at 16 GB | loading full frames | load parquet lazily; page the stream endpoint |
| Kaggle cannot clone the repo | repo is private, or internet off | make it public; toggle Internet On; phone-verify |
| Kaggle session dies at 12 h | no checkpoints | checkpoint per stage; make the run resumable |
| Push to Space rejected | password used instead of token | use a **write**-scoped HF access token |

More in [ERRORS_PLAYBOOK.md](ERRORS_PLAYBOOK.md) and `brain/ERRORS.md`.

---

## 10. Security

- **Never commit** `.env`, `kaggle.json`, or any token. They are in `.gitignore`.
- Secrets go in HF Space settings or Kaggle Add-ons → Secrets.
- Before submission, check the git history, not just the working tree — a token
  committed and then deleted is still in the history.
- Gate 7 checks for a committed `.env`, but it cannot catch a token pasted into a
  notebook cell. Check that yourself.
