from typing import Optional
from app.core.models.users import User
from app.core.repositories.users import UsersRepository
from app.core.services.base import BaseEntityService
from app.extensions.helpers import hash_password


class UsersService(BaseEntityService):
    def __init__(self) -> None:
        self.repository = UsersRepository()

    async def count(self, filter_data: Optional[dict] = None) -> int:
        if not filter_data:
            filter_data = {}
        count = await self.repository.count(filter_data=filter_data)
        return count

    async def get_first(self, filter_data: Optional[dict] = None) -> Optional[User]:
        if not filter_data:
            filter_data = {}
        result = await self.repository.get_first(filter_data=filter_data)
        return result

    async def create_user(self, user_data: dict) -> None:
        username = user_data["username"]
        first_name = user_data["first_name"]
        last_name = user_data["last_name"]
        password = user_data["password"]
        hashed_password = hash_password(password)
        user_raw = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "password": hashed_password,
        }
        result = await self.repository.create(data=user_raw)
        return result

    async def get_my_account(self, filter_data: dict):
        me = await self.get_first(filter_data=filter_data)
        me_raw = {
            "username": me.username,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "created_at": me.created_at
        }
        return me_raw