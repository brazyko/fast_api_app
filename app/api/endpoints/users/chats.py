from typing import List, Dict

from celery.utils.serialization import jsonify
from fastapi import APIRouter, Depends, HTTPException, Query
from jose import jwt, JWTError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from app.api.schemas.req_schemas import ChatListReq, ChatCreateReq, BaseReq, MessagesListReq, ChatGetOrCreateReq
from app.core.models.users import User
from app.core.services.auth import SECRET_KEY, ALGORITHM
from app.core.services.auth_service import AuthService
from app.core.services.chats import ChatsService
from app.core.services.users import UsersService
from app.extensions.helpers import validate_user

router = APIRouter(prefix="/chats")

active_connections = {}

@router.get("/my-chats")
async def get_my_chats(
    data: ChatListReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):

    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    filter_data = raw_data

    user_id = user_data.id
    filter_data["user_id"] = user_id
    order_data = ("-updated_at", )
    chats_service = ChatsService()
    user_chats = await chats_service.get_my_chats(
        filter_data=filter_data, order_data=order_data
    )
    return user_chats

@router.get("/my-chats/{chat_id}")
async def get_my_chats(
    chat_id: int,
    user_data: User = Depends(AuthService.validate_user),
):

    user_id = user_data.id
    filter_data = {
        "user_id": user_id,
        "chat_id": chat_id,
    }
    chats_service = ChatsService()
    user_chats = await chats_service.get_chat_by_id(
        filter_data=filter_data
    )
    return user_chats

@router.get("/my-chats/messages/")
async def get_my_chats(
    data: MessagesListReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):
    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    filter_data = raw_data
    user_id = user_data.id
    filter_data["user_id"] = user_id

    order_data = ("-sent_at", )
    chats_service = ChatsService()
    messages = await chats_service.get_chat_messages(
        filter_data=filter_data, order_data=order_data
    )
    return messages

@router.post("/create-chat")
async def create_chat(
    data: ChatCreateReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):
    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    data = raw_data

    user_id = user_data.id
    data["user_id"] = user_id
    chats_service = ChatsService()
    user_chats = await chats_service.create_chat(
        data=data
    )
    return user_chats

@router.get("/get-or-create-chat")
async def create_chat(
    data: ChatGetOrCreateReq = Depends(),
    user_data: User = Depends(AuthService.validate_user),
):
    raw_data = data.dict(exclude_none=True)
    # filter data pre processing
    filter_data = raw_data

    user_id = user_data.id
    filter_data["user_id"] = user_id
    chats_service = ChatsService()
    user_chats = await chats_service.get_or_create_chat(
        filter_data=filter_data
    )
    return user_chats

@router.post("/delete-chat")
async def delete_chat(
    data: BaseReq = Depends(),
    user_data: User = Depends(AuthService.validate_user)
):
    raw_data = data.dict(exclude_none=True)
    data = raw_data

    user_id = user_data.id
    data["user_id"] = user_id
    chats_service = ChatsService()
    user_chats = await chats_service.delete_chat(data=data)
    return user_chats


class ConnectionManager:
    def __init__(self):
        # Store connections per user_id
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Add user to the active connections and accept the websocket."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        """Remove user from active connections."""
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user if they are connected."""
        connection = self.active_connections.get(user_id)  # Get the connection for the user
        if connection:
            try:
                await connection.send_json(message)  # Send message directly to the connection
            except RuntimeError as e:
                print(f"Error sending message to {user_id}: {e}")
        else:
            print(f"No active connection found for user {user_id}")

    async def broadcast(self, message: dict, users: List[str]):
        """Broadcast message to all users in the chat who are connected."""
        for user_id in users:
            if user_id in self.active_connections:
                await self.send_personal_message(message, user_id)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Validate token and get user_id
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Validate user from database
    users_service = UsersService()
    user = await users_service.get_first(filter_data={"id": user_id})
    if user is None:
        raise credentials_exception

    await manager.connect(websocket, user_id)

    try:
        while True:
            message_data = await websocket.receive_json()
            event_type = message_data.get("event_type")
            event_data = message_data.get("event_data")

            if event_type == "new_message":
                await handle_new_message(event_data, user_id)
            if event_type == "message_update_content":
                await handle_new_message(event_data, user_id)
            if event_type == "delete_message":
                await delete_message(event_data, user_id)
            elif event_type == "chat_creation":
                await handle_chat_creation(event_data, user_id)
            elif event_type == "message_reaction":
                await handle_message_reaction(event_data, user_id)
            else:
                await manager.send_personal_message({"error": "Invalid event_type"}, user_id)

    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
        manager.disconnect(user_id)


