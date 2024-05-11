from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from .base import BaseWithTimestamps
from datetime import datetime


class AccountSubscriptionModel(BaseWithTimestamps):
    __tablename__ = 'account_subscriptions'

    user_id = Column(String, ForeignKey('account_credits.user_id'), primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'), primary_key=True)
    credits = Column(Integer, nullable=False)
    next_renewal = Column(DateTime, nullable=False)
  