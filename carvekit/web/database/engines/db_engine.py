import abc
import sqlalchemy


class AbstractDbEngine(abc.ABC):

    @abc.abstractmethod
    def create_engine(self) -> sqlalchemy.engine.Engine:
        pass
