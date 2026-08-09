"""
Lakebase / PostgreSQL database manager for Capstone Project.
Handles connections, schema initialization, read/write SQL operations.
Supports both psycopg2 and pure-Python pg8000 drivers.
"""

from contextlib import contextmanager
import logging
from pathlib import Path
from urllib.parse import urlparse

from src.config import LAKEBASE_URL

logger = logging.getLogger(__name__)

# Primary driver selection: psycopg2 with fallback to pure-Python pg8000
USE_PG8000 = False
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception as e:
    logger.info(f"psycopg2 unavailable ({e}), defaulting to pure-Python pg8000 driver.")
    USE_PG8000 = True


def get_connection_url() -> str:
    """Returns the Postgres connection URL from config or secrets."""
    url = LAKEBASE_URL
    if not url:
        try:
            from databricks.sdk import WorkspaceClient
            import base64
            w = WorkspaceClient()
            secret = w.secrets.get_secret(scope="database", key="lakebase-url")
            url = base64.b64decode(secret.value).decode("utf-8")
        except Exception as e:
            logger.warning(f"Could not load Lakebase URL from secrets: {e}")
    return url


class Pg8000CursorWrapper:
    """Cursor wrapper for pg8000 to match psycopg2 DictCursor API."""
    def __init__(self, conn):
        self.conn = conn
        self.last_rows = []
        self.rowcount = 0

    def execute(self, sql: str, params: tuple | dict | None = None):
        param_list = list(params) if isinstance(params, (tuple, list)) else ([params] if params is not None else [])
        res = self.conn.run(sql, *param_list)
        if res and hasattr(self.conn, "columns") and self.conn.columns:
            cols = [c["name"] for c in self.conn.columns]
            self.last_rows = [dict(zip(cols, row)) for row in res]
            self.rowcount = len(res)
        else:
            self.last_rows = []
            self.rowcount = 0

    def fetchall(self):
        return self.last_rows


class Pg8000ConnWrapper:
    """Connection wrapper for pg8000."""
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return Pg8000CursorWrapper(self.conn)

    def commit(self):
        pass

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


@contextmanager
def get_connection():
    """Context manager yielding a database connection supporting DictCursor."""
    url_str = get_connection_url()

    if not USE_PG8000:
        try:
            conn = psycopg2.connect(url_str, cursor_factory=RealDictCursor)
            try:
                yield conn
            finally:
                conn.close()
            return
        except Exception as e:
            logger.warning(f"psycopg2 connection attempt failed: {e}. Falling back to pg8000.")

    # Fallback / Pure Python pg8000 driver
    import pg8000.native
    u = urlparse(url_str)
    native_conn = pg8000.native.Connection(
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
        database=u.path.lstrip('/'),
        ssl_context=True
    )
    wrapper = Pg8000ConnWrapper(native_conn)
    try:
        yield wrapper
    finally:
        wrapper.close()


def get_engine():
    """Return SQLAlchemy engine for Lakebase."""
    from sqlalchemy import create_engine
    return create_engine(get_connection_url())


def run_query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Execute a read query and return rows as list of dicts."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def run_write(sql: str, params: tuple | dict | None = None) -> int:
    """Execute INSERT/UPDATE/DELETE query and return affected row count."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def init_db():
    """Initialize database tables using sql/01_schema.sql if needed."""
    schema_path = Path(__file__).resolve().parent.parent / "sql" / "01_schema.sql"
    if not schema_path.exists():
        logger.warning(f"Schema file not found at {schema_path}")
        return

    sql_content = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)
            conn.commit()
    logger.info("Database schema initialized successfully.")
