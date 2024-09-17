from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    photo = Column(String, nullable=True)
    chat_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    users = relationship("User", secondary="user_chats", back_populates="chats")
    admins = relationship("User", secondary="admin_chats", back_populates="admin_of_chats")
    messages = relationship("Message", back_populates="chat")
