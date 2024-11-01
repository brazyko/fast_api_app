from sqlalchemy import text

from app.core.models.message import Message
from app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository
from app.extensions.dbs import get_session


class MessagesRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = Message

    async def get_message_by_id(self, message_id: int):
        q_params = {
            "message_id": message_id,
        }
        base_stmt = """
            SELECT
                *,
                messages.id as message_id,
                u.first_name,
                u.last_name,
                u.username
            FROM messages
            LEFT JOIN users as u on messages.user_id = u.id
        """

        where_stmt = """
            WHERE messages.id = :message_id
        """

        stmt = f"{base_stmt} {where_stmt}"

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params=q_params)
            return result.first()