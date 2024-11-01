from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from app.core.models.mixins import PKMixin

Base = declarative_base()


class Message(Base, PKMixin):
    __tablename__ = "messages"

    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True)

    content = Column(String(2048), default=None)
    sent_at = Column(DateTime, nullable=True, default=None)
    seen_at = Column(DateTime, nullable=True, default=None)
    is_read = Column(Boolean, default=False)
    reply_to_id = Column(Integer, default=None)
    reply_to_content = Column(JSONB, nullable=True)
    reply_to_user_id = Column(Integer, default=None)
    reactions = Column(JSONB, default=dict)
