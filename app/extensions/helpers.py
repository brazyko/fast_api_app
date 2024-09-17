import bcrypt

from fastapi import Depends
from fastapi.security import HTTPBearer

from app.core.models.users import User

from app.core.services.auth_service import AuthService


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


security = HTTPBearer()


async def validate_user(token: str = Depends(security)) -> User:
    return await AuthService.validate_user(token=token)
