import uuid

from sqlalchemy import ForeignKey, String, func, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE",
            deferrable=True,      # Tells PostgreSQL this constraint can be delayed
            initially="DEFERRED"  # Delays the check automatically until the final commit
        ),
        nullable=False
    )

    # Credentials & Metadata
    username: Mapped[str] = mapped_column(String(128), nullable=False, unique=True) # Email
    password: Mapped[str] = mapped_column(String(64), nullable=False) # Bcrypt hash
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        nullable=False,
        default=UserRole.EDITOR
    )

    # Optimization
    __table_args__ = (
        Index("ix_users_workspace_id", "workspace_id"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id], back_populates="members")
    owned_workspace = relationship("Workspace", foreign_keys="[Workspace.owner_id]", back_populates="owner", uselist=False)

    # Back-populations from other modules
    assigned_assets = relationship("Asset", back_populates="assigned_user")