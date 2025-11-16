## Deployment (Docker Compose)

Prereqs: Docker, Docker Compose.

1) Build and start

```
make up
```

Services:
- Streamlit app: http://localhost:8501
- API: http://localhost:9000 (health: /health)
- Redis and RQ worker for async jobs

2) Security

- Set `API_KEY` in your environment before `make up` to require the `X-API-Key` header on API endpoints.
- Set `CORS_ALLOWED_ORIGINS` (comma-separated) for browsers.

3) Jobs workflow

- Enqueue ND/NM interpretation:
  POST /v1/jobs/interpret-ndnm
  GET /v1/jobs/{id}

- Enqueue GLASS export:
  POST /v1/jobs/export-glass
  GET /v1/jobs/{id}
  Artifact: `artifacts/glass_{job_id}.csv`

4) Logs & audit

- `logs/audit.jsonl` stores JSON lines of job events.


