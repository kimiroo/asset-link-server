import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Complex(Base):
    __tablename__ = "complexes"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    # Core data fields
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Optimization and constraints
    __table_args__ = (
        Index("ix_complexes_workspace_id", "workspace_id"),
        # Prevent duplicate complex names within the same workspace
        UniqueConstraint("workspace_id", "name", name="uq_complexes_workspace_name"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    assets = relationship("Asset", back_populates="complex")
    unit_types = relationship("UnitType", back_populates="complex", cascade="all, delete-orphan")