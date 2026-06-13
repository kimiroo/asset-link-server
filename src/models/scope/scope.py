import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Scope(Base):
    __tablename__ = "scopes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Self-referential parent link for hierarchical tree structure
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="RESTRICT"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Optimization
    __table_args__ = (
        Index("ix_scopes_workspace_parent", "workspace_id", "parent_id"),

        # Prevent duplicate sibling scope names within the same parent/workspace context
        UniqueConstraint("workspace_id", "parent_id", "name", name="uq_scopes_workspace_parent_name"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])

    # Self-referential tree relations
    parent = relationship("Scope", remote_side=[id], back_populates="children")
    children = relationship("Scope", back_populates="parent", cascade="all, delete-orphan")