from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    photo = Column(String, nullable=True)
    chat_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_ids = Column(ARRAY(Integer))
    last_message = Column(String(2048), default=None)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)