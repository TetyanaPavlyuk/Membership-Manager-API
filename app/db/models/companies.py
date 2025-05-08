from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base


class CompanyModel(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    owner = relationship("UserModel", back_populates="companies")
    invitations = relationship(
        "InvitationModel", back_populates="company", cascade="all, delete"
    )
    requests = relationship(
        "RequestModel", back_populates="company", cascade="all, delete"
    )
    memberships = relationship(
        "MembershipModel", back_populates="company", cascade="all, delete"
    )
