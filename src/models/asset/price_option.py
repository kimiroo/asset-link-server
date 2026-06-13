import uuid
from typing import Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Integer, func, Index, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import PriceType


# Price options for flexible listing contracts
class AssetPriceOption(Base):
    __tablename__ = "asset_price_options"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False,
        default=uuid.uuid4, server_default=func.gen_random_uuid()
    )

    # Tenant isolation key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    scope_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Foreign keys
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Price metadata with pick-one constraint
    type: Mapped[PriceType] = mapped_column(
        SQLEnum(PriceType, native_enum=False), nullable=False
    )
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deposit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Optimization and constraints
    __table_args__ = (
        # Enforce strict scope alignment with parent asset at the DB level
        ForeignKeyConstraint(
            ["asset_id", "scope_id", "workspace_id"],                 # Source columns in this table
            ["assets.id", "assets.scope_id", "assets.workspace_id"],  # Target columns in parent (Asset) table
            ondelete="CASCADE",                                       # Purge mapping if the parent asset is hard-deleted
            onupdate="CASCADE"                                        # Automatically propagate scope changes from parent asset
        ),

        Index("ix_asset_price_options_workspace_scope_id", "workspace_id", "scope_id"),
        Index("ix_asset_price_options_asset_id", "asset_id"),

        # Enforce single unique price scheme per contract type on each asset
        UniqueConstraint("asset_id", "type", name="uq_asset_price_options_asset_type"),
    )

    # ORM Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    asset = relationship("Asset", back_populates="price_options", foreign_keys=[asset_id])