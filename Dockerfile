FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

RUN addgroup --system careerpilot \
    && adduser --system --ingroup careerpilot careerpilot \
    && mkdir -p /workspace/data \
    && chown -R careerpilot:careerpilot /workspace

COPY --chown=careerpilot:careerpilot pyproject.toml README.md ./
COPY --chown=careerpilot:careerpilot app ./app
COPY --chown=careerpilot:careerpilot frontend ./frontend
COPY --chown=careerpilot:careerpilot data ./data

RUN python -m pip install --upgrade pip \
    && python -m pip install .

USER careerpilot

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
