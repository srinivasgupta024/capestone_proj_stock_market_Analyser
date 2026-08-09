"""
Lakebase / PostgreSQL database manager for Capstone Project.
Handles connections, schema initialization, read/write SQL operations.
Uses pure-Python pg8000 driver (DB-API 2.0) to guarantee 100% crash-free compatibility with PyTorch & Databricks Serverless.
"""

from contextlib import contextmanager
import logging
from pathlib import Path
from urllib.parse import urlparse
import pg8000.dbapi

from src.config import LAKEBASE_URL

logger = logging.getLogger(__name__)


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


@contextmanager
def get_connection():
    """Yield a raw pg8000 DB-API connection."""
    url_str = get_connection_url()
    u = urlparse(url_str)
    conn = pg8000.dbapi.connect(
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
        database=u.path.lstrip('/'),
        ssl_context=True
    )
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_engine():
    """Return SQLAlchemy engine for Lakebase using pg8000 dialect."""
    from sqlalchemy import create_engine
    url_str = get_connection_url()
    if url_str.startswith("postgresql://"):
        url_str = url_str.replace("postgresql://", "postgresql+pg8000://", 1)
    return create_engine(url_str)


def run_query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Execute a read query and return rows as list of dicts."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        return []


def run_write(sql: str, params: tuple | dict | None = None) -> int:
    """Execute INSERT/UPDATE/DELETE query and return affected row count."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.rowcount if hasattr(cur, "rowcount") and cur.rowcount >= 0 else 1


def init_db():
    """Initialize database tables using sql/01_schema.sql or candidate paths if needed."""
    base_dir = Path(__file__).resolve().parent.parent
    candidate_paths = [
        base_dir / "sql" / "01_schema.sql",
        base_dir / "01_schema.sql",
        Path.cwd() / "sql" / "01_schema.sql",
        Path.cwd() / "01_schema.sql",
        Path("sql/01_schema.sql"),
        Path("01_schema.sql"),
    ]
    
    schema_path = None
    for p in candidate_paths:
        if p.exists():
            schema_path = p
            break

    if not schema_path:
        logger.warning("Schema file 01_schema.sql not found in candidate paths.")
        return

    sql_content = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
    logger.info(f"Database schema initialized successfully from {schema_path}.")

