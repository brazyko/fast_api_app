from app.core.models.user_chats import UserChat
from app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository

class UserChatsRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = UserChat
