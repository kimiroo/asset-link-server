import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class Asset(Base):
    """SQLAlchemy model for managing properties and assets."""

    __tablename__ = "assets"

    # 🔑 Primary Key using UUID v4 (Highly recommended for Supabase/PostgreSQL)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # 📝 Core Asset Information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(nullable=False)

    # 🗺️ Location Details
    address: Mapped[str] = mapped_column(String(500), nullable=False)

    # ⏳ Audit Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )