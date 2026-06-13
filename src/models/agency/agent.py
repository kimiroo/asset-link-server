import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Agent(Base):
    __tablename__ = "agents"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Foreign keys
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    agency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False
    )

    # Agent details
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Optimization
    __table_args__ = (
        Index("ix_agents_workspace_id", "workspace_id"),
        Index("ix_agents_agency_id", "agency_id"),
        Index("ix_agents_workspace_phone", "workspace_id", "phone"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    agency = relationship("Agency", back_populates="agents", foreign_keys=[agency_id])