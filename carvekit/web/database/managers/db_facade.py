from carvekit.web.database.engines.pg_engine import PgEngine
from carvekit.web.database.engines.sqlite_engine import SqlliteDbEngine
from carvekit.web.database.models.account import AccountModel
from carvekit.web.schemas.config import WebAPIConfig
from carvekit.web.utils.singleton import Singleton
from .db_manager import BaseDatabaseManager
from .accounts_db_manager import AccountManager
from .subscription_db_manager import SubscriptionManager
from carvekit.web.database.engines.db_engine import AbstractDbEngine
from sqlalchemy_utils import database_exists, create_database

class DBSingleton(metaclass=Singleton):
    __metaclass__ = Singleton

    def init_db(self, config: WebAPIConfig) -> None:
        self.engine = self.make_engine(config)
        self.manager = DbFacade(self.engine)
        self.manager.initialize_if_needed()

    def make_engine(self, config):
        if config.db.engine_type == "sqlite":
            engine = SqlliteDbEngine(config.db)
        elif config.db.engine_type == "postgres":
            engine = PgEngine(config.db)
        else:
            raise NotImplementedError
        return engine

    def get_manager(self):
        return self.manager


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
            self.accounts = AccountManager(self.engine, self.Session, db_facade=self)
            self.subscriptions = SubscriptionManager(self.engine, self.Session, db_facade=self)
            return True
        return False

    
    