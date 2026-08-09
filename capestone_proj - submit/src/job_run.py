"""
Databricks Scheduled Job Runner Entrypoint.
Executes Bronze Ingestion, Silver/Gold Persistence, and Vector Embeddings generation.
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory and parent directory to sys.path
cwd = Path.cwd().resolve()
for p in [str(cwd), str(cwd.parent), str(cwd.parent.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.lakebase import init_db
    from src.spark_pipeline.ingestion import run_bronze_ingestion
    from src.spark_pipeline.transformations import process_silver_gold_and_persist
    from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
    from src.spark_pipeline.cdf_analytics import process_cdf_analytics
except ImportError:
    sys.path.insert(0, os.path.abspath("."))
    from src.lakebase import init_db
    from src.spark_pipeline.ingestion import run_bronze_ingestion
    from src.spark_pipeline.transformations import process_silver_gold_and_persist
    from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
    from src.spark_pipeline.cdf_analytics import process_cdf_analytics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DatabricksJobRunner")


def main():
    logger.info("Starting Databricks Automated Ingestion, PySpark Delta Transformations, CDF Analytics & RAG Job...")

    # Step 1. Ensure Schema Initialized
    init_db()

    # Step 2. Run Bronze Ingestion
    tickers = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"]
    logger.info(f"Ingesting Bronze records for tickers: {tickers}")
    prices, news = run_bronze_ingestion(tickers)
    logger.info(f"Ingested {len(prices)} price snapshots and {len(news)} news articles.")

    # Step 3. Silver & Gold Transformations & Delta Persistence
    logger.info("Executing PySpark Silver & Gold transformations and persisting to Delta Lake & Lakebase...")
    process_silver_gold_and_persist(prices, news)

    # Step 4. Delta Change Data Feed (CDF) Downstream Analytics Pipeline
    logger.info("Processing Delta Change Data Feed (CDF) into downstream analytics tables...")
    cdf_stats = process_cdf_analytics()
    logger.info(f"CDF Analytics processing completed: {cdf_stats}")

    # Step 5. Compute and Store pgvector Multi-Chunk News Embeddings
    logger.info("Computing 384-dimensional dense vectors and storing in Lakebase pgvector table...")
    count = generate_and_store_news_embeddings()
    logger.info(f"SUCCESS: Embedded {count} unstructured news chunks into news_embeddings pgvector index and Delta storage.")


if __name__ == "__main__":
    main()

