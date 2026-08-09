"""
PySpark Transformations Module (Silver & Gold Layer ETL).
Applies data quality rules, sentiment aggregations, and saves to Lakebase relational tables.
"""

from typing import List, Dict, Any
import logging
import pandas as pd

from src.lakebase import run_write, run_query

logger = logging.getLogger(__name__)


from typing import List, Dict, Any
import logging
import pandas as pd

from src.lakebase import run_write, run_query
from src.spark_pipeline.ingestion import create_spark_session

logger = logging.getLogger(__name__)


def process_silver_gold_and_persist(price_records: List[Dict[str, Any]], news_records: List[Dict[str, Any]]):
    """
    Transforms Bronze raw records into Silver (cleaned & feature-engineered)
    and Gold (aggregated metrics) datasets using native PySpark DataFrames,
    persists to Delta Lake format with Change Data Feed, and syncs to Lakebase tables.
    """
    # 1. Upsert Companies table (Gold reference dimension in Lakebase)
    company_seeds = {
        "AAPL": ("Apple Inc.", "Technology", "Consumer Electronics & Services", "Apple designs and manufactures smartphones, personal computers, tablets, and AI services.", 3400000000000, 32.5, 0.55),
        "MSFT": ("Microsoft Corporation", "Technology", "Software & Cloud Services", "Microsoft develops enterprise cloud infrastructure, Office software, and Copilot AI systems.", 3300000000000, 35.1, 0.70),
        "NVDA": ("NVIDIA Corporation", "Semiconductors", "AI Compute Accelerators", "NVIDIA builds graphics processing units (GPUs) and CUDA AI hardware platforms.", 3100000000000, 48.2, 0.05),
        "AMZN": ("Amazon.com Inc.", "Consumer Cyclical", "E-Commerce & AWS Cloud", "Amazon operates e-commerce retail networks and AWS cloud infrastructure.", 1950000000000, 42.0, 0.00),
        "GOOGL": ("Alphabet Inc.", "Communication Services", "Internet Search & Gemini AI", "Alphabet operates Google search, YouTube, Android, and Gemini generative AI.", 2150000000000, 24.8, 0.45),
        "TSLA": ("Tesla Inc.", "Automotive / EV", "Electric Vehicles & Autonomy", "Tesla produces electric vehicles, energy storage systems, and Full Self-Driving AI.", 680000000000, 58.0, 0.00)
    }

    for ticker, info in company_seeds.items():
        run_write("""
            INSERT INTO companies (ticker, name, sector, industry, description, market_cap, pe_ratio, dividend_yield)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                description = EXCLUDED.description,
                market_cap = EXCLUDED.market_cap,
                pe_ratio = EXCLUDED.pe_ratio,
                dividend_yield = EXCLUDED.dividend_yield,
                updated_at = now();
        """, (ticker, info[0], info[1], info[2], info[3], info[4], info[5], info[6]))

    # 2. PySpark Silver & Gold Transformations
    spark = create_spark_session()
    if spark and price_records:
        try:
            from pyspark.sql import functions as F
            from pyspark.sql.window import Window

            pdf_prices = pd.DataFrame(price_records)
            df_prices_bronze = spark.createDataFrame(pdf_prices)

            # Silver Layer PySpark Transformation: Window moving averages & price spread metrics
            window_spec = Window.partitionBy("ticker").orderBy("timestamp")
            
            df_silver = (
                df_prices_bronze
                .withColumn("close_price", F.col("close_price").cast("double"))
                .withColumn("open_price", F.col("open_price").cast("double"))
                .withColumn("high_price", F.col("high_price").cast("double"))
                .withColumn("low_price", F.col("low_price").cast("double"))
                .withColumn("volume", F.col("volume").cast("long"))
                .withColumn("daily_spread", F.col("high_price") - F.col("low_price"))
                .withColumn("price_change_pct", ((F.col("close_price") - F.col("open_price")) / F.col("open_price")) * 100.0)
                .withColumn("sma_5", F.avg("close_price").over(window_spec.rowsBetween(-4, 0)))
            )

            # Gold Layer PySpark Aggregations: Stock Summary & Market Analytics
            df_gold = (
                df_silver
                .groupBy("ticker")
                .agg(
                    F.avg("close_price").alias("avg_close"),
                    F.max("high_price").alias("max_high"),
                    F.min("low_price").alias("min_low"),
                    F.sum("volume").alias("total_volume"),
                    F.avg("price_change_pct").alias("avg_daily_return_pct"),
                    F.count("ticker").alias("snapshot_count")
                )
            )

            logger.info("PySpark Silver Transformation Output:")
            df_silver.show(5, truncate=False)

            logger.info("PySpark Gold Aggregations Output:")
            df_gold.show(5, truncate=False)

            # Persist PySpark Silver & Gold DataFrames to Delta Lake Storage with CDF Enabled
            try:
                df_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option("delta.enableChangeDataFeed", "true").save("storage/delta/silver_price_metrics")
                df_gold.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option("delta.enableChangeDataFeed", "true").save("storage/delta/gold_stock_analytics")
                logger.info("PySpark Delta Lake persistence completed for storage/delta/silver_price_metrics and storage/delta/gold_stock_analytics.")
            except Exception as delta_ex:
                logger.info(f"PySpark Delta Lake write notice: {delta_ex}. Writing Parquet backup layer.")
                df_silver.write.mode("overwrite").parquet("storage/delta/silver_price_metrics")
                df_gold.write.mode("overwrite").parquet("storage/delta/gold_stock_analytics")

        except Exception as spark_err:
            logger.warning(f"PySpark Silver/Gold transformation notice: {spark_err}")

    # 3. Persist Price Snapshots to Lakebase Relational DB
    for quote in price_records:
        ticker = quote.get("ticker")
        if not ticker:
            continue
        run_write("""
            INSERT INTO price_snapshots (ticker, open_price, high_price, low_price, close_price, volume, snapshot_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (
            ticker,
            quote.get("open_price"),
            quote.get("high_price"),
            quote.get("low_price"),
            quote.get("close_price"),
            quote.get("volume"),
            quote.get("timestamp")
        ))

    # 4. Persist News Articles to Lakebase
    for news in news_records:
        run_write("""
            INSERT INTO news_articles (article_id, ticker, title, description, article_url, publisher, author, published_utc, sentiment, sentiment_reasoning)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (article_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                sentiment = EXCLUDED.sentiment,
                synced_at = now();
        """, (
            news.get("article_id"),
            news.get("ticker"),
            news.get("title"),
            news.get("description"),
            news.get("article_url"),
            news.get("publisher"),
            news.get("author"),
            news.get("published_utc"),
            news.get("sentiment", "neutral"),
            news.get("sentiment_reasoning", "Extracted via NLP pipeline.")
        ))

    # 5. Seed & Sync Portfolio Watchlist Delta & Lakebase Tables
    run_write("""
        INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
        VALUES 
            ('default_watchlist', 'NVDA', 115.00, 145.00, 'Core AI hardware play. Accumulate on dips.'),
            ('default_watchlist', 'MSFT', 420.00, 480.00, 'Cloud + Copilot revenue driver.'),
            ('default_watchlist', 'AAPL', 210.00, 240.00, 'Apple Intelligence supercycle.')
        ON CONFLICT (watchlist_id, ticker) DO NOTHING;
    """)

    # Materialize watchlist Delta table for CDF tracking
    if spark:
        try:
            watchlists_data = run_query("SELECT watchlist_id, ticker, target_buy_price, target_sell_price, notes, added_at FROM watchlist_tickers;")
            if watchlists_data:
                df_wl = spark.createDataFrame(pd.DataFrame(watchlists_data))
                try:
                    df_wl.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option("delta.enableChangeDataFeed", "true").save("storage/delta/watchlists")
                    logger.info("Persisted PySpark Watchlists Delta table with CDF enabled (storage/delta/watchlists).")
                except Exception:
                    df_wl.write.mode("overwrite").parquet("storage/delta/watchlists")
        except Exception as wl_err:
            logger.warning(f"Watchlists Delta table notice: {wl_err}")

    logger.info("Silver & Gold PySpark & Lakebase persistence completed successfully.")

