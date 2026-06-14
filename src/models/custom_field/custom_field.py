import uuid
import datetime

from sqlalchemy import DateTime, String, ForeignKey, func, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.models.base import Base
from src.models.enums import CustomFieldType


class CustomFieldDefinition(Base):
    __tablename__ = "custom_field_definitions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    field_type: Mapped[CustomFieldType] = mapped_column(
        SQLEnum(CustomFieldType, native_enum=False), nullable=False
    )
    options: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True) # For SELECT
    remarks: Mapped[str | None] = mapped_column(nullable=True)

    # Metadata
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    # Optimization and constraints
    __table_args__ = (
        Index("ix_custom_field_definitions_workspace_id", "workspace_id"),
    )