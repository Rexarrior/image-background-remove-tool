from .db_manager import BaseDatabaseManager
from .accounts_db_manager import AccountManager
from .subscription_db_manager import SubscriptionManager
from carvekit.web.database.engines.db_engine import AbstractDbEngine

class DbFacade(BaseDatabaseManager):
    def __init__(self, db_engine: AbstractDbEngine) -> None:
        super().__init__(db_engine)
        self.accounts = AccountManager(self.engine, self.Session)
        self.subscriptions = SubscriptionManager(self.engine, self.Session)
    
