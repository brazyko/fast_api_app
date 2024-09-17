from app.core.dto.base import BaseDTO


class UserCreateDTO(BaseDTO):
    username: str
    first_name: str
    last_name: str
    password: str
