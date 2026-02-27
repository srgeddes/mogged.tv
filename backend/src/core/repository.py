from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from sqlalchemy import Select, exists, func, select

from core.exceptions import NotFoundError
from core.models import SoftDeleteMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class SortDirection(enum.StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class OrderBy:
    field: str
    direction: SortDirection = SortDirection.ASC


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- read operations ---

    async def get(self, **filters: Any) -> T:
        stmt = self._apply_filters(self._base_query(), filters)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(self.model.__name__, **filters)
        return row

    async def get_or_none(self, **filters: Any) -> T | None:
        stmt = self._apply_filters(self._base_query(), filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_attribute(
        self, attr: str, *, include_deleted: bool = False, **filters: Any
    ) -> Any:
        column = self._get_column(attr)
        stmt = select(column)
        if not include_deleted and self._has_soft_delete():
            stmt = self._exclude_deleted(stmt)
        stmt = self._apply_filters(stmt, filters)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(self.model.__name__, **filters)
        return row

    async def list(
        self,
        *,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **filters: Any,
    ) -> Sequence[T]:
        stmt = self._base_query(include_deleted=include_deleted)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_attribute(
        self,
        attr: str,
        *,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **filters: Any,
    ) -> Sequence[Any]:
        column = self._get_column(attr)
        stmt = select(column)
        if not include_deleted and self._has_soft_delete():
            stmt = self._exclude_deleted(stmt)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # --- write operations ---

    async def create(self, **kwargs: Any) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def bulk_create(self, items: list[dict[str, Any]]) -> Sequence[T]:
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def update(self, id: uuid.UUID, **kwargs: Any) -> T:
        instance = await self.get(id=id)
        for key, value in kwargs.items():
            if not hasattr(self.model, key):
                msg = f"{self.model.__name__} has no attribute '{key}'"
                raise ValueError(msg)
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID, *, hard: bool = False) -> None:
        instance = await self.get(id=id)
        if hard or not self._has_soft_delete():
            await self.session.delete(instance)
        else:
            instance.deleted_at = func.now()
        await self.session.flush()

    # --- aggregate operations ---

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        if self._has_soft_delete():
            stmt = self._exclude_deleted(stmt)
        stmt = self._apply_filters(stmt, filters)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, **filters: Any) -> bool:
        stmt = self._base_query().limit(1)
        stmt = self._apply_filters(stmt, filters)
        result = await self.session.execute(select(exists(stmt)))
        return result.scalar_one()

    # --- private helpers ---

    def _base_query(self, include_deleted: bool = False) -> Select:
        stmt = select(self.model)
        if not include_deleted and self._has_soft_delete():
            stmt = self._exclude_deleted(stmt)
        return stmt

    def _has_soft_delete(self) -> bool:
        return issubclass(self.model, SoftDeleteMixin)

    def _exclude_deleted(self, stmt: Select) -> Select:
        return stmt.where(self.model.deleted_at.is_(None))

    def _get_column(self, name: str) -> Any:
        if not hasattr(self.model, name):
            msg = f"{self.model.__name__} has no attribute '{name}'"
            raise ValueError(msg)
        return getattr(self.model, name)

    def _apply_filters(self, stmt: Select, filters: dict[str, Any]) -> Select:
        for key, value in filters.items():
            parts = key.split("__")
            if len(parts) == 1:
                column = self._get_column(parts[0])
                stmt = stmt.where(column == value)
            elif len(parts) == 2:
                field_name, operator = parts
                column = self._get_column(field_name)
                stmt = self._apply_operator(stmt, column, operator, value)
            else:
                msg = f"Invalid filter key: '{key}'"
                raise ValueError(msg)
        return stmt

    def _apply_operator(self, stmt: Select, column: Any, operator: str, value: Any) -> Select:
        if operator == "in":
            return stmt.where(column.in_(value))
        if operator == "ne":
            return stmt.where(column != value)
        if operator == "gt":
            return stmt.where(column > value)
        if operator == "gte":
            return stmt.where(column >= value)
        if operator == "lt":
            return stmt.where(column < value)
        if operator == "lte":
            return stmt.where(column <= value)
        if operator == "like":
            return stmt.where(column.like(value))
        if operator == "ilike":
            return stmt.where(column.ilike(value))
        if operator == "is_null":
            if value:
                return stmt.where(column.is_(None))
            return stmt.where(column.is_not(None))
        msg = f"Unknown filter operator: '{operator}'"
        raise ValueError(msg)

    def _apply_ordering(self, stmt: Select, order_by: list[OrderBy] | None) -> Select:
        if not order_by:
            return stmt
        for clause in order_by:
            column = self._get_column(clause.field)
            if clause.direction == SortDirection.DESC:
                stmt = stmt.order_by(column.desc())
            else:
                stmt = stmt.order_by(column.asc())
        return stmt
