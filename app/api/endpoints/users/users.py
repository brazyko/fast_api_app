from fastapi import Depends
from fastapi import APIRouter

from app.api.schemas.req_schemas import FindUserReq, GetUserReq
from app.core.models.users import User
from app.core.services.auth_service import AuthService
from app.core.services.users import UsersService


router = APIRouter(prefix="/users")


@router.get("/my-profile")
async def get_my_account(
    user_data: User = Depends(AuthService.validate_user),
):
    user_id = user_data.id
    users_service = UsersService()
    existing_user = await users_service.get_my_account(
        filter_data={"id": user_id}
    )
    return existing_user


@router.get("/find")
async def find_users(
    data: FindUserReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):
    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    filter_data = raw_data

    users_service = UsersService()
    user = await users_service.get_users_list(
        filter_data=filter_data
    )
    return user

@router.get("/get_user")
async def get_user_by_id(
    data: GetUserReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):
    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    user_id = raw_data.get("user_id")
    users_service = UsersService()
    user = await users_service.get_user_by_id(
        user_id=user_id
    )
    return user