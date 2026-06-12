import uuid

from sqlalchemy import ForeignKey, String, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Foreign key to user (Unique constraint enforces 1:1 workspace ownership)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
            deferrable=True,      # Tells PostgreSQL this constraint can be delayed
            initially="DEFERRED"  # Delays the check automatically until the final commit
        ),
        nullable=False,
        unique=True
    )

    # Core fields
    workspace_name: Mapped[str] = mapped_column(String(32), nullable=False)

    # Optimization
    __table_args__ = (
        Index("ix_workspaces_owner_id", "owner_id"),
    )

    # ORM Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_workspace")
    members = relationship("User", foreign_keys="[User.workspace_id]", back_populates="workspace")