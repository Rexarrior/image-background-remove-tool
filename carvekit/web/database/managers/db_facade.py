from carvekit.web.database.engines.pg_engine import PgEngine
from carvekit.web.database.engines.sqlite_engine import SqlliteDbEngine
from carvekit.web.database.models.account import AccountModel
from carvekit.web.schemas.config import WebAPIConfig
from .db_manager import BaseDatabaseManager
from .accounts_db_manager import AccountManager
from .subscription_db_manager import SubscriptionManager
from carvekit.web.database.engines.db_engine import AbstractDbEngine


class DbFacade(BaseDatabaseManager):
    def __init__(self, db_engine: AbstractDbEngine) -> None:
        super().__init__(db_engine, db_facade=self)
        self.accounts = AccountManager(self.engine, self.Session, db_facade=self)
        self.subscriptions = SubscriptionManager(self.engine, self.Session, db_facade=self)
        
    def check_initialized(self):
        try:
            with self.get_session() as session:
                session.query(AccountModel).first()
            return True
        except Exception as ex:
            return False


    def initialize_if_needed(self):
        if not self.check_initialized():
            self.init_db()
            self._delete_test_acc()
            self._create_test_acc()
            self._delete_test_acc()
            return True
        return False

    def _create_test_acc(self):
        with self.get_session() as session:
            model = AccountModel(user_id="test_tmp_uid", token="123", credits=0,)
            session.add(model)
            session.commit()

    def _delete_test_acc(self):
        with self.get_session() as session:
            model = session.query(AccountModel).filter_by(user_id="test_tmp_uid").first()
            if model:
                session.delete(model)
                session.commit()
    
    @classmethod
    def make_db_facade(cls, config: WebAPIConfig) -> None:
        engine = cls.make_engine(config)
        manager = DbFacade(engine)
        manager.initialize_if_needed()
        return manager

    @classmethod
    def make_engine(cls, config):
        if config.db.engine_type == "sqlite":
            engine = SqlliteDbEngine(config.db)
        elif config.db.engine_type == "postgres":
            engine = PgEngine(config.db)
        else:
            raise NotImplementedError
        return engine
    
    