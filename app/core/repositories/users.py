from app.core.models.users import User
from app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User
