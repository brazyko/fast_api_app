from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class UserChat(Base):
    __tablename__ = "user_chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    chat_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer))

