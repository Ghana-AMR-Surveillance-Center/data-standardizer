## Recommended Tech Stack (Robust, Modern, User-Friendly)

- Frontend (Phase 2+):
  - React + TypeScript (Next.js App Router)
  - Component library: MUI or Ant Design; Charting: Plotly.js + ECharts
  - State: TanStack Query; Form: React Hook Form + Zod
  - Auth: OAuth2/OIDC (Keycloak/Auth0/Azure AD)
  - Accessibility/i18n: WCAG AA; react-intl or lingui

- Backend (Phase 1 now; Phase 2 scaling):
  - FastAPI + Pydantic v2 for APIs and schema validation
  - Worker queue: Celery or RQ with Redis for long-running jobs (imports, transforms)
  - Storage: Postgres (metadata), DuckDB/Parquet (data lake), S3/MinIO (artifacts)
  - ETL Core: decoupled services for mapping, interpretation (CLSI/EUCAST), validation, exports
  - Observability: structlog/loguru + OpenTelemetry; Prometheus metrics; Sentry

- Packaging & Ops:
  - Poetry/uv for dependency management; Docker images; Helm charts for k8s
  - CI/CD: GitHub Actions (lint/test/build/publish); image scanning; IaC with Terraform (optional)

## Current System & Migration Plan

The current Streamlit app is production-hardened and suitable for MVP. We added a FastAPI service (`api/`) and a `core/` layer with schemas and services to incrementally migrate logic out of UI modules.

### Phase 1 (done here)
- Core schemas (`core/schemas.py`) for canonical AMR and GLASS rows
- Core services: mapping, interpretation, validation
- API integrations using core services; extra endpoint for ND/NM interpretation

### Phase 2
- Add job queue (Redis + RQ/Celery) for background processing; expose job endpoints
- Persist lineage and audit logs in Postgres; store artifacts in S3/MinIO
- Enrich vocabularies; admin sync for breakpoints and dictionaries

### Phase 3
- Frontend rewrite (Next.js): mapping wizard, builder UI, validation dashboards, exports
- RBAC and OIDC; embed API docs (OpenAPI) and interactive consoles

## Code Organization (Target)

```
src/
  core/
    schemas.py
    services/
      mapping.py
      interpretation.py
      validation.py
      export.py
  api/
    app.py
  ui/ (future react app) 
```

The Streamlit UI can remain for operators while the React app is built; both call the FastAPI/worker APIs.


