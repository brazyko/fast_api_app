from typing import Optional, List
from pydantic.class_validators import validator

from fastapi import Query, HTTPException
from pydantic import BaseModel

from app.config.settings import settings
from app.core.utils.enum import ChatType


class BaseReq(BaseModel):
    pass


class ListReq(BaseReq):
    limit: int = Query(default=settings.BATCH_SIZE, gt=0, description="Limit items")
    offset: int = Query(default=0, ge=0, description="Offset items")

class FindUserReq(BaseReq):
    user: str


class GetUserReq(BaseReq):
    user_id: int

class ChatListReq(ListReq):
    pass

class MessagesListReq(ListReq):
    chat_id: int


class ChatCreateReq(BaseReq):
    chat_type: Optional[str]
    participants: Optional[List[int]]

    @validator("chat_type", pre=True)
    def validate_chat_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            try:
                value in [ChatType.GROUP.value, ChatType.PRIVATE.value]
            except Exception as e:  # noqa
                raise HTTPException(status_code=422, detail=f"Invalid value {value}")
        return value

class ChatGetOrCreateReq(BaseReq):
    receiver_id: int
