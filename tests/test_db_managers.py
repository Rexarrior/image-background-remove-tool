import pytest
from sqlalchemy.orm import sessionmaker
from carvekit.web.database.managers import DbFacade
from carvekit.web.database.engines import SqlliteDbEngine
from carvekit.web.database.models import (SubscriptionModel, AccountSubscriptionModel,
                                          AccountModel, CreditsReservationModel)
from carvekit.web.schemas import (SubscriptionSchema, AccountSubscriptionSchema,
                                  AccountSchema, CreditsReservationSchema)
from datetime import datetime, timedelta


@pytest.fixture
def db_engine():
    db_uri = "sqlite:///:memory:"
    engine = SqlliteDbEngine(db_uri)
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
        subscription = db_manager.subscriptions_manager.create_subscription_from_pydantic(subscription_data, session)
        assert subscription.id is not None
        assert subscription.name == subscription_data.name


def test_update_subscription(db_manager, subscription_data):
    with db_manager.get_session() as session:
        subscription = db_manager.subscriptions_manager\
                                .create_subscription_from_pydantic(subscription_data,
                                                                    session)
        updated_data = SubscriptionSchema(
            id=subscription.id,
            name="Updated Premium",
            description="Updated premium subscription",
            price=subscription.price,
            duration=subscription.duration
        )
        updated_subscription = db_manager.subscriptions_manager.update_subscription_from_pydantic(
            updated_data, session
        )
        assert updated_subscription.name == updated_data.name
        assert updated_subscription.price == updated_data.price


def test_delete_subscription(db_manager, subscription_data):
    with db_manager.get_session() as db_session:
        subscription = db_manager.subscriptions_manager.create_subscription_from_pydantic(subscription_data, db_session)
        db_manager.subscriptions_manager.delete_subscription_by_id(subscription.id, db_session)
        deleted_subscription = db_session.query(SubscriptionModel).filter_by(id=subscription.id).first()
        assert deleted_subscription is None


def test_create_account(db_manager, account_data):
    with db_manager.get_session() as session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, session)
        assert account.user_id is not None
        assert account.token == account_data.token


def test_update_account(db_manager, account_data):
    with db_manager.get_session() as session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, session)
        updated_data = AccountSchema(
            token="updated_token",
            credits=account.credits,
            user_id=account.user_id
        )
        updated_account = db_manager.credits_manager.update_account_from_pydantic(
             updated_data, session
        )
        assert updated_account.token == updated_data.token
        assert updated_account.credits == updated_data.credits


def test_delete_account(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, db_session)
        db_manager.credits_manager.delete_account_by_id(account.user_id, db_session)
        deleted_account = db_session.query(AccountModel).filter_by(token=account.token).first()
        assert deleted_account is None


def test_get_credits_by_token(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, db_session)
        credits = db_manager.credits_manager.get_credits_by_token(account.token, db_session)
        assert credits == account_data.credits


def test_reserve_credits(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, db_session)
        reservation_id = db_manager.credits_manager.reserve_credits(account.user_id, 500, "personal", db_session)
        assert reservation_id is not None


def test_deduct_credits_by_reservation_id(db_manager, account_data):
    with db_manager.get_session() as db_session:
        account = db_manager.credits_manager.create_account_from_pydantic(account_data, db_session)
        reservation_id = db_manager.credits_manager.reserve_credits(account.user_id, 1000, "personal", db_session)
        db_manager.credits_manager.deduct_credits_by_reservation_id(reservation_id, db_session)
        assert account.credits == account_data.credits - 1000


def test_cancel_reservation(db_manager, account_subscription_data):
    with db_manager.get_session() as db_session:
        reservation = db_manager.credits_manager.reserve_credits(
            user_id=account_subscription_data.user_id,
            credits=100,
            credits_type="personal",
            session=db_session
        )
        db_manager.credits_manager.cancel_reservation_by_id(reservation, db_session)
        canceled_reservation = db_session.query(CreditsReservationModel).get(reservation)
        assert canceled_reservation is None