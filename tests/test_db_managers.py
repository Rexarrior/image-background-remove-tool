import pytest
from sqlalchemy.orm import sessionmaker
from carvekit.web.database.managers import DbFacade
from carvekit.web.database.engines import SqlliteDbEngine
from carvekit.web.database.models import (SubscriptionModel, AccountSubscriptionModel,
                                          AccountModel, CreditsReservationModel)
from carvekit.web.schemas import (SubscriptionSchema, AccountSubscriptionSchema,
                                  AccountSchema, CreditsReservationSchema)
from datetime import datetime, timedelta

from carvekit.web.schemas.database_credentials import SqliteCredentials


@pytest.fixture
def db_engine():
    db_creds = SqliteCredentials(connection_string="sqlite:///:memory:")
    engine = SqlliteDbEngine(db_creds)
    return engine


@pytest.fixture
def db_manager(db_engine):
    manager = DbFacade(db_engine)
    manager.init_db()
    return manager


@pytest.fixture
def subscription_data():
    return SubscriptionSchema(
        name="Premium",
        id=1,
        description="Premium subscription",
        price=10,
        duration=timedelta(days=30),
    )


@pytest.fixture
def account_subscription_data():
    return AccountSubscriptionSchema(
        user_id="user123",
        subscription_id=1,
        credits=100,
        next_renewal=datetime.now() + timedelta(days=30),
    )

@pytest.fixture
def account_data():
    return AccountSchema(
        token="user token",
        user_id="user123",
        credits=100,
        next_renewal=datetime.now() + timedelta(days=30),
    )



def test_create_subscription(db_manager, subscription_data):
    with db_manager.get_session() as session:
        subscription = db_manager.subscriptions.create_subscription_from_pydantic(subscription_data, session)
        assert subscription.id is not None
        assert subscription.name == subscription_data.name


def test_update_subscription(db_manager, subscription_data):
    with db_manager.get_session() as session:
        subscription = db_manager.subscriptions\
                                .create_subscription_from_pydantic(subscription_data,
                                                                    session)
        updated_data = SubscriptionSchema(
            id=subscription.id,
            name="Updated Premium",
            description="Updated premium subscription",
            price=subscription.price,
            duration=subscription.duration
        )
        updated_subscription = db_manager.subscriptions.update_subscription_from_pydantic(
            updated_data, session
        )
        assert updated_subscription.name == updated_data.name
        assert updated_subscription.price == updated_data.price


def test_delete_subscription(db_manager, subscription_data):
    with db_manager.get_session() as db_session:
        subscription = db_manager.subscriptions.create_subscription_from_pydantic(subscription_data, db_session)
        db_manager.subscriptions.delete_subscription_by_id(subscription.id, db_session)
        deleted_subscription = db_session.query(SubscriptionModel).filter_by(id=subscription.id).first()
        assert deleted_subscription is None

def test_get_subscription_by_id(db_manager, subscription_data):
    with db_manager.get_session() as db_session:
        subscription = db_manager.subscriptions.create_subscription_from_pydantic(subscription_data, db_session)
        retrieved_subscription = db_manager.subscriptions.get_subscription_by_id(subscription.id, db_session)
        assert subscription.id == retrieved_subscription.id
        retrieved_subscription = db_manager.subscriptions.get_subscription_by_id("invalid id", db_session)
        assert retrieved_subscription is None

def test_create_account(db_manager, account_data):
    with db_manager.get_session() as session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, session)
        assert account.user_id is not None
        assert account.token == account_data.token


def test_update_account(db_manager, account_data):
    with db_manager.get_session() as session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, session)
        updated_data = AccountSchema(
            token="updated_token",
            credits=account.credits,
            user_id=account.user_id
        )
        updated_account =db_manager.accounts.update_account_from_pydantic(
             updated_data, session
        )
        assert updated_account.token == updated_data.token
        assert updated_account.credits == updated_data.credits


def test_delete_account(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, db_session)
        db_manager.accounts.delete_account_by_id(account.user_id, db_session)
        deleted_account = db_session.query(AccountModel).filter_by(token=account.token).first()
        assert deleted_account is None


def test_get_account_by_token(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, db_session)
        retrieved_account =db_manager.accounts.get_account_by_token(account.token, db_session)
        assert retrieved_account.user_id == account.user_id
        retrieved_account =db_manager.accounts.get_account_by_token("invalid_token", db_session)
        assert retrieved_account is None


def test_reserve_credits(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, db_session)
        reservation_id =db_manager.accounts.reserve_credits(account.user_id, 500, "personal", db_session)
        assert reservation_id is not None


def test_deduct_credits_by_reservation_id(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account =db_manager.accounts.create_account_from_pydantic(account_data, db_session)
        reservation_id =db_manager.accounts.reserve_credits(account.user_id, 1000, "personal", db_session)
        db_manager.accounts.deduct_credits_by_reservation_id(reservation_id, db_session)
        assert account.credits == account_data.credits - 1000


def test_cancel_reservation(db_manager, account_subscription_data):
    with db_manager.get_session() as db_session:
        reservation =db_manager.accounts.reserve_credits(
            user_id=account_subscription_data.user_id,
            credits=100,
            credits_type="personal",
            session=db_session
        )
        db_manager.accounts.cancel_reservation_by_id(reservation, db_session)
        canceled_reservation = db_session.query(CreditsReservationModel).get(reservation)
        assert canceled_reservation is None
    

@pytest.mark.parametrize("reservations_count", [0, 1, 3, 10])
def test_calculate_personal_credits(db_manager, account_data, reservations_count):
    with db_manager.get_session() as db_session:
        account = db_manager.accounts.create_account_from_pydantic(account_data, db_session)
        reserved_credits = 0
        for _ in range(reservations_count):
            reserved_credits += 10
            db_manager.accounts.reserve_credits(account.user_id, 10, "personal", db_session)
        total = db_manager.accounts.calculate_personal_credits(account.token, db_session)
        assert total == account_data.credits - reserved_credits

def test_calculate_all_account_subscription_credits(db_manager):
    with db_manager.get_session() as db_session:
        account = AccountModel(user_id="user1", token="token1", credits=100)
        subscription1 = SubscriptionModel(name="subscription1", description="description1", price=100, duration=timedelta(days=10))
        subscription2 = SubscriptionModel(name="subscription2", description="description1", price=100, duration=timedelta(days=10))
        db_session.add(subscription1)
        db_session.add(subscription2)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(subscription1)
        db_session.refresh(subscription2)
        acc_subscription1 = AccountSubscriptionModel(user_id="user1", subscription_id=subscription1.id,
                                                     credits=10,
                                                     next_renewal=(datetime.now() + timedelta(days=30)))
        acc_subscription2 = AccountSubscriptionModel(user_id="user1", subscription_id=subscription2.id,
                                                     credits=20,
                                                     next_renewal=(datetime.now() + timedelta(days=30)))
        db_session.add(acc_subscription1)
        db_session.add(acc_subscription2)
        db_session.commit()
        expected_credits_sum = acc_subscription1.credits + acc_subscription2.credits

        result = db_manager.subscriptions.calculate_all_account_subscription_credits("user1", session=db_session)

        # Проверка на соответствие ожидаемому результату
        assert result == expected_credits_sum
        result = db_manager.subscriptions.calculate_all_account_subscription_credits_by_token("token1", session=db_session)
        assert result == expected_credits_sum

