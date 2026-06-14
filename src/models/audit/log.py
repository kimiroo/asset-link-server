import uuid
import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, func, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.models.base import Base
from src.models.enums import AuditActionType, AuditTableName


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    action: Mapped[AuditActionType] = mapped_column(
        SQLEnum(AuditActionType, native_enum=False), nullable=False
    )

    # Target information
    target_table: Mapped[AuditTableName] = mapped_column(
        SQLEnum(AuditTableName, native_enum=False), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Changed information
    before_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    after_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Other metadata
    client_ip: Mapped[str | None] = mapped_column(nullable=True)

    # Optimization and constraints
    __table_args__ = (
        Index("ix_audit_logs_workspace_id", "workspace_id"),
        Index("ix_audit_logs_workspace_target", "workspace_id", "user_id", "action", "target_table", "target_id"),
        Index("ix_audit_logs_workspace_timestamp", "workspace_id", timestamp.desc()),
    )