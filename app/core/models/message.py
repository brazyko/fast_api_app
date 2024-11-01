from sqlalchemy import Column, String, Integer, DateTime, Numeric, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from app.core.models.mixins import PKMixin

Base = declarative_base()


class UserMessage(Base):
    __tablename__ = "user_messages"

    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, nullable=True, default=None)
    seen_at = Column(DateTime, nullable=True, default=None)
    content = Column(String(2048), default=None)
    reply_to = Column(Integer, default=None)
