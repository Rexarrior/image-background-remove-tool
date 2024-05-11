from sqlalchemy import (ForeignKey, create_engine, Column,
                        String, Integer, DateTime, Enum)
from sqlalchemy.sql import func
from datetime import datetime
from .base import BaseWithTimestamps


class AccountModel(BaseWithTimestamps):
    __tablename__ = 'account_credits'

    user_id = Column(String, primary_key=True, unique=True) # TODO foreing key to user model
    token = Column(String, unique=True) # API key

    credits = Column(Integer, nullable=False) # personal credits

    # Should be in organization credits model
    # credits_enterprice = Column(Integer, nullable=False)

