"""
PySpark Ingestion Module (Bronze Layer ETL).
Fetches raw market and news data and ingests into PySpark DataFrames.
"""

from typing import List, Dict, Any
import logging
from src.massive_client import MassiveClient

logger = logging.getLogger(__name__)


def create_spark_session():
    """Build or retrieve a PySpark SparkSession."""
    try:
        from pyspark.sql import SparkSession
        return (
            SparkSession.builder
            .appName("Capstone_Bronze_Ingestion")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .getOrCreate()
        )
    except Exception as e:
        logger.warning(f"Native SparkSession unavailable in local standalone mode: {e}")
        return None


def run_bronze_ingestion(tickers: List[str] = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "TSLA"]):
    """
    Bronze Layer: Ingest raw REST API payloads from Massive API,
    convert to PySpark DataFrame / pandas DataFrame, and write to Lakebase.
    """
    client = MassiveClient()
    news_records = []
    price_records = []

    for t in tickers:
        quote = client.get_ticker_quote(t)
        price_records.append(quote)
        
        articles = client.get_news(t, limit=5)
        news_records.extend(articles)

    spark = create_spark_session()
    if spark:
        # Ingest into PySpark DataFrames
        df_prices_bronze = spark.createDataFrame(price_records)
        df_news_bronze = spark.createDataFrame(news_records)
        
        logger.info("PySpark Bronze DataFrames Created:")
        df_prices_bronze.show(5)
        df_news_bronze.show(5)

    return price_records, news_records
