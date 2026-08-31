# Hugging Face Space — Docker SDK, CPU basic (2 vCPU / 16 GB / free).
#
# Deliberately Python-only. The React app is built LOCALLY and `frontend/dist`
# is committed, so npm never runs here. npm inside a Space build is the single
# most likely last-day deploy failure; this removes it entirely.
#
# Local:  docker build -t mcdl . && docker run -p 7860:7860 mcdl

FROM python:3.11-slim

# Spaces run the container as uid 1000. Create that user before anything is
# copied, or every COPY lands root-owned and the app cannot read its own files.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCDL_SCALE=tiny

WORKDIR $HOME/app

# Dependencies first so code edits do not invalidate the layer.
COPY --chown=user pyproject.toml ./
COPY --chown=user src ./src
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY --chown=user api ./api
COPY --chown=user configs ./configs
COPY --chown=user frontend/dist ./frontend/dist
COPY --chown=user artifacts ./artifacts

EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
