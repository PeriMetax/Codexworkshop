import json
from collections import Counter

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import (
    CorrectionSuggestion,
    MappingRule,
    PlatformSyncJob,
    PlatformSyncResult,
    RecordStatus,
    ReviewAction,
    SyncStatus,
    TaxonomyRecord,
)
from app.schemas.taxonomy import ReviewDecision, SyncRequest
from app.services.connectors.meta_ads import MetaAdsConnector
from app.services.correction import suggest_correction
from app.services.ingestion import read_tabular_file, parse_mapping
from app.services.validator import validate_taxonomy_string

router = APIRouter()


@router.post("/ingest")
def ingest(
    dataset_file: UploadFile = File(...),
    mapping_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    mapping_raw = read_tabular_file(mapping_file)
    if isinstance(mapping_raw, list):
        mapping_obj = mapping_raw[0] if mapping_raw else {}
    else:
        mapping_obj = mapping_raw
    if isinstance(mapping_obj, str):
        mapping_obj = json.loads(mapping_obj)

    mapping = parse_mapping(mapping_obj)
    rule = MappingRule(name="uploaded", raw_config=mapping)
    db.add(rule)
    db.flush()

    dataset_rows = read_tabular_file(dataset_file)
    created_ids = []
    for row in dataset_rows:
        rec = TaxonomyRecord(
            row_id=str(row.get("row_id", "")),
            source_platform=row.get("source_platform", "unknown"),
            raw_taxonomy=row.get("taxonomy_string", ""),
            market=row.get("market") or None,
            review_status=RecordStatus.ingested,
            sync_status=SyncStatus.not_started,
        )
        db.add(rec)
        db.flush()

        result = validate_taxonomy_string(rec.raw_taxonomy, mapping)
        rec.parsed_components = result.parsed
        rec.error_types = result.errors

        if result.errors:
            rec.validation_status = "invalid"
            rec.review_status = RecordStatus.invalid
            suggestion = suggest_correction(result.parsed, mapping)
            rec.suggested_taxonomy = suggestion.suggested_taxonomy
            rec.confidence_score = suggestion.confidence
            rec.review_status = RecordStatus.pending_review if suggestion.needs_review else RecordStatus.suggested

            db.add(
                CorrectionSuggestion(
                    record_id=rec.id,
                    suggestion_source=suggestion.source,
                    suggested_components=suggestion.suggested_components,
                    suggested_taxonomy=suggestion.suggested_taxonomy,
                    confidence_score=suggestion.confidence,
                    reasoning=suggestion.reasoning,
                    auto_suggested=not suggestion.needs_review,
                )
            )
        else:
            rec.validation_status = "valid"
            rec.review_status = RecordStatus.valid
            rec.suggested_taxonomy = rec.raw_taxonomy
            rec.confidence_score = 1.0
        created_ids.append(rec.id)

    db.commit()
    return {"ingested": len(created_ids), "record_ids": created_ids, "mapping_rule_id": rule.id}


@router.get("/records")
def list_records(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(TaxonomyRecord)
    if status:
        query = query.filter(TaxonomyRecord.review_status == status)
    return query.order_by(TaxonomyRecord.id.desc()).all()


@router.post("/records/{record_id}/review")
def review_record(record_id: int, decision: ReviewDecision, db: Session = Depends(get_db)):
    record = db.get(TaxonomyRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.add(
        ReviewAction(
            record_id=record_id,
            reviewer_id=decision.reviewer_id,
            action=decision.action,
            final_taxonomy=decision.final_taxonomy,
            comments=decision.comments,
        )
    )

    if decision.action in {"accept", "amend"}:
        record.suggested_taxonomy = decision.final_taxonomy
        record.review_status = RecordStatus.approved
    else:
        record.review_status = RecordStatus.rejected
    db.commit()
    return {"record_id": record_id, "review_status": record.review_status}


@router.post("/sync")
def sync_records(payload: SyncRequest, db: Session = Depends(get_db)):
    connector = MetaAdsConnector()
    job = PlatformSyncJob(platform=payload.platform, dry_run=payload.dry_run, status="running")
    db.add(job)
    db.flush()

    for rid in payload.record_ids:
        record = db.get(TaxonomyRecord, rid)
        if not record:
            continue
        if record.review_status not in {RecordStatus.approved, RecordStatus.valid, RecordStatus.suggested}:
            continue

        external_id = record.row_id or str(record.id)
        result = connector.sync_record(external_id=external_id, taxonomy_value=record.suggested_taxonomy or record.raw_taxonomy, dry_run=payload.dry_run)
        status = "synced" if result["status"] in {"success", "dry_run"} else "failed"

        db.add(
            PlatformSyncResult(
                job_id=job.id,
                record_id=record.id,
                status=status,
                request_payload=result.get("request", {}),
                response_payload=result.get("response", {}),
                failure_reason=None if status == "synced" else str(result.get("response")),
            )
        )
        record.sync_status = SyncStatus.dry_run if payload.dry_run else (SyncStatus.synced if status == "synced" else SyncStatus.failed)
        record.review_status = RecordStatus.synced if status == "synced" else RecordStatus.sync_failed

    job.status = "completed"
    db.commit()
    return {"job_id": job.id, "status": job.status}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.query(func.count(TaxonomyRecord.id)).scalar() or 0
    valid = db.query(func.count(TaxonomyRecord.id)).filter(TaxonomyRecord.validation_status == "valid").scalar() or 0
    invalid = db.query(func.count(TaxonomyRecord.id)).filter(TaxonomyRecord.validation_status == "invalid").scalar() or 0
    pending_review = db.query(func.count(TaxonomyRecord.id)).filter(TaxonomyRecord.review_status == RecordStatus.pending_review).scalar() or 0
    synced = db.query(func.count(TaxonomyRecord.id)).filter(TaxonomyRecord.sync_status.in_([SyncStatus.synced, SyncStatus.dry_run])).scalar() or 0

    errors = Counter()
    for row in db.query(TaxonomyRecord.error_types).all():
        for err in (row[0] or []):
            errors[err] += 1

    platform_counts = db.query(TaxonomyRecord.source_platform, func.count(TaxonomyRecord.id)).group_by(TaxonomyRecord.source_platform).all()

    return {
        "total_rows": total,
        "valid_rows": valid,
        "invalid_rows": invalid,
        "pct_auto_corrected": round(((invalid - pending_review) / invalid) * 100, 2) if invalid else 0,
        "pct_pending_review": round((pending_review / total) * 100, 2) if total else 0,
        "pct_synced": round((synced / total) * 100, 2) if total else 0,
        "top_error_categories": errors.most_common(5),
        "platform_breakdown": [{"platform": p, "count": c} for p, c in platform_counts],
    }