async def handle_new_message(event_data: dict, user_id: str):
    """Handle the 'new_message' event and broadcast it to all chat participants."""
    chat_id = event_data.get("chat_id")
    if not chat_id:
        await manager.send_personal_message({"error": "Chat ID not provided"}, user_id)
        return

    # Fetch the chat details including the participants
    chat_service = ChatsService()
    chat = await chat_service.repository.get_first(filter_data={"id": chat_id})

    if not chat:
        await manager.send_personal_message({"error": "Chat not found"}, user_id)
        return

    # Save the message to the database
    message_raw = await chat_service.send_chat_message(message_data=event_data)
    data_to_broadcast = {"event": "new_message", "data": message_raw }
    # Broadcast the message to all users in the chatв
    participants = [participant for participant in chat.user_ids]  # Assuming chat.user_ids is a list of user IDs
    await manager.broadcast(data_to_broadcast, participants)



async def handle_chat_creation(event_data: dict, user_id: str):
    """Handle the 'chat_creation' event and notify the creator."""
    chat_service = ChatsService()
    new_chat = await chat_service.create_chat(data=event_data)
    await manager.send_personal_message({"message": "Chat created", "chat": new_chat}, user_id)


async def handle_message_reaction(event_data: dict, user_id: str):
    """Handle the 'message_reaction' event and update the message with the new reaction."""
    message_id = event_data.get("message_id")
    user_id = event_data.get("user_id")
    chat_id = event_data.get("chat_id")
    reaction = event_data.get("reaction")  # The reaction (e.g., 'like', 'love', 'haha')
    if not message_id or not reaction:
        await manager.send_personal_message({"error": "Message ID or reaction type not provided"}, user_id)
        return

    # Fetch the chat details including the participants
    chat_service = ChatsService()
    chat = await chat_service.repository.get_first(filter_data={"id": chat_id})

    if not chat:
        await manager.send_personal_message({"error": "Chat not found"}, user_id)
        return

    message = await chat_service.add_message_reaction(message_id=message_id, data={"user_id": user_id, "reaction": reaction})
    # Notify other participants in the chat about the reaction
    participants = [participant for participant in chat.user_ids]
    message_raw = {
        "message_id": message_id,
        "reaction": reaction,
        "user_id": user_id,
    }
    data_to_broadcast = {"event": "message_reaction", "data": message_raw}
    await manager.broadcast(data_to_broadcast, participants)


async def delete_message(event_data: dict, user_id: str):
    """Handle the 'delete_message' event and broadcast it to all chat participants."""
    chat_id = event_data.get("chat_id")
    if not chat_id:
        await manager.send_personal_message({"error": "Chat ID not provided"}, user_id)
        return

    # Fetch the chat details including the participants
    chat_service = ChatsService()
    chat = await chat_service.repository.get_first(filter_data={"id": chat_id})

    if not chat:
        await manager.send_personal_message({"error": "Chat not found"}, user_id)
        return

    # Save the message to the database
    message_raw = await chat_service.delete_chat_message(message_data=event_data)
    data_to_broadcast = {"event": "delete_message", "data": message_raw }
    # Broadcast the message to all users in the chatв
    participants = [participant for participant in chat.user_ids]  # Assuming chat.user_ids is a list of user IDs
    await manager.broadcast(data_to_broadcast, participants)