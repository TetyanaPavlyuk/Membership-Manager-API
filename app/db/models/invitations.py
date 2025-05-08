from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.enums import StatusEnum


class InvitationModel(Base):
    __tablename__ = "invitations"

    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False
    )

    company = relationship("CompanyModel", back_populates="invitations")
    user = relationship("UserModel", back_populates="invitations")
