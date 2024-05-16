from .db_manager import BaseDatabaseManager
from carvekit.web.database.models import SubscriptionModel, AccountSubscriptionModel
from carvekit.web.schemas import AccountSubscriptionSchema, SubscriptionSchema
import typing
from datetime import datetime, timedelta
from pydantic import BaseModel
import sqlalchemy


class SubscriptionManager(BaseDatabaseManager):
    def create_subscription_from_pydantic(
        self, subscription_data: SubscriptionSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> SubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscription = SubscriptionModel(**subscription_data.model_dump())
            session.add(subscription)
            session.commit()
            return subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def get_subscription_by_id(self, subscription_id: int,
                               session: typing.Optional[sqlalchemy.orm.Session] = None) -> SubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscription = session.query(
                SubscriptionModel).get(subscription_id)
            if not subscription:
                return None
            return subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def get_account_subscriptions_by_user_id(self, user_id: str,
                                             session: typing.Optional[sqlalchemy.orm.Session] = None) -> typing.List[AccountSubscriptionModel]:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscriptions = session.query(
                AccountSubscriptionModel).filter_by(user_id=user_id).all()
            return subscriptions
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def update_subscription_from_pydantic(
        self,
        subscription_data: SubscriptionSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> SubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscription = session.query(SubscriptionModel).filter_by(
                id=subscription_data.id).first()
            if not subscription:
                raise ValueError("Subscription not found")
            for key, value in subscription_data.model_dump().items():
                setattr(subscription, key, value)
            session.commit()
            return subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def delete_subscription_by_id(
        self, subscription_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscription = session.query(
                SubscriptionModel).get(subscription_id)
            if subscription:
                session.delete(subscription)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def create_account_subscription_from_pydantic(
        self, account_subscription_data: AccountSubscriptionSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> AccountSubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            account_subscription = AccountSubscriptionModel(
                **account_subscription_data.model_dump())
            session.add(account_subscription)
            session.commit()
            return account_subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def get_account_subscription_by_id(self, user_id: str, subscription_id: int,
                                       session: typing.Optional[sqlalchemy.orm.Session] = None) -> AccountSubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            account_subscription = session.query(AccountSubscriptionModel).filter_by(
                user_id=user_id, subscription_id=subscription_id
            ).first()
            if not account_subscription:
                return None
            return account_subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def update_account_subscription_from_pydantic(
        self,
        user_id: str,
        subscription_id: int,
        account_subscription_data: AccountSubscriptionSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> AccountSubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            account_subscription = session.query(AccountSubscriptionModel).filter_by(
                user_id=user_id, subscription_id=subscription_id
            ).first()
            if not account_subscription:
                raise ValueError("Account subscription not found")
            for key, value in account_subscription_data.model_dump().items():
                setattr(account_subscription, key, value)
            session.commit()
            return account_subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def delete_account_subscription_by_id(
        self, user_id: str, subscription_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            account_subscription = session.query(AccountSubscriptionModel).filter_by(
                user_id=user_id, subscription_id=subscription_id
            ).first()
            if account_subscription:
                session.delete(account_subscription)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def renew_subscription(
        self, subscription_id: int, renewal_period: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> SubscriptionModel:
        session, is_session_managed = (
            session, False) or (self.get_session(), True)
        try:
            subscription = session.query(
                SubscriptionModel).get(subscription_id)
            if not subscription:
                raise ValueError("Subscription not found")
            subscription.next_renewal += timedelta(days=renewal_period)
            # Restore credits
            subscription.credits = subscription.initial_credits
            session.commit()
            return subscription
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def calculate_subscription_credits(self, subscription_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None) -> int:
        subscription = self.get_subscription_by_id(
            subscription_id, session=session)
        if not subscription:
            raise ValueError("Subscription not found")
        return subscription.credits

    def calculate_all_account_subscription_credits(self, user_id: str, session: typing.Optional[sqlalchemy.orm.Session] = None) -> int:
        account_subscriptions = self.get_account_subscriptions_by_user_id(
            user_id, session=session)
        if not account_subscriptions:
            raise ValueError("Account subscriptions not found")
        return sum(subscription.credits for subscription in account_subscriptions)
   
    def calculate_all_account_subscription_credits_by_token(self, token: str, session: typing.Optional[sqlalchemy.orm.Session] = None) -> int:
        account = self.db_facade.accounts.get_account_by_token(token, session=session)
        if not account:
            raise ValueError("Account not found")
        return self.calculate_all_account_subscription_credits(account.user_id, session=session)
