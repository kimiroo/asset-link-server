import datetime
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String, Boolean, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ContactPhone(Base):
    __tablename__ = "contact_phones"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="RESTRICT"), nullable=False
    )

    # Foreign keys
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )

    # Phone details
    label: Mapped[Optional[str]] = mapped_column(String(64), nullable=True) # e.g., "Mobile", "Office"
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    # Status flags
    is_local: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_opted_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    opted_out_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optimization
    __table_args__ = (
        # Enforce strict scope alignment with parent contact
        ForeignKeyConstraint(
            ["contact_id", "scope_id", "workspace_id"],
            ["contacts.id", "contacts.scope_id", "contacts.workspace_id"],
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),

        Index("ix_contact_phones_workspace_scope_id_phone", "workspace_id", "scope_id", "phone"),
        Index("ix_contact_phones_contact_id", "contact_id")
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    contact = relationship("Contact", back_populates="phones", foreign_keys=[contact_id])