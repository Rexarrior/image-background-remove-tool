import sqlalchemy
from sqlalchemy.orm import sessionmaker
from carvekit.web.database.engines.db_engine import AbstractDbEngine
from carvekit.web.database.models.base import Base
import typing

class BaseDatabaseManager:
    def __init__(self,
                 db_engine: AbstractDbEngine| sqlalchemy.engine.Engine,
                 session_maker = None
                 ) -> None:
        if isinstance(db_engine, AbstractDbEngine):
            self.engine: sqlalchemy.engine.Engine = db_engine.create_engine()
            self.Session: sqlalchemy.orm.sessionmaker = sessionmaker(bind=self.engine)
        elif isinstance(db_engine, sqlalchemy.engine.Engine) and session_maker:
            self.engine: sqlalchemy.engine.Engine = db_engine
            self.Session: sqlalchemy.orm.sessionmaker = sessionmaker(bind=self.engine)
        else:
            raise ValueError("Invalid db_engine or session_maker")
    
    def get_session(self) -> sqlalchemy.orm.Session:
        return self.Session()

    def close_session(self, session: sqlalchemy.orm.Session) -> None:
        session.close()

    def rollback_session(self, session: sqlalchemy.orm.Session) -> None:
        session.rollback()
        session.close()

    def init_db(self):
        Base.metadata.create_all(self.engine)
  

