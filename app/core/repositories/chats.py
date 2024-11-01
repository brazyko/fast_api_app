from sqlalchemy import text
from app.core.models.chat import Chat
from app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository
from app.extensions.dbs import get_session

class ChatsRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = Chat

    async def get_users_chats(self, filter_data, order_data: tuple):
        limit = filter_data.get('limit')
        offset = filter_data.get('offset')
        user_id = filter_data.get('user_id')
        q_params = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }
        base_stmt = """
            SELECT
                *
            FROM chats
        """

        where_stmt = """
            WHERE chats.user_ids @> ARRAY[:user_id]::integer[]
        """

        order_stmt = ""
        if order_data:
            order_data_tmp = []
            for item in order_data:
                tmp = item
                is_desc = False
                if tmp.startswith("-"):
                    tmp = f"{tmp[1:]}"
                    is_desc = True
                    tmp = f"{tmp}"
                if is_desc:
                    tmp = f"{tmp} DESC"
                order_data_tmp.append(tmp)
            order_data_str = ", ".join(order_data_tmp)
            order_stmt = f"""ORDER BY {order_data_str}"""

        if not limit:
            stmt = f"{base_stmt} {where_stmt} {order_stmt} OFFSET :offset;"
        else:
            stmt = f"{base_stmt} {where_stmt} {order_stmt} OFFSET :offset LIMIT :limit;"

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params=q_params)
            return list(result)


    async def get_chat_by_id(self, filter_data):

        user_id = filter_data.get('user_id')
        chat_id = filter_data.get('chat_id')
        limit = filter_data.get('limit')
        offset = filter_data.get('offset')
        q_params = {
            "user_id": user_id,
            "chat_id": chat_id,
            "limit": limit,
            "offset": offset,
        }
        base_stmt = """
            SELECT
                *
            FROM chats
        """

        where_stmt = """
            WHERE chats.id = :chat_id
        """

        if not limit:
            stmt = f"{base_stmt} {where_stmt} OFFSET :offset;"
        else:
            stmt = f"{base_stmt} {where_stmt} OFFSET :offset LIMIT :limit;"

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params=q_params)
            return result.first()

    async def get_chat_messages(self, filter_data: dict, order_data: tuple):
        limit = filter_data.get('limit')
        offset = filter_data.get('offset')
        user_id = filter_data.get('user_id')
        chat_id = filter_data.get('chat_id')
        q_params = {
            "limit": limit,
            "offset": offset,
            "chat_id": chat_id,
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
            WHERE messages.chat_id = :chat_id
        """

        order_stmt = ""
        if order_data:
            order_data_tmp = []
            for item in order_data:
                tmp = item
                is_desc = False
                if tmp.startswith("-"):
                    tmp = f"{tmp[1:]}"
                    is_desc = True
                    tmp = f"{tmp}"
                if is_desc:
                    tmp = f"{tmp} DESC"
                order_data_tmp.append(tmp)
            order_data_str = ", ".join(order_data_tmp)
            order_stmt = f"""ORDER BY {order_data_str}"""

        if not limit:
            stmt = f"{base_stmt} {where_stmt} {order_stmt} OFFSET :offset;"
        else:
            stmt = f"{base_stmt} {where_stmt} {order_stmt} OFFSET :offset LIMIT :limit;"

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params=q_params)
            return list(result)
