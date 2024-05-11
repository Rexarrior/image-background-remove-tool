from sqlalchemy import (ForeignKey, create_engine, Column,
                        String, Integer, DateTime, Enum)
from .base import BaseWithTimestamps
from datetime import datetime


class CreditsReservationModel(BaseWithTimestamps):
    __tablename__ = 'credits_reservation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String,  ForeignKey('account_credits.user_id'))
    credits = Column(Integer, nullable=False) # reserved credits
    credits_type = Column(Enum('personal', 'subscription', 'enterprise',
                          name='credits_reservation_type'), nullable=False) # type of reserved credits
