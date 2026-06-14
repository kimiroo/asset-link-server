import uuid

from sqlalchemy import ForeignKey, func, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import Base


class CustomFieldScope(Base):
    __tablename__ = "custom_field_scopes"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False
    )

    # Scope definition
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scopes.id", ondelete="RESTRICT"),
        nullable=False
    ) # NOT tenant isolation key
    custom_field_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("custom_field_definitions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Optimization
    __table_args__ = (
        Index(
            "ix_custom_field_scopes_workspace_scope_id_cfd",
            "workspace_id",
            "scope_id",
            "custom_field_definition_id"
        ),

        UniqueConstraint(
            "workspace_id",
            "scope_id",
            "custom_field_definition_id",
            name="uq_custom_field_scopes_workspace_scope_id_cfd"
        ),
    )