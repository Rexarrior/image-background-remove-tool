from .db_manager import BaseDatabaseManager
from .credits_db_manager import CreditsManager
from .subscription_db_manager import SubscriptionManager
from carvekit.web.database.engines.db_engine import AbstractDbEngine

class DbFacade(BaseDatabaseManager):
    def __init__(self, db_engine: AbstractDbEngine) -> None:
        super().__init__(db_engine)
        self.credits_manager = CreditsManager(self.engine, self.Session)
        self.subscriptions_manager = SubscriptionManager(self.engine, self.Session)
    
