import uuid
from typing import Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Boolean, Integer, func, Index, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import ContactRole


# N:M Junction table between Assets and Contacts with custom payload
class AssetContact(Base):
    __tablename__ = "asset_contacts"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Composite foreign key components (Declared without inline ForeignKeys)
    scope_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )

    # Relationship payload fields
    role: Mapped[Optional[ContactRole]] = mapped_column(
        SQLEnum(ContactRole, native_enum=False), nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ownership_share: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Percentage (0-100)

    # Optimization and constraints
    __table_args__ = (
        # Enforce strict scope alignment with parent asset at the DB level
        ForeignKeyConstraint(
            ["asset_id", "scope_id", "workspace_id"],                 # Source columns in this table
            ["assets.id", "assets.scope_id", "assets.workspace_id"],  # Target columns in parent (Asset) table
            ondelete="CASCADE",                                       # Purge mapping if the parent asset is hard-deleted
            onupdate="CASCADE"                                        # Automatically propagate scope changes from parent asset
        ),

        Index("ix_asset_contacts_workspace_scope_id", "workspace_id", "scope_id"),
        Index("ix_asset_contacts_asset_id", "asset_id"),
        Index("ix_asset_contacts_contact_id", "contact_id"),

        # Prevent assigning the exact same person to the exact same role on a single asset twice
        UniqueConstraint("asset_id", "contact_id", "role", name="uq_asset_contacts_asset_contact_role"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    asset = relationship("Asset", back_populates="asset_contacts", foreign_keys=[asset_id])
    contact = relationship("Contact", back_populates="asset_contacts", foreign_keys=[contact_id])