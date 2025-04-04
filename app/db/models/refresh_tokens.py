from datetime import datetime
from sqlalchemy import Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.models.base import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String, ForeignKey("users.email"), nullable=False
    )
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("UserModel", back_populates="refresh_token")

    def is_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()
