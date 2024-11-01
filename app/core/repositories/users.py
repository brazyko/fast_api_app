from sqlalchemy import text

from app.core.models.users import User
from app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository
from app.extensions.dbs import get_session


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User

    async def get_user(self, filter_data):
        limit = filter_data.get('limit')
        offset = filter_data.get('offset')

        q_params = {
            "limit": limit,
            "offset": offset
        }
        base_stmt = """
            SELECT
                *
            FROM users
        """

        where_stmt = """
            WHERE users.id > 0
        """
        user = filter_data.get('user')
        user_int = None
        if user and user.isdigit():
            user_int = int(user)

        if user and not user_int:
            q_params["user"] = user
            where_stmt = (
                f"{where_stmt} AND "
                f"( "
                f"   users.username LIKE CONCAT('%', CAST(:user as TEXT) ,'%') OR"
                f"   users.first_name LIKE CONCAT('%', CAST(:user as TEXT),'%') OR"
                f"   users.last_name LIKE CONCAT('%', CAST(:user as TEXT) ,'%')"
                f")"
            )
        if user_int:
            q_params["parent_int"] = user_int
            where_stmt = f"{where_stmt} AND parent.id = :parent_int"

        if not limit:
            stmt = f"{base_stmt} {where_stmt} OFFSET :offset;"
        else:
            stmt = f"{base_stmt} {where_stmt} OFFSET :offset LIMIT :limit;"

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params=q_params)
            return list(result)