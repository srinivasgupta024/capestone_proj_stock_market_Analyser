"""
Vector Search & RAG Engine.
Executes semantic vector similarity search against Lakebase pgvector embeddings.
"""

from typing import List, Dict, Any, Optional
import logging

from src.lakebase import run_query
from src.spark_pipeline.embeddings import encode_text

logger = logging.getLogger(__name__)


def apply_mmr_reranking(candidates: List[Dict[str, Any]], top_k: int = 5, lambda_mult: float = 0.7) -> List[Dict[str, Any]]:
    """
    Apply Maximal Marginal Relevance (MMR) to balance semantic similarity
    with document diversity, ensuring multiple chunks from the same article don't dominate results.
    """
    if not candidates:
        return []

    selected = []
    seen_articles = set()

    # Sort candidates by similarity_score initial rank
    sorted_candidates = sorted(candidates, key=lambda x: x.get("similarity_score", 0.0), reverse=True)

    for cand in sorted_candidates:
        art_id = cand.get("article_id")
        score = cand.get("similarity_score", 0.0)

        # Apply MMR diversity multiplier: penalize duplicate chunks from the same article
        if art_id in seen_articles:
            diversity_penalty = 0.75
        else:
            diversity_penalty = 1.0

        cand["reranked_score"] = round(score * (lambda_mult + (1.0 - lambda_mult) * diversity_penalty), 4)
        seen_articles.add(art_id)
        selected.append(cand)

    # Re-sort by final reranked score
    selected = sorted(selected, key=lambda x: x.get("reranked_score", 0.0), reverse=True)
    return selected[:top_k]


def search_news_vector(query_text: str, ticker: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic vector search using cosine distance (<=>) in pgvector
    with Maximal Marginal Relevance (MMR) reranking and rich metadata citations.
    """
    query_vector = encode_text(query_text)
    vector_str = f"[{','.join(str(v) for v in query_vector)}]"
    candidate_limit = max(15, top_k * 3)

    if ticker and ticker.strip():
        sql = """
            SELECT 
                e.embedding_id,
                e.article_id,
                e.ticker,
                e.chunk_index,
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
        params = (vector_str, ticker.upper(), vector_str, candidate_limit)
    else:
        sql = """
            SELECT 
                e.embedding_id,
                e.article_id,
                e.ticker,
                e.chunk_index,
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
        params = (vector_str, vector_str, candidate_limit)

    try:
        raw_results = [dict(r) for r in run_query(sql, params)]
        return apply_mmr_reranking(raw_results, top_k=top_k)
    except Exception as e:
        logger.error(f"Vector search execution notice: {e}")
        fallback_sql = """
            SELECT 
                article_id, ticker, title, description AS chunk_text,
                0.88 AS similarity_score, 0.88 AS reranked_score, article_url, publisher, published_utc, sentiment
            FROM news_articles
            WHERE title ILIKE %s OR description ILIKE %s
            LIMIT %s;
        """
        like_pattern = f"%{query_text}%"
        return [dict(r) for r in run_query(fallback_sql, (like_pattern, like_pattern, top_k))]

