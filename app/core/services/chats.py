import json
from datetime import datetime
from app.core.repositories.chats import ChatsRepository
from app.core.repositories.messages import MessagesRepository
from app.core.services.base import BaseEntityService
from app.core.services.users import UsersService


class ChatsService(BaseEntityService):
    def __init__(self) -> None:
        self.repository = ChatsRepository()

    async def get_my_chats(self, filter_data, order_data = ("-updated_at",)):
        chats_raw = await self.repository.get_users_chats(filter_data=filter_data, order_data=order_data)
        chats = []
        for chat in chats_raw:
            chat_raw = {
                "id": chat.id,
                "name": chat.name,
                "participants": chat.user_ids,
                "last_message": chat.last_message,
                "updated_at": chat.updated_at,
            }
            chats.append(chat_raw)
        return chats

    async def get_chat_by_id(self, filter_data: dict):
        user_id = filter_data.get("user_id")
        chat_raw = await self.repository.get_chat_by_id(filter_data=filter_data)
        chat = {
            "id": chat_raw.id,
            "name": chat_raw.name,
            "user_ids": chat_raw.user_ids,
            "chat_type": chat_raw.chat_type,
            "description": chat_raw.description,
        }
        return chat

    async def create_chat(self, data: dict):
        chat_type = data.get("chat_type")
        participants = data.get("participants")
        users_service = UsersService()
        participants_names = await users_service.repository.get_list(filter_data={"id__in": participants})
        users_first_name_raw = [user.first_name for user in participants_names]
        users_first_name = ', '.join(users_first_name_raw)
        chat_raw = {
            "chat_type": chat_type,
            "user_ids": participants,
            "created_at": datetime.utcnow(),
            "name": users_first_name,
        }
        result = await self.repository.create(chat_raw)
        return result

    async def get_or_create_chat(self, filter_data: dict):
        user_id = filter_data.pop("user_id")
        receiver_id = filter_data.pop("receiver_id")
        filter_data = {
            "user_ids": [user_id, receiver_id],
        }
        chat = await self.repository.get_first(filter_data=filter_data)
        if chat:
            chat_id = chat.id
        else:
            new_chat = await self.create_chat(
                data={
                    "user_id": user_id,
                    "chat_type": "private",
                    "participants": [user_id, receiver_id],
                }
            )
            chat_id = new_chat["id"]
        return chat_id

    async def delete_chat(self, data: dict):
        chat_id = data.get("chat_id")
        await self.repository.remove(filter_data={"chat_id": chat_id})
        return 'deleted'

    async def get_chat_messages(self, filter_data: dict, order_data: tuple):
        messages_raw = await self.repository.get_chat_messages(filter_data=filter_data, order_data=order_data)
        results = []
        for message_raw in messages_raw:
            sender_info = {
                "user_id": message_raw.user_id,
                "first_name": message_raw.first_name,
                "last_name": message_raw.last_name,
                "username": message_raw.username,
            }
            message = {
                "id": message_raw.message_id,
                "chat_id": message_raw.chat_id,
                "content": message_raw.content,
                "sent_at": message_raw.sent_at,
                "seen_at": message_raw.seen_at,
                "is_read": message_raw.is_read,
                "reply_to_id": message_raw.reply_to_id,
                "reply_to_user_id": message_raw.reply_to_user_id,
                "reply_to_content": message_raw.reply_to_content,
                "reactions": message_raw.reactions,
                "sender_info": sender_info
            }
            results.append(message)
        results = results[::-1]
        return results

    async def get_chat_message_by_id(self, filter_data: dict):
        message_raw = await self.repository.get_first(filter_data=filter_data)
        sender_info = {
            "user_id": message_raw.user_id,
            "first_name": message_raw.first_name,
            "last_name": message_raw.last_name,
            "username": message_raw.username,
        }
        message = {
            "id": message_raw.message_id,
            "chat_id": message_raw.chat_id,
            "content": message_raw.content,
            "sent_at": message_raw.sent_at,
            "seen_at": message_raw.seen_at,
            "reply_to_id": message_raw.reply_to_id,
            "reply_to_user_id": message_raw.reply_to_user_id,
            "reply_to_content": message_raw.reply_to_content,
            "sender_info": sender_info
        }

        return message

    async def send_chat_message(self, message_data: json):
        user_id = message_data.get("user_id")
        content = message_data.get("content")
        reply_to_id = message_data.get("reply_to_id")
        reply_to_user_id = message_data.get("reply_to_user_id")
        reply_to_content = message_data.get("reply_to_content")
        chat_id = message_data.get("chat_id")
        message_repository = MessagesRepository()
        message_raw = {
            "chat_id": int(chat_id),
            "user_id": int(user_id),
            "content": content,
            "reply_to_id": reply_to_id,
            "reply_to_user_id": reply_to_user_id,
            "reply_to_content": reply_to_content,
            "sent_at": datetime.utcnow(),
        }
        chat_to_update = {
            "last_message": message_raw["content"][:120],
            "updated_at": message_raw["sent_at"],
        }

        result_raw = await message_repository.create(message_raw)
        await self.repository.update(filter_data={"id": chat_id}, data=chat_to_update)
        crated_new_message = await message_repository.get_message_by_id(
            message_id=result_raw["id"]
        )
        sender_info = {
            "user_id": crated_new_message.user_id,
            "first_name": crated_new_message.first_name,
            "last_name": crated_new_message.last_name,
            "username": crated_new_message.username,
        }
        new_message = {
            "id": crated_new_message.message_id,
            "content": crated_new_message.content,
            "sent_at": str(crated_new_message.sent_at),
            "seen_at": str(crated_new_message.seen_at),
            "is_read": crated_new_message.is_read,
            "reply_to_id": crated_new_message.reply_to_id,
            "reply_to_user_id": crated_new_message.reply_to_user_id,
            "reply_to_content": crated_new_message.reply_to_content,
            "sender_info": sender_info
        }
        return new_message

    async def delete_chat_message(self, message_data: json):
        user_id = message_data.get("user_id")
        message_id = message_data.get("message_id")
        message_repository = MessagesRepository()
        message = await message_repository.get_first(filter_data={"id": message_id})
        if message is not None:
            if message.user_id == int(user_id):
                await message_repository.remove(filter_data={"id": message_id})
            else:
                return None
        return message_id

    async def get_chat_participants(self, chat_id):
        chat = await self.repository.get_first(filter_data={"id": chat_id})
        user_ids = chat.user_ids
        return user_ids

    async def add_message_reaction(self, message_id: int, data: dict):
        message_repository = MessagesRepository()
        message_raw = await message_repository.get_first(filter_data={"id": message_id})

        user_id = data["user_id"]
        reaction = data["reaction"]
        message_reactions = message_raw.reactions
        user_message_reactions = message_reactions.get(user_id)
        if user_message_reactions:
            message_reactions[user_id] = reaction
        else:
            message_reactions = {user_id: reaction}

        raw_message = {
            "reactions": message_reactions,
        }
        result = await message_repository.update(filter_data={"id": message_id}, data=raw_message)
        return result



