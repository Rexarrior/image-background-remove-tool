from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

class AccountSubscriptionSchema(BaseModel):
    user_id: str
    subscription_id: int
    credits: int
    next_renewal: datetime

    class Config:
        orm_mode = True


class AccountSchema(BaseModel):
    user_id: str
    token: str
    credits: int = 0

    class Config:
        orm_mode = True


class CreditsReservationSchema(BaseModel):
    id: int
    user_id: str
    credits: int
    credits_type: str

    class Config:
        orm_mode = True


class SubscriptionSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    duration: Optional[timedelta] = None

    class Config:
        orm_mode = True

