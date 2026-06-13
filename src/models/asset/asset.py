import datetime
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKey, String, Date, DateTime, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import SourceType


class Asset(Base):
    __tablename__ = "assets"

    # Primary key (primary_key=True implies unique=True)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="RESTRICT"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Address & Location hierarchy
    complex_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complexes.id", ondelete="SET NULL"), nullable=True
    )
    bld: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    unit_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unit_types.id", ondelete="SET NULL"), nullable=True
    )

    # Core data fields
    tags: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True, default=list, server_default="[]"
    )
    color: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    # Date operations
    intake_date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, default=datetime.date.today, server_default=func.current_date()
    )
    expiration_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    # Business routing & Assignment
    source_type: Mapped[SourceType] = mapped_column(
        String(16), nullable=False, default=SourceType.COLD_SOURCE
    )
    referring_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    assigned_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Descriptions & Custom extensions
    remarks: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    custom_field: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, default=dict, server_default="{}"
    )

    # System audit trails
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Database performance tuning
    __table_args__ = (
        Index("ix_assets_workspace_scope_id", "workspace_id", "scope_id"),
        Index("ix_assets_complex_bld_unit", "complex_id", "bld", "unit"),
        Index("ix_assets_unit_type_id", "unit_type_id"),
        Index("ix_assets_assigned_user_id", "assigned_user_id"),
        Index("ix_assets_source_type", "source_type"),
        Index("ix_assets_tags", "tags", postgresql_using="gin"),
        Index(
            "ix_assets_remarks_trgm", "remarks",
            postgresql_using="gin",
            postgresql_ops={"remarks": "gin_trgm_ops"}
        ),

        # Required to allow composite foreign key references from child tables (e.g., asset_contacts)
        UniqueConstraint("id", "scope_id", "workspace_id", name="uq_assets_id_scope_workspace")
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    complex = relationship("Complex", back_populates="assets", foreign_keys=[complex_id])
    unit_type = relationship("UnitType", back_populates="assets", foreign_keys=[unit_type_id])
    referring_agent = relationship("Agent", foreign_keys=[referring_agent_id])
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], back_populates="assigned_assets")

    price_options = relationship("AssetPriceOption", back_populates="asset", cascade="all, delete-orphan")

    # These contain sensitive info managed by App-level security.
    # Force explicit querying to prevent accidental exposure via joinedload.
    consult_logs = relationship("AssetConsultLog", back_populates="asset", cascade="all, delete-orphan", lazy="raise")
    asset_contacts = relationship("AssetContact", back_populates="asset", cascade="all, delete-orphan", lazy="raise")