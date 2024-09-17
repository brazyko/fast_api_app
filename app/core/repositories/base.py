from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Tuple

import pymongo
from beanie import Document
from sqlalchemy import update, select, func, delete, text, or_, String

from app.extensions.dbs import Base, get_session

ModelType = TypeVar("ModelType", bound=Base)


class AbstractRepository(ABC):
    pass


class AbstractBaseRepository(AbstractRepository):
    MODEL: Optional[Type[Base]] = None

    @classmethod
    def get_first(cls, filter_data: dict) -> Any:
        raise NotImplementedError

    @classmethod
    async def get_list(
        cls, filter_data: dict, order_data: Tuple[str] = ("id",)
    ) -> List[Any]:
        raise NotImplementedError

    @classmethod
    async def count(cls, filter_data: dict) -> int:
        raise NotImplementedError

    @classmethod
    async def create(
        cls,
        data: dict,
    ) -> Any:
        raise NotImplementedError

    @classmethod
    async def create_bulk(
        cls,
        items: List[dict],
    ) -> List[Any]:  # type: ignore
        raise NotImplementedError

    @classmethod
    async def update(cls, filter_data: dict, data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    @classmethod
    async def update_bulk(cls, items: List[dict]) -> Any:
        raise NotImplementedError

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
    ) -> Any:
        raise NotImplementedError

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        raise NotImplementedError

    @classmethod
    async def remove_all(cls) -> None:
        raise NotImplementedError


