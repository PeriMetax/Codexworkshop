# Taxonomy Validator (MVP)

Production-ready internal MVP for validating, correcting, reviewing, and syncing campaign taxonomy strings to ad platforms with a mandatory human-in-the-loop workflow.

## 1) Architecture Summary

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
- Ingestion endpoint accepts campaign dataset + mapping file (CSV/XLSX/JSON).
- Mapping file is config-driven and defines delimiter, component order, allowed values, aliases/synonyms, and defaults.
- Validation engine parses taxonomy and classifies issues:
  - invalid structure/component count
  - missing required components
  - invalid component values
- Correction engine applies layered strategy:
  1. exact / mapping match
  2. alias normalization
  3. fuzzy matching (RapidFuzz)
  4. pattern/default inference
  5. LLM fallback scaffold (flagged low confidence)
- Human review workflow captures accept/reject/amend decisions with reviewer metadata.
- Sync workflow uses connector abstraction; Meta Ads connector scaffold included with dry-run support.
- Full audit trail tables for suggestions, review actions, sync jobs/results.

### Frontend (Next.js + TypeScript)
Screens included:
- Upload / ingest page
- Validation results page
- Review queue
- Record detail / edit page
- Sync status page
- Dashboard page

### Async jobs
- Celery worker scaffold with Redis broker/backend for future background queue expansion.

## 2) Folder Structure

```text
.
├── backend
│   ├── app
│   │   ├── api/routes.py
│   │   ├── core/config.py
│   │   ├── db/session.py
│   │   ├── models/entities.py
│   │   ├── schemas/taxonomy.py
│   │   ├── services/
│   │   │   ├── correction.py
│   │   │   ├── ingestion.py
│   │   │   ├── validator.py
│   │   │   └── connectors/
│   │   │       ├── base.py
│   │   │       └── meta_ads.py
│   │   ├── workers/celery_app.py
│   │   └── main.py
│   ├── tests/test_validation_correction.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend
│   ├── src/app/* (upload/results/review/record/sync/dashboard)
│   ├── src/components/Nav.tsx
│   ├── src/lib/api.ts
│   └── Dockerfile
├── data
│   ├── sample_mapping.json
│   └── sample_taxonomy.csv
├── notebooks
│   └── taxonomy_validator_workbook.ipynb
├── .env.example
└── docker-compose.yml
```

## 3) Data Model

Core entities:
- `taxonomy_records`
- `taxonomy_components`
- `mapping_rules`
- `correction_suggestions`
- `review_actions`
- `platform_sync_jobs`
- `platform_sync_results`
- `users`

Record lifecycle statuses supported:
- ingested → validated → valid/invalid → suggested/pending_review → approved/rejected → ready_to_sync → synced/sync_failed

## 4) API Endpoints (Sample)

- `POST /api/v1/ingest`
  - multipart form:
    - `dataset_file`: CSV/XLSX/JSON
    - `mapping_file`: JSON (or tabular coercible)
- `GET /api/v1/records?status=pending_review`
- `POST /api/v1/records/{record_id}/review`
- `POST /api/v1/sync`
- `GET /api/v1/dashboard`
- `GET /health`

## 5) Local Setup

### Prerequisites
- Docker + Docker Compose

### Run with Docker
```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

### Ingest sample data
Use UI Upload page or curl:
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "dataset_file=@data/sample_taxonomy.csv" \
  -F "mapping_file=@data/sample_mapping.json"
```

## 6) Environment Variables

Copy `.env.example` as `.env` and edit values as needed.
Important values:
- `DATABASE_URL`
- `REDIS_URL`
- `CONFIDENCE_AUTO_THRESHOLD`
- `META_ACCESS_TOKEN`
- `LLM_ENABLED`, `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`

## 7) Governance, Auditability, and Safety

- No silent overwrite design: corrections are explicit and auditable.
- Human-in-the-loop required for low-confidence suggestions.
- Confidence threshold routing for auto-suggest vs review queue.
- Dry-run sync mode defaults safe validation before push.
- Sync attempts persist request/response/failure reason.

## 8) Tests

Run backend unit tests:
```bash
cd backend
pytest
```

Coverage in this MVP focuses on validation/correction logic.

## 9) Extensibility Notes

- Add new platform connectors by implementing `PlatformConnector` interface.
- Extend mapping schema for platform object-level routing (campaign/adset/ad).
- Replace LLM fallback scaffold with constrained JSON prompt/response validator.
- Promote sync workflow to async Celery tasks for large batch throughput.
