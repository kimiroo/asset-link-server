import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Float, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class UnitType(Base):
    __tablename__ = "unit_types"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Foreign keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    complex_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complexes.id", ondelete="CASCADE"), nullable=False
    )

    # Metadata fields
    type_name: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    area_exclusive: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_exclusive_pyeong: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_total_pyeong: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor_plan: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # Image URL or ID

    # Optimization and constraints
    __table_args__ = (
        Index("ix_unit_types_workspace_id", "workspace_id"),
        Index("ix_unit_types_complex_id", "complex_id"),
        # Prevent duplicate type names within the same complex
        UniqueConstraint("complex_id", "type_name", name="uq_unit_types_complex_type"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    complex = relationship("Complex", back_populates="unit_types", foreign_keys=[complex_id])
    assets = relationship("Asset", back_populates="unit_type")