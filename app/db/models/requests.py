from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.enums.status_enum import StatusEnum


class RequestModel(Base):
    __tablename__ = "requests"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False
    )

    user = relationship("UserModel", back_populates="requests")
    company = relationship("CompanyModel", back_populates="requests")
