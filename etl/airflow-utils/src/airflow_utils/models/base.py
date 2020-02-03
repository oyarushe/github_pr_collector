"""Base classes for SQLAlchemy models."""
from airflow.hooks.postgres_hook import PostgresHook
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()  # Base class for SQLAlchemy model


class DB:
    """Class for common methods."""

    def __init__(self, conn_id):
        """
        Initialization.

        :param conn_id: Postgres connection ID
        """
        self._session = None
        self._engine = None
        self.conn_id = conn_id

    @property
    def engine(self):
        """Get PostgreSQL engine."""
        if self._engine is None:
            conn_uri = PostgresHook(postgres_conn_id=self.conn_id).get_uri()

            self._engine = create_engine(conn_uri, pool_pre_ping=True)

        return self._engine

    @property
    def session(self):
        """Get session."""
        if self._session is None:
            session_class = sessionmaker(bind=self.engine)
            self._session = session_class(autocommit=False)

        return self._session
