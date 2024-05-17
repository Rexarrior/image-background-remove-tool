from .db_manager import BaseDatabaseManager
from carvekit.web.database.models import AccountModel, CreditsReservationModel
from carvekit.web.schemas.model_schemas import AccountSchema, AccountSubscriptionSchema
from carvekit.web.utils.db_utils import managed_session
import typing
import sqlalchemy


class AccountManager(BaseDatabaseManager):

    @managed_session
    def create_account_from_pydantic(
        self, account_data: AccountSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> AccountModel:
        account = AccountModel(**account_data.model_dump())
        session.add(account)
        return account

    @managed_session
    def update_account_from_pydantic(
        self,
        account_data: AccountSchema,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> AccountModel:
        account = session.query(AccountModel).filter_by(user_id=account_data.user_id).first()
        if not account:
            raise ValueError("Account not found")
        for key, value in account_data.model_dump().items():
            setattr(account, key, value)
        return account

    @managed_session
    def delete_account_by_id(
        self, user_id: str, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        account = session.query(AccountModel).filter_by(user_id=user_id).first()
        if account:
            session.delete(account)

    @managed_session
    def get_account_by_token(
        self, token: str, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> typing.Optional[int]:
        account = session.query(AccountModel).filter_by(token=token).first()
        return account

    @managed_session
    def reserve_credits(
        self,
        user_id: int,
        credits: int,
        credits_type: str,
        session: typing.Optional[sqlalchemy.orm.Session] = None,
    ) -> int:
        reservation = CreditsReservationModel(
            user_id=user_id, credits=credits, credits_type=credits_type
        )
        session.add(reservation)
        return reservation

    @managed_session
    def deduct_credits_by_reservation_id(
        self, reservation_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
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

    @managed_session
    def cancel_reservation_by_id(
        self, reservation_id: int, session: typing.Optional[sqlalchemy.orm.Session] = None
    ) -> None:
        reservation = session.query(CreditsReservationModel).get(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        session.delete(reservation)

    @managed_session
    def calculate_personal_credits(self, user_token: str, session: typing.Optional[sqlalchemy.orm.Session] = None) -> int:
        account = session.query(AccountModel).filter_by(token=user_token).first()
        reservations = session.query(CreditsReservationModel).filter_by(user_id=account.user_id).all()
        sum_reservations = sum([reservation.credits for reservation in reservations])
        return account.credits - sum_reservations
