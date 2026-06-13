import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import AccessControlType

class ScopeAccessControl(Base):
    __tablename__ = "scope_access_controls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Target Security Container (What)
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="CASCADE"), nullable=False
    )

    # Subject Target (Who: Can assign to a specific User OR an entire Directory node)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    directory_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("directories.id", ondelete="CASCADE"), nullable=True
    )

    # Access privilege definition (e.g., "READ", "WRITE", "ADMIN")
    access_level: Mapped[AccessControlType] = mapped_column(
        SQLEnum(AccessControlType, native_enum=False),
        nullable=False,
        default=AccessControlType.READ,
        server_default=AccessControlType.READ.value
    )

    __table_args__ = (
        # Data Integrity Check: Ensure either user_id OR directory_id is set, but never both or neither
        CheckConstraint(
            "(user_id IS NOT NULL AND directory_id IS NULL) OR (user_id IS NULL AND directory_id IS NOT NULL)",
            name="chk_scope_acl_subject_exclusive"
        ),

        # Prevent duplicate privilege records for the same subject and scope
        UniqueConstraint("scope_id", "user_id", name="uq_scope_acl_user"),
        UniqueConstraint("scope_id", "directory_id", name="uq_scope_acl_directory"),

        # High-speed permission lookups for target subject
        Index("ix_scope_acl_lookup_user", "workspace_id", "user_id"),
        Index("ix_scope_acl_lookup_directory", "workspace_id", "directory_id"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    scope = relationship("Scope", foreign_keys=[scope_id])
    user = relationship("User", foreign_keys=[user_id])
    directory = relationship("Directory", foreign_keys=[directory_id])