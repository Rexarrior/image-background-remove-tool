from carvekit.web.database.engines.db_engine import AbstractDbEngine
import sqlalchemy

from carvekit.web.schemas.database_credentials import SqliteCredentials


class SqlliteDbEngine(AbstractDbEngine):
    def __init__(self, sqlite_creds: SqliteCredentials) -> None:
        self.db_uri = sqlite_creds.connection_string

    def create_engine(self) -> sqlalchemy.engine.Engine:
        return sqlalchemy.create_engine(self.db_uri)