from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from users.models import User


class OrgRole(enum.StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    creator: Mapped[User] = relationship("User", foreign_keys=[created_by], lazy="raise")
    members: Mapped[list[OrganizationMember]] = relationship(
        "OrganizationMember", back_populates="organization", lazy="raise"
    )


class OrganizationMember(Base, TimestampMixin):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        Index("ix_organization_members_organization_id", "organization_id"),
        Index("ix_organization_members_user_id", "user_id"),
    )

    id: Mapped[uuid_pk]
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    role: Mapped[OrgRole] = mapped_column(Enum(OrgRole, name="org_role"), default=OrgRole.MEMBER)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="members", lazy="raise"
    )
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], lazy="raise")
