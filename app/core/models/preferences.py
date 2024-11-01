from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

from app.core.models.mixins import PKMixin

Base = declarative_base()


class Preferences(Base, PKMixin):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    color_scheme = Column(String, index=True)
    language = Column(String, default='En')
    notifications_on = Column(Boolean, default=True)