class BaseSQLAsyncDrivenBaseRepository(AbstractBaseRepository):
    MODEL: Optional[Type[Base]] = None

    @staticmethod
    def __not_like_all(q: Any, k: Any, v: Any) -> Any:
        for item in v:
            q = q.filter(k.notlike(f"%{item}%"))
        return q

    @staticmethod
    def __any_e(q: Any, k: Any, v: Any) -> Any:
        q = q.filter(or_((k == i for i in v)))  # type: ignore
        return q

    __ATR_SEPARATOR: str = "__"
    LOOKUP_MAP = {
        "gt": lambda stmt, k, v: stmt.where(k > v),
        "gte": lambda stmt, k, v: stmt.where(k >= v),
        "lt": lambda stmt, k, v: stmt.where(k < v),
        "lte": lambda stmt, k, v: stmt.where(k <= v),
        "e": lambda stmt, k, v: stmt.where(k == v),
        "ne": lambda stmt, k, v: stmt.where(k != v),
        "in": lambda stmt, k, v: stmt.where(k.in_(v)),  # does not work with None
        "any_e": lambda q, k, v: BaseSQLAsyncDrivenBaseRepository.__any_e(q, k, v),
        "not_in": lambda stmt, k, v: stmt.where(k.not_in(v)),  # does not work with None
        "like": lambda q, k, v: q.filter(k.like(f"%{v}%")),
        "not_like_all": lambda q, k, v: BaseSQLAsyncDrivenBaseRepository.__not_like_all(
            q, k, v
        ),
        "jsonb_like": lambda stmt, k, v: stmt.where(k.cast(String).like(f"%{v}%")),
        "jsonb_not_like": lambda stmt, k, v: stmt.where(~k.cast(String).like(f"%{v}%")),
    }

    @classmethod
    def _parse_filter_key(cls, key: str) -> Tuple[str, str]:  # type: ignore
        splatted: list = key.split(cls.__ATR_SEPARATOR)

        if len(splatted) == 1:
            return key, "e"
        elif len(splatted) == 2:
            tmp_key = splatted[0]
            lookup = splatted[1]
            return tmp_key, lookup

    @classmethod
    def _parse_order_data(cls, order_data: Optional[Tuple[str]] = None) -> tuple:
        if not order_data:
            order_data = ()  # type: ignore
        parsed_order_data = []

        for order_item in order_data:  # type: ignore
            order_item_tmp = order_item
            if order_item_tmp.startswith("-"):
                order_item_tmp = order_item[1:]
                parsed_order_data.append(getattr(cls.model(), order_item_tmp).desc())
            else:
                parsed_order_data.append(getattr(cls.model(), order_item_tmp).asc())

        return tuple(parsed_order_data)

    @classmethod
    def _parse_order_data_for_target(
        cls, target: Base, order_data: Optional[Tuple[str]] = None
    ) -> tuple:
        if not order_data:
            order_data = ()  # type: ignore
        parsed_order_data = []

        for order_item in order_data:  # type: ignore
            order_item_tmp = order_item
            if order_item_tmp.startswith("-"):
                order_item_tmp = order_item[1:]
                parsed_order_data.append(getattr(target, order_item_tmp).desc())
            else:
                parsed_order_data.append(getattr(target, order_item_tmp).asc())

        return tuple(parsed_order_data)

    @classmethod
    def _apply_where(cls, stmt: Any, filter_data: dict) -> Any:
        for key, value in filter_data.items():
            tmp_key, lookup = cls._parse_filter_key(key)
            stmt = cls.LOOKUP_MAP[lookup](stmt, getattr(cls.model(), tmp_key), value)
        return stmt

    @classmethod
    def model(cls) -> Type[Base]:
        if not cls.MODEL:
            raise AttributeError
        return cls.MODEL

    @classmethod
    async def __get_max_id(cls) -> int:
        tmp_table_name = cls.model().__tablename__
        max_id_stmp = f"SELECT MAX(t.id) FROM {tmp_table_name} t;"
        async with get_session() as session:
            max_id_q = await session.execute(statement=text(max_id_stmp))
            max_id = max_id_q.scalars().first() or 0
            return max_id

    @classmethod
    async def get_first(cls, filter_data: dict) -> ModelType:  # type: ignore
        filter_data.pop("limit", "")
        filter_data.pop("offset", "")

        stmt = select(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        async with get_session() as session:
            result = await session.execute(stmt)

        return result.scalars().first()  # type: ignore

    @classmethod
    async def get_list(
        cls,
        filter_data: Optional[dict] = None,
        order_data: Optional[Tuple[str]] = ("id",),
    ) -> List[ModelType]:  # type: ignore
        if not filter_data:
            filter_data = {}
        limit = filter_data.pop("limit", None)
        offset = filter_data.pop("offset", 0)

        stmt = select(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)
        stmt = stmt.order_by(*cls._parse_order_data(order_data))
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        async with get_session() as session:
            result = await session.execute(stmt)

        return result.scalars().all()  # type: ignore

    @classmethod
    async def count(cls, filter_data: Optional[dict] = None) -> int:  # type: ignore
        if not filter_data:
            filter_data = {}

        filter_data.pop("limit", "")
        filter_data.pop("offset", "")

        stmt = select(func.count(cls.model().id))
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        async with get_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()  # type: ignore

    @classmethod
    async def create(
        cls,
        data: dict,
    ) -> ModelType:  # type: ignore

        async with get_session() as session:
            if "id" not in list(data.keys()):
                max_id = await cls.__get_max_id()
                data["id"] = max_id + 1
            new_obj = cls.model()(**data)
            session.add(new_obj)
            await session.commit()

        return new_obj

    @classmethod
    async def create_bulk(
        cls,
        items: List[dict],
    ) -> List[ModelType]:  # type: ignore

        max_id = await cls.__get_max_id()
        async with get_session() as session:
            raw_items = []
            for index, item in enumerate(items):
                if item.get("id") is None or item.get("id", -1) < 0:
                    tmp_id = max_id + 1 + index
                    item["id"] = tmp_id
                raw_items.append(cls.model()(**item))
            session.add_all(raw_items)
            await session.flush()
            await session.commit()
        return raw_items

    @classmethod
    async def update(cls, filter_data: dict, data: Dict[str, Any]) -> ModelType:  # type: ignore
        stmt = update(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)
        stmt = stmt.values(**data)
        stmt.execution_options(synchronize_session="fetch")

        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()
        # TODO make per on request

        updated_obj: Base = await cls.get_first(filter_data=filter_data)

        return updated_obj

    @classmethod
    async def update_bulk(cls, items: List[dict]) -> None:
        if items:
            stmt = update(cls.model())

            async with get_session() as session:
                await session.execute(stmt, items)
                await session.flush()
                await session.commit()

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
    ) -> ModelType:  # type: ignore
        count = await cls.count(filter_data=filter_data)  # TODO make via exists
        if count:
            data_tmp = data
            data_tmp.pop("id", None)
            data_tmp.pop("uuid", None)
            return await cls.update(filter_data=filter_data, data=data)  # type: ignore
        else:
            return await cls.create(data=data)  # type: ignore
        # TODO raise exception

    @classmethod
    async def remove(
        cls,
        filter_data: Dict[str, Any],  # type: ignore
    ) -> None:  # mypy: ignore-errors
        stmt = delete(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def remove_all(cls) -> None:  # type: ignore
        stmt = delete(cls.model())
        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()


class BaseNoSQLAsyncDrivenBaseRepository(AbstractBaseRepository):
    MODEL: Optional[Type[Document]] = None

    __ATR_SEPARATOR: str = "__"
    LOOKUP_MAP = {
        "gt": lambda stmt, k, v: stmt.find(k > v),
        "gte": lambda stmt, k, v: stmt.find(k >= v),
        "lt": lambda stmt, k, v: stmt.find(k < v),
        "lte": lambda stmt, k, v: stmt.find(k <= v),
        "e": lambda stmt, k, v: stmt.find(k == v),
        "ne": lambda stmt, k, v: stmt.find(k != v),
        "like": lambda stmt, k, v: stmt.find(
            {k: {"$regex": f".*{v}.*", "$options": "i"}}
        ),
        "in": lambda stmt, k, v: stmt.find({k: {"$in": v}}),
    }

    @classmethod
    def _parse_filter_key(cls, key: str) -> Tuple[str, str]:  # type: ignore
        splatted: list = key.split(cls.__ATR_SEPARATOR)

        if len(splatted) == 1:
            return key, "e"
        elif len(splatted) == 2:
            tmp_key = splatted[0]
            lookup = splatted[1]
            return tmp_key, lookup

    @classmethod
    def _parse_order_data(cls, order_data: Optional[Tuple[str]] = None) -> list:
        if not order_data:
            order_data = ()  # type: ignore
        parsed_order_data = []

        for order_item in order_data:  # type: ignore
            order_item_tmp = order_item
            if order_item_tmp.startswith("-"):
                order_item_tmp = order_item[1:]
                parsed_order_data.append(
                    (getattr(cls.model(), order_item_tmp), pymongo.DESCENDING)
                )
            else:
                parsed_order_data.append(
                    (getattr(cls.model(), order_item_tmp), pymongo.ASCENDING)
                )

        return parsed_order_data

    @classmethod
    def _apply_where(cls, stmt: Any, filter_data: dict) -> Any:
        for key, value in filter_data.items():
            tmp_key, lookup = cls._parse_filter_key(key)
            stmt = cls.LOOKUP_MAP[lookup](stmt, getattr(cls.model(), tmp_key), value)
        return stmt

    @classmethod
    def model(cls) -> Type[Document]:
        if not cls.MODEL:
            raise AttributeError
        return cls.MODEL

    @classmethod
    async def get_first(cls, filter_data: dict) -> Optional[Document]:  # type: ignore
        filter_data.pop("limit", "")
        filter_data.pop("offset", "")
        limit = filter_data.pop("limit", None)
        offset = filter_data.pop("offset", 0)
        stmt = cls.model().find()
        stmt = cls._apply_where(stmt=stmt, filter_data=filter_data)
        stmt = stmt.skip(offset)
        if limit:
            stmt = stmt.limit(limit)
        return await stmt.first_or_none()

    @classmethod
    async def get_list(
        cls,
        filter_data: Optional[dict] = None,
        order_data: Optional[Tuple[str]] = ("id",),
    ) -> List[Document]:  # type: ignore
        if not filter_data:
            filter_data = {}
        limit = filter_data.pop("limit", None)
        offset = filter_data.pop("offset", 0)
        stmt = cls.model().find()
        stmt = cls._apply_where(stmt=stmt, filter_data=filter_data)
        stmt = stmt.sort(cls._parse_order_data(order_data))
        stmt = stmt.skip(offset)
        if limit:
            stmt = stmt.limit(limit)
        return await stmt.to_list()

    @classmethod
    async def count(cls, filter_data: Optional[dict] = None) -> int:  # type: ignore
        if not filter_data:
            filter_data = {}
        filter_data.pop("limit", None)
        filter_data.pop("offset", 0)
        stmt = cls.model().find()
        stmt = cls._apply_where(stmt=stmt, filter_data=filter_data)
        return await stmt.count()

    @classmethod
    async def create(
        cls,
        data: dict,
    ) -> Document:  # type: ignore

        if not data.get("created_at") and hasattr(cls.model(), "created_at"):
            data["created_at"] = datetime.utcnow()
        if not data.get("updated_at") and hasattr(cls.model(), "updated_at"):
            data["updated_at"] = datetime.utcnow()
        row = await cls.model()(**data).create()
        return row

    @classmethod
    async def create_bulk(  # type: ignore
        cls,
        items: List[dict],
    ) -> None:  # type: ignore
        items_tmp = []
        for data in items:
            if not data.get("created_at") and hasattr(cls.model(), "created_at"):
                data["created_at"] = datetime.utcnow()
            if not data.get("updated_at") and hasattr(cls.model(), "updated_at"):
                data["updated_at"] = datetime.utcnow()
            row = cls.model()(**data)
            items_tmp.append(row)
        if items_tmp:
            await cls.model().insert_many(items_tmp)

    @classmethod
    async def update(cls, filter_data: dict, data: Dict[str, Any]) -> Document:  # type: ignore
        raise NotImplementedError

    @classmethod
    async def update_bulk(cls, items: List[dict]) -> None:
        raise NotImplementedError

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
    ) -> Document:  # type: ignore
        raise NotImplementedError

    @classmethod
    async def remove(
        cls,
        filter_data: Dict[str, Any],  # type: ignore
    ) -> None:  # mypy: ignore-errors
        stmt = cls.model().find()
        stmt = cls._apply_where(stmt=stmt, filter_data=filter_data)
        await stmt.delete()

    @classmethod
    async def remove_all(cls) -> None:  # type: ignore
        stmt = cls.model().find()
        await stmt.delete()
