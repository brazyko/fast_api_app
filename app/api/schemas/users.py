from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: Optional[str]
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
