"""
Databricks Scheduled Job Runner Entrypoint.
Executes Bronze Ingestion, Silver/Gold Persistence, and Vector Embeddings generation.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to sys.path safely (supports both standard python and Databricks IPykernel)
if "__file__" in globals():
    project_root = Path(__file__).resolve().parent.parent
else:
    project_root = Path.cwd()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from src.lakebase import init_db
from src.spark_pipeline.ingestion import run_bronze_ingestion
from src.spark_pipeline.transformations import process_silver_gold_and_persist
from src.spark_pipeline.embeddings import generate_and_store_news_embeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DatabricksJobRunner")


def main():
    logger.info("Starting Databricks Automated Ingestion & RAG Job...")

    # Step 1. Ensure Schema Initialized
    init_db()

    # Step 2. Run Bronze Ingestion
    tickers = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"]
    logger.info(f"Ingesting Bronze records for tickers: {tickers}")
    prices, news = run_bronze_ingestion(tickers)
    logger.info(f"Ingested {len(prices)} price snapshots and {len(news)} news articles.")

    # Step 3. Silver & Gold Transformations & Persistence
    logger.info("Executing Silver & Gold transformations and persisting to Lakebase...")
    process_silver_gold_and_persist(prices, news)

    # Step 4. Compute and Store pgvector News Embeddings
    logger.info("Computing 384-dimensional dense vectors and storing in Lakebase pgvector table...")
    count = generate_and_store_news_embeddings()
    logger.info(f"SUCCESS: Embedded {count} news articles into news_embeddings pgvector index.")


if __name__ == "__main__":
    main()
