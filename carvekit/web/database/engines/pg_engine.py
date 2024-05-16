from carvekit.web.schemas.database_credentials import PgCredentials
from carvekit.web.database.engines.db_engine import AbstractDbEngine
import sqlalchemy


class PgEngine(AbstractDbEngine):
    def __init__(self, db_creds: PgCredentials) -> None:
        self.cres = db_creds

    def create_engine(self) -> sqlalchemy.engine.Engine:
        return sqlalchemy.create_engine(
            f'postgresql://{self.creds.user}:{self.creds.password}@{self.creds.host}:{self.creds.port}/{self.creds.database}')