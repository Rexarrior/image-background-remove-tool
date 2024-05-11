from carvekit.web.database.engines.db_engine import AbstractDbEngine
import sqlalchemy


class SqlliteDbEngine(AbstractDbEngine):
    def __init__(self, db_uri: str) -> None:
        self.db_uri = db_uri

    def create_engine(self) -> sqlalchemy.engine.Engine:
        return sqlalchemy.create_engine(self.db_uri)