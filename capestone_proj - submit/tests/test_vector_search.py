"""
Unit tests for sliding-window text chunking, dense embeddings, and MMR vector search reranking.
"""

from src.spark_pipeline.embeddings import create_text_chunks, encode_text
from src.rag.vector_search import apply_mmr_reranking, search_news_vector


def test_create_text_chunks():
    long_text = "A" * 700
    chunks = create_text_chunks(long_text, chunk_size=300, overlap=50)
    assert len(chunks) >= 3
    assert len(chunks[0]) == 300


def test_encode_text():
    vec = encode_text("Databricks PySpark Delta Lake Vector RAG")
    assert isinstance(vec, list)
    assert len(vec) == 384


def test_apply_mmr_reranking():
    candidates = [
        {"article_id": "art_1", "similarity_score": 0.95, "title": "Article 1 Chunk 0"},
        {"article_id": "art_1", "similarity_score": 0.94, "title": "Article 1 Chunk 1"},
        {"article_id": "art_2", "similarity_score": 0.88, "title": "Article 2 Chunk 0"},
    ]
    reranked = apply_mmr_reranking(candidates, top_k=2)
    assert len(reranked) == 2
    assert reranked[0]["article_id"] == "art_1"
    assert "reranked_score" in reranked[0]
