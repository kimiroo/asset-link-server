import datetime
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class AssetConsultLog(Base):
    __tablename__ = "asset_consult_log"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="RESTRICT"), nullable=False
    ) # TODO: [IMPORTANT] Add lower bound application security logic
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Foreign keys
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Log timestamp evaluated at execution time
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    consult_log: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Optimization
    __table_args__ = (
        # Ensure log belongs to the same workspace as the asset, even if scope is different
        ForeignKeyConstraint(
            ["asset_id", "workspace_id"],
            ["assets.id", "assets.workspace_id"],
            ondelete="CASCADE"
        ),

        Index("ix_asset_consult_log_workspace_scope_id", "workspace_id", "scope_id"),
        Index("ix_asset_consult_log_asset_id", "asset_id"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    asset = relationship("Asset", back_populates="consult_logs", foreign_keys=[asset_id])
    creator = relationship("User", foreign_keys=[created_by])