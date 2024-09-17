from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    sender_id = Column(Integer)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    sender = relationship("User", backref="sent_messages")
    chat = relationship("Chat", back_populates="messages")
