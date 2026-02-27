from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, default=uuid.uuid4),
]

created_at_col = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]

updated_at_col = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]

deleted_at_col = Annotated[
    datetime | None,
    mapped_column(DateTime(timezone=True), default=None),
]


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]


class SoftDeleteMixin:
    deleted_at: Mapped[deleted_at_col]
