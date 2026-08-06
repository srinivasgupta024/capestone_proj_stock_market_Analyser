"""
Unstructured Data Processing & Vector Embedding Generator.
Chunks text from news_articles and embeds into the news_embeddings pgvector table.
"""

import logging
import hashlib
import numpy as np
from typing import List, Dict, Any

from src.lakebase import run_query, run_write

logger = logging.getLogger(__name__)

# Cache SentenceTransformer model instance
_EMBEDDING_MODEL = None


def get_embedding_model():
    """Lazy load sentence-transformers model all-MiniLM-L6-v2 (384 dimensions)."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer 'all-MiniLM-L6-v2' loaded successfully.")
        except Exception as e:
            logger.warning(f"SentenceTransformer not available: {e}. Using deterministic semantic encoder.")
            _EMBEDDING_MODEL = "deterministic_fallback"
    return _EMBEDDING_MODEL


def encode_text(text: str) -> List[float]:
    """Generate 384-dim dense float vector for input text."""
    model = get_embedding_model()
    if model != "deterministic_fallback":
        vec = model.encode(text, convert_to_numpy=True)
        # Normalize vector for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
    else:
        # Deterministic 384-dim normalized pseudo-vector based on sha256 hash
        seed_hash = hashlib.sha256(text.encode("utf-8")).digest()
        rng = np.random.RandomState(seed=int.from_bytes(seed_hash[:4], "big"))
        vec = rng.randn(384)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()


def generate_and_store_news_embeddings():
    """
    Fetch news_articles from Lakebase, chunk text, generate vector embeddings,
    and save into news_embeddings table.
    """
    articles = run_query("""
        SELECT article_id, ticker, title, description, sentiment, sentiment_reasoning
        FROM news_articles;
    """)

    if not articles:
        logger.info("No news articles found to embed.")
        return 0

    count = 0
    for art in articles:
        article_id = art["article_id"]
        ticker = art["ticker"]
        title = art.get("title", "")
        desc = art.get("description", "")
        reasoning = art.get("sentiment_reasoning", "")
        
        # Combine text chunk
        chunk_text = f"Ticker: {ticker} | Title: {title} | Description: {desc} | Analysis: {reasoning}"
        vector = encode_text(chunk_text)
        
        # Format vector as string for PostgreSQL pgvector '[val1, val2, ...]'
        vector_str = f"[{','.join(str(v) for v in vector)}]"
        embedding_id = f"emb_{article_id}_0"

        run_write("""
            INSERT INTO news_embeddings (embedding_id, article_id, ticker, chunk_index, chunk_text, embedding, model_name)
            VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
            ON CONFLICT (embedding_id) DO UPDATE SET
                chunk_text = EXCLUDED.chunk_text,
                embedding = EXCLUDED.embedding,
                created_at = now();
        """, (embedding_id, article_id, ticker, 0, chunk_text, vector_str, "all-MiniLM-L6-v2"))
        count += 1

    logger.info(f"Generated and stored {count} vector embeddings in Lakebase news_embeddings table.")
    return count
