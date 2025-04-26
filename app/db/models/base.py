from uuid import uuid4
from datetime import datetime
from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.testing.schema import mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False
    )
