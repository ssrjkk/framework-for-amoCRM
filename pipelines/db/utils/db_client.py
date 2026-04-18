import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import DB_DSN
import logging
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBClient:
    def __init__(self, dsn: str = None):
        self.dsn = dsn or DB_DSN
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        self.pool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=self.dsn)

    @contextmanager
    def connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def cursor(self, dict_cursor: bool = False):
        with self.connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(self, query: str, params: tuple = None, fetch: bool = True):
        with self.cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount

    def execute_one(self, query: str, params: tuple = None):
        with self.cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_raw(self, query: str, params: tuple = None, fetch: bool = True):
        with self.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount

    def get_value(self, query: str, params: tuple = None):
        result = self.execute_one(query, params)
        if result:
            return list(result.values())[0]
        return None

    def table_exists(self, table_name: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """
        return self.get_value(query, (table_name,))

    def get_columns(self, table_name: str) -> list:
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute(query, (table_name,))

    def row_count(self, table_name: str) -> int:
        query = f"SELECT COUNT(*) FROM {table_name}"
        return self.get_value(query)

    def close(self):
        if self.pool:
            self.pool.closeall()


@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def db_transaction(db_client):
    with db_client.connection() as conn:
        yield conn
        conn.rollback()
