from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class MembershipModel(Base):
    __tablename__ = "memberships"

    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    company = relationship("CompanyModel", back_populates="memberships")
    user = relationship("UserModel", back_populates="memberships")
