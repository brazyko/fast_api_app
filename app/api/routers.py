from fastapi import APIRouter

from app.api.endpoints.auth.auth import router as auth
from app.api.endpoints.users.users import router as users
from app.api.endpoints.users.chats import router as chats

V1_PREFIX = "api"

api_router = APIRouter(prefix=f"/{V1_PREFIX}")

# Auth Router
auth_router = APIRouter(tags=[f"{V1_PREFIX}:auth"])
auth_router.include_router(auth)

# Users Router
users_router = APIRouter(tags=[f"{V1_PREFIX}:users"])
users_router.include_router(users)

# Chats Router
chats_router = APIRouter(tags=[f"{V1_PREFIX}:chats"])
chats_router.include_router(chats)

# Include common routes if needed
common_router = APIRouter(prefix="/common", tags=[f"{V1_PREFIX}:common"])

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(chats_router)
api_router.include_router(common_router)
