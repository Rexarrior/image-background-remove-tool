from .db_manager import BaseDatabaseManager
from carvekit.web.database.models  import AccountModel, CreditsReservationModel
from carvekit.web.schemas.model_schemas import AccountSchema, AccountSubscriptionSchema 
import typing
import sqlalchemy


class CreditsManager(BaseDatabaseManager):
    def create_account_from_pydantic(
        self, account_data: AccountSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> AccountModel:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            account = AccountModel(**account_data.model_dump())
            session.add(account)
            session.commit()
            return account
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def update_account_from_pydantic(
        self,
        account_data: AccountSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> AccountModel:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            account = session.query(AccountModel).filter_by(user_id=account_data.user_id).first()
            if not account:
                raise ValueError("Account not found")
            for key, value in account_data.model_dump().items():
                setattr(account, key, value)
            session.commit()
            return account
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def delete_account_by_id(
        self, user_id: str, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            account = session.query(AccountModel).filter_by(user_id=user_id).first()
            if account:
                session.delete(account)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def get_credits_by_token(
        self, token: str, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> typing.Optional[int]:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            account = session.query(AccountModel).filter_by(token=token).first()
            if account:
                return account.credits
            return None
        finally:
            if session and is_session_managed:
                session.close()

    def reserve_credits(
        self,
        user_id: int,
        credits: int,
        credits_type: str,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> int:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            reservation = CreditsReservationModel(
                user_id=user_id, credits=credits, credits_type=credits_type
            )
            session.add(reservation)
            session.commit()
            return reservation.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    def deduct_credits_by_reservation_id(
        self, reservation_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            reservation = session.query(CreditsReservationModel).get(reservation_id)
            if not reservation:
                raise ValueError("Reservation not found")
            account = session.query(AccountModel).filter_by(
                user_id=reservation.user_id
            ).first()
            if not account:
                raise ValueError("Account not found")
            if reservation.credits_type == "personal":
                account.credits -= reservation.credits
            elif reservation.credits_type == "subscription":
                account.credits_subscription -= reservation.credits
            # Add other types if needed
            session.delete(reservation)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()

    
    def cancel_reservation_by_id(
        self, reservation_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        session, is_session_managed = (session, False) or (self.get_session(), True)
        try:
            reservation = session.query(CreditsReservationModel).get(reservation_id)
            if not reservation:
                raise ValueError("Reservation not found")
            session.delete(reservation)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session and is_session_managed:
                session.close()