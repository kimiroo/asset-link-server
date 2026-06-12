import uuid
from sqlalchemy import ForeignKey, String, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ContactTag(Base):
    __tablename__ = "contact_tags"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Core data field
    tag: Mapped[str] = mapped_column(String(32), nullable=False)

    # Optimization and constraints
    __table_args__ = (
        Index("ix_contact_tags_workspace_id", "workspace_id"),
        # Prevent duplicate contact tags within the same workspace
        UniqueConstraint("workspace_id", "tag", name="uq_contact_tags_workspace_tag"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])