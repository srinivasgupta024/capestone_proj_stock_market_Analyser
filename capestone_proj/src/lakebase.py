"""
Lakebase / PostgreSQL database manager for Capstone Project.
Handles connections, schema initialization, read/write SQL operations.
"""

from contextlib import contextmanager
import logging
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

from src.config import LAKEBASE_URL

logger = logging.getLogger(__name__)


def get_connection_url() -> str:
    """Returns the Postgres connection URL from config or secrets."""
    url = LAKEBASE_URL
    if not url:
        # Fallback check via Databricks SDK if in workspace
        try:
            from databricks.sdk import WorkspaceClient
            import base64
            w = WorkspaceClient()
            secret = w.secrets.get_secret(scope="database", key="lakebase-url")
            url = base64.b64decode(secret.value).decode("utf-8")
        except Exception as e:
            logger.warning(f"Could not load Lakebase URL from secrets: {e}")
    return url


@contextmanager
def get_connection():
    """Context manager yielding a raw psycopg2 connection with RealDictCursor."""
    conn = psycopg2.connect(get_connection_url(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def get_engine():
    """Return SQLAlchemy engine for Lakebase."""
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
            # Execute schema statements
            cur.execute(sql_content)
            conn.commit()
    logger.info("Database schema initialized successfully.")
