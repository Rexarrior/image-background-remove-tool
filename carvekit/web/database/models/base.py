from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
Base = declarative_base()


class BaseWithTimestamps(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)