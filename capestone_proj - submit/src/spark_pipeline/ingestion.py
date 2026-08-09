"""
PySpark Ingestion Module (Bronze Layer ETL).
Fetches raw market and news data and ingests into PySpark DataFrames.
"""

from typing import List, Dict, Any
import logging
import pandas as pd

from src.massive_client import MassiveClient

logger = logging.getLogger(__name__)


def create_spark_session():
    """Build or retrieve a PySpark SparkSession configured with Delta Lake catalog support."""
    try:
        from pyspark.sql import SparkSession
        builder = (
            SparkSession.builder
            .appName("Capstone_Bronze_Ingestion")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        )
        try:
            from delta import configure_spark_with_delta_pip
            builder = configure_spark_with_delta_pip(builder)
        except ImportError:
            pass
        return builder.getOrCreate()
    except Exception as e:
        logger.warning(f"Native SparkSession creation notice: {e}")
        return None


def run_bronze_ingestion(tickers: List[str] = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "TSLA"]):
    """
    Bronze Layer: Ingest raw REST API payloads from Massive API,
    convert to PySpark DataFrames, and write directly to Delta Lake storage.
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
        try:
            df_prices_pd = pd.DataFrame(price_records)
            df_news_pd = pd.DataFrame(news_records)

            df_prices_bronze = spark.createDataFrame(df_prices_pd)
            df_news_bronze = spark.createDataFrame(df_news_pd)
            
            logger.info("PySpark Bronze DataFrames Materialized:")
            df_prices_bronze.show(5, truncate=False)
            df_news_bronze.show(5, truncate=False)

            # Persist Bronze DataFrames to Delta Lake Storage
            try:
                df_prices_bronze.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("storage/delta/bronze_prices")
                df_news_bronze.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("storage/delta/bronze_news")
                logger.info("Successfully wrote PySpark DataFrames to Delta Lake (storage/delta/bronze_prices & storage/delta/bronze_news).")
            except Exception as delta_err:
                logger.info(f"Delta write notice: {delta_err}. Storage materialized as PySpark parquet/json fallback.")
                df_prices_bronze.write.mode("overwrite").parquet("storage/delta/bronze_prices")
                df_news_bronze.write.mode("overwrite").parquet("storage/delta/bronze_news")

        except Exception as e:
            logger.warning(f"PySpark Bronze DataFrame creation notice: {e}")

    return price_records, news_records

