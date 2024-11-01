from app.core.repositories.user_chats import UserChatsRepository
from app.core.services.base import BaseEntityService


class UserChatsService(BaseEntityService):
    def __init__(self) -> None:
        self.repository = UserChatsRepository()