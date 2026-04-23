import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RecordStatus(str, enum.Enum):
    ingested = "ingested"
    validated = "validated"
    valid = "valid"
    invalid = "invalid"
    suggested = "suggested"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    ready_to_sync = "ready_to_sync"
    synced = "synced"
    sync_failed = "sync_failed"


class SyncStatus(str, enum.Enum):
    not_started = "not_started"
    dry_run = "dry_run"
    synced = "synced"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaxonomyRecord(Base):
    __tablename__ = "taxonomy_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    row_id: Mapped[str] = mapped_column(String(100), index=True)
    source_platform: Mapped[str] = mapped_column(String(50), index=True)
    raw_taxonomy: Mapped[str] = mapped_column(Text)
    parsed_components: Mapped[dict] = mapped_column(JSON, default=dict)
    validation_status: Mapped[str] = mapped_column(String(30), default="unknown")
    error_types: Mapped[list] = mapped_column(JSON, default=list)
    suggested_taxonomy: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    review_status: Mapped[str] = mapped_column(Enum(RecordStatus), default=RecordStatus.ingested)
    sync_status: Mapped[str] = mapped_column(Enum(SyncStatus), default=SyncStatus.not_started)
    market: Mapped[str | None] = mapped_column(String(20), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    components = relationship("TaxonomyComponent", back_populates="record")
    suggestions = relationship("CorrectionSuggestion", back_populates="record")


class TaxonomyComponent(Base):
    __tablename__ = "taxonomy_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("taxonomy_records.id", ondelete="CASCADE"), index=True)
    component_name: Mapped[str] = mapped_column(String(100))
    component_value: Mapped[str] = mapped_column(String(255))
    component_order: Mapped[int] = mapped_column(Integer)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)

    record = relationship("TaxonomyRecord", back_populates="components")


class MappingRule(Base):
    __tablename__ = "mapping_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(50), default="v1")
    name: Mapped[str] = mapped_column(String(255))
    raw_config: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CorrectionSuggestion(Base):
    __tablename__ = "correction_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("taxonomy_records.id", ondelete="CASCADE"), index=True)
    suggestion_source: Mapped[str] = mapped_column(String(30))
    suggested_components: Mapped[dict] = mapped_column(JSON)
    suggested_taxonomy: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[str] = mapped_column(Text)
    auto_suggested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    record = relationship("TaxonomyRecord", back_populates="suggestions")


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("taxonomy_records.id", ondelete="CASCADE"), index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(30))
    final_taxonomy: Mapped[str] = mapped_column(Text)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PlatformSyncJob(Base):
    __tablename__ = "platform_sync_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(30), index=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PlatformSyncResult(Base):
    __tablename__ = "platform_sync_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("platform_sync_jobs.id", ondelete="CASCADE"), index=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("taxonomy_records.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    response_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
