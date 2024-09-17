from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.models.users import User
from app.core.services.auth import SECRET_KEY, ALGORITHM


security = HTTPBearer()


class AuthService:
    @staticmethod
    async def validate_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> User:
        token = credentials.credentials
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        from app.core.services.users import UsersService

        users_service = UsersService()
        user = await users_service.get_first(filter_data={"username": username})
        if user is None:
            raise credentials_exception

        return user
