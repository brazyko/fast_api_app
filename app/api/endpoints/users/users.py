from fastapi import Depends
from fastapi import APIRouter
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
