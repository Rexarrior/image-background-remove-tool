
from pydantic import BaseModel


class DatabaseCredentials(BaseModel):
    engine_type: str

class PgCredentials(DatabaseCredentials):
    """Postgres credentials"""
    engine_type: str = "postgresql"

    host: str = "localhost"
    """Postgres host"""
    port: int = 5432
    """Postgres port"""
    database: str = "carvekit"
    """Postgres database"""
    user: str = "postgres"
    """Postgres user"""
    password: str = ""
    """Postgres password"""

class SqliteCredentials(DatabaseCredentials):
    engine_type: str = "sqlite"

    connection_string: str = "sqlite:///:memory:"