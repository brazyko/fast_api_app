from abc import ABC
from typing import Any, Dict, List, Optional, Tuple

from app.core.dto.base import BaseDTO
from app.core.repositories.base import AbstractBaseRepository
from app.extensions.dbs import Base


class AbstractBaseService(ABC):
    pass


class AbstractEntityService(AbstractBaseService):
    async def count(self, filter_data: Optional[dict] = None) -> int:
        raise NotImplementedError

    async def get_list(
        self, filter_data: Optional[dict], order_data: Optional[Tuple[str]]
    ) -> List[Any]:
        raise NotImplementedError

    async def get_first(self, filter_data: Optional[dict]) -> Any:
        raise NotImplementedError

    async def create_bulk(self, items: List[dict]) -> None:
        raise NotImplementedError

    async def update_or_create(self, filter_data: dict, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def update_bulk(self, items: List[dict]) -> None:
        raise NotImplementedError


class BaseEntityService(AbstractEntityService):
    BASE_DTO_CLASS: BaseDTO

    @classmethod
    def get_base_dto(cls) -> BaseDTO:
        if not cls.BASE_DTO_CLASS:
            raise AttributeError
        return cls.BASE_DTO_CLASS

    def __init__(self, repository: AbstractBaseRepository) -> None:
        self.repository = repository

    async def count(self, filter_data: Optional[dict] = None) -> int:
        if not filter_data:
            filter_data = {}
        count = await self.repository.count(filter_data=filter_data)
        return count

    async def get_list(
        self,
        filter_data: Optional[dict] = None,
        order_data: Optional[Tuple[str]] = None,
    ) -> List[Any]:
        if not filter_data:
            filter_data = {}
        if not order_data:
            order_data = ()  # type: ignore
        rows: List[Base] = await self.repository.get_list(
            filter_data=filter_data,  # type: ignore
            order_data=order_data,  # type: ignore
        )
        dto_items = [self.get_base_dto()(**item.__dict__) for item in rows]  # type: ignore
        return dto_items

    async def get_first(self, filter_data: dict) -> Any:  # type: ignore
        row: Base = await self.repository.get_first(filter_data=filter_data)
        if row:
            return self.get_base_dto()(**row.__dict__)  # type: ignore
        return None

    async def create_bulk(self, items: List[dict]) -> None:
        await self.repository.create_bulk(items=items)

    async def update_or_create(
        self, filter_data: Dict[str, Any], data: Dict[str, Any]
    ) -> None:
        await self.repository.update_or_create(filter_data=filter_data, data=data)

    async def update_bulk(self, items: List[dict]) -> None:
        await self.repository.update_bulk(items=items)
