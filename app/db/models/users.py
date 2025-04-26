from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base
from typing import Optional


class UserModel(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255), default=None, nullable=True
    )

    companies = relationship("CompanyModel", back_populates="owner")
    invitations = relationship(
        "InvitationModel", back_populates="user", cascade="all, delete"
    )
    requests = relationship(
        "RequestModel", back_populates="user", cascade="all, delete"
    )
    memberships = relationship(
        "MembershipModel", back_populates="user", cascade="all, delete"
    )
