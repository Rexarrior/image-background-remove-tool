
from .base import BaseWithTimestamps
from sqlalchemy.sql import func
from sqlalchemy import (ForeignKey, create_engine, Column,
                        String, Integer, DateTime, Interval, Enum)

from datetime import datetime

class SubscriptionModel(BaseWithTimestamps):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    duration = Column(Interval, nullable=False)
