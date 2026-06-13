import uuid
from typing import Optional, List
from sqlalchemy import ForeignKey, String, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Contact(Base):
    __tablename__ = "contacts"

    # Primary key
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

    # Core metadata
    name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    # Hybrid tag system (JSONB array)
    tags: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, nullable=True, default=list, server_default="[]"
    )
    remarks: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Optimization
    __table_args__ = (
        Index("ix_contacts_workspace_scope_id", "workspace_id", "scope_id"),
        Index("ix_contacts_name", "name"), # For quick customer search
        Index("ix_contacts_tags", "tags", postgresql_using="gin"), # High-speed contact tag filtering

        # Required for composite foreign key references from child tables (e.g., contact_phones)
        UniqueConstraint("id", "scope_id", "workspace_id", name="uq_contacts_id_scope_workspace")
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    phones = relationship("ContactPhone", back_populates="contact", cascade="all, delete-orphan")
    asset_contacts = relationship("AssetContact", back_populates="contact", cascade="all, delete-orphan")