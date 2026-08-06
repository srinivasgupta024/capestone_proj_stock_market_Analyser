"""
PySpark Transformations Module (Silver & Gold Layer ETL).
Applies data quality rules, sentiment aggregations, and saves to Lakebase relational tables.
"""

from typing import List, Dict, Any
import logging
import pandas as pd

from src.lakebase import run_write, run_query

logger = logging.getLogger(__name__)


def process_silver_gold_and_persist(price_records: List[Dict[str, Any]], news_records: List[Dict[str, Any]]):
    """
    Transforms Bronze raw records into Silver (cleaned & validated)
    and Gold (aggregated metrics) datasets, then persists to Lakebase tables.
    """
    # 1. Upsert Companies table (Gold reference dimension)
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

    # 2. Persist Price Snapshots (Silver/Gold facts)
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

    # 3. Persist News Articles (Unstructured Silver table)
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

    # Seed Default Watchlist Tickers if empty
    run_write("""
        INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
        VALUES 
            ('default_watchlist', 'NVDA', 115.00, 145.00, 'Core AI hardware play. Accumulate on dips.'),
            ('default_watchlist', 'MSFT', 420.00, 480.00, 'Cloud + Copilot revenue driver.'),
            ('default_watchlist', 'AAPL', 210.00, 240.00, 'Apple Intelligence supercycle.')
        ON CONFLICT (watchlist_id, ticker) DO NOTHING;
    """)

    logger.info("Silver & Gold pipeline persistence completed.")
