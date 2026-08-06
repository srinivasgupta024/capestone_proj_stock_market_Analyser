"""
Vector Search & RAG Engine.
Executes semantic vector similarity search against Lakebase pgvector embeddings.
"""

from typing import List, Dict, Any, Optional
import logging

from src.lakebase import run_query
from src.spark_pipeline.embeddings import encode_text

logger = logging.getLogger(__name__)


def search_news_vector(query_text: str, ticker: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic vector search using cosine distance (<=>) in pgvector.
    Returns top-k most semantically relevant news chunks.
    """
    query_vector = encode_text(query_text)
    vector_str = f"[{','.join(str(v) for v in query_vector)}]"

    if ticker and ticker.strip():
        sql = """
            SELECT 
                e.embedding_id,
                e.article_id,
                e.ticker,
                e.chunk_text,
                1 - (e.embedding <=> %s::vector) AS similarity_score,
                a.title,
                a.article_url,
                a.publisher,
                a.published_utc,
                a.sentiment
            FROM news_embeddings e
            JOIN news_articles a ON e.article_id = a.article_id
            WHERE e.ticker = %s
            ORDER BY e.embedding <=> %s::vector ASC
            LIMIT %s;
        """
        params = (vector_str, ticker.upper(), vector_str, top_k)
    else:
        sql = """
            SELECT 
                e.embedding_id,
                e.article_id,
                e.ticker,
                e.chunk_text,
                1 - (e.embedding <=> %s::vector) AS similarity_score,
                a.title,
                a.article_url,
                a.publisher,
                a.published_utc,
                a.sentiment
            FROM news_embeddings e
            JOIN news_articles a ON e.article_id = a.article_id
            ORDER BY e.embedding <=> %s::vector ASC
            LIMIT %s;
        """
        params = (vector_str, vector_str, top_k)

    try:
        results = run_query(sql, params)
        return [dict(r) for r in results]
    except Exception as e:
        logger.error(f"Vector search execution error: {e}")
        # Fallback to text matching if pgvector extension query fails
        fallback_sql = """
            SELECT 
                article_id, ticker, title, description AS chunk_text,
                0.85 AS similarity_score, article_url, publisher, published_utc, sentiment
            FROM news_articles
            WHERE title ILIKE %s OR description ILIKE %s
            LIMIT %s;
        """
        like_pattern = f"%{query_text}%"
        return [dict(r) for r in run_query(fallback_sql, (like_pattern, like_pattern, top_k))]
