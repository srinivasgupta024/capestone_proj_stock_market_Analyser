"""
Client for fetching stock quotes, news articles, and company fundamentals
from the Massive / Financial API (with offline sample data fallbacks).
"""

import base64
from datetime import datetime, timezone
import logging
import os
import time
from typing import Any, List, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import MASSIVE_API_BASE_URL, MASSIVE_SECRET_SCOPE, MASSIVE_SECRET_KEY

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    """Fetch API key from env or Databricks secret scope."""
    key = os.environ.get("MASSIVE_API_KEY", "")
    if key:
        return key
    try:
        from databricks.sdk import WorkspaceClient
        w = WorkspaceClient()
        secret = w.secrets.get_secret(scope=MASSIVE_SECRET_SCOPE, key=MASSIVE_SECRET_KEY)
        return base64.b64decode(secret.value).decode("utf-8")
    except Exception:
        return "mock_demo_api_key"


class MassiveClient:
    """Wrapper for Massive Stock & News API with exponential backoff & rate-limit handling."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or MASSIVE_API_BASE_URL).rstrip("/")
        self.api_key = _get_api_key()
        self.session = requests.Session()
        
        # Configure robust urllib3 exponential backoff retry strategy for HTTP 429 & 5xx errors
        retry_strategy = Retry(
            total=4,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # In-memory API call telemetry for audit monitoring
        self.telemetry = {
            "total_calls": 0,
            "status_200": 0,
            "rate_limits_hit": 0,
            "retries": 0,
            "last_status": 200,
            "last_call_timestamp": None
        }

    def _execute_get_with_retry(self, url: str, params: dict | None = None, timeout: int = 10) -> requests.Response:
        """Execute GET request with rate-limit monitoring and exponential backoff."""
        self.telemetry["total_calls"] += 1
        self.telemetry["last_call_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        resp = self.session.get(url, params=params, timeout=timeout)
        self.telemetry["last_status"] = resp.status_code

        if resp.status_code == 200:
            self.telemetry["status_200"] += 1
        elif resp.status_code == 429:
            self.telemetry["rate_limits_hit"] += 1
            logger.warning("HTTP 429 Rate Limit encountered. Retry adapter executing exponential backoff...")
            time.sleep(2)  # Additional backoff delay for rate limit resolution
        else:
            logger.warning(f"API request returned non-200 status code: {resp.status_code}")

        return resp

    def get_ticker_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price snapshot for a symbol."""
        symbol = symbol.upper()
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/prev"
        try:
            resp = self._execute_get_with_retry(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [{}])[0]
                return {
                    "ticker": str(symbol),
                    "close_price": float(results.get("c", 150.0)),
                    "open_price": float(results.get("o", 148.5)),
                    "high_price": float(results.get("h", 152.0)),
                    "low_price": float(results.get("l", 147.8)),
                    "volume": int(results.get("v", 10500000)),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "api_status": "200_OK_LIVE"
                }
        except Exception as e:
            logger.warning(f"Live API call notice for {symbol}: {e}. Utilizing high-fidelity sandbox snapshot.")

        # Reliable Fallback Market Data for Demo / Sandbox
        mock_prices = {
            "AAPL": {"close": 224.50, "open": 221.30, "high": 226.10, "low": 220.80, "vol": 48200000, "name": "Apple Inc.", "sector": "Technology"},
            "MSFT": {"close": 448.20, "open": 444.00, "high": 450.50, "low": 442.10, "vol": 21500000, "name": "Microsoft Corporation", "sector": "Technology"},
            "NVDA": {"close": 128.90, "open": 124.50, "high": 130.20, "low": 123.80, "vol": 89400000, "name": "NVIDIA Corporation", "sector": "Semiconductors"},
            "AMZN": {"close": 186.40, "open": 184.20, "high": 188.00, "low": 183.50, "vol": 31200000, "name": "Amazon.com Inc.", "sector": "Consumer Cyclical"},
            "GOOGL": {"close": 175.80, "open": 173.90, "high": 177.10, "low": 173.20, "vol": 24800000, "name": "Alphabet Inc.", "sector": "Communication Services"},
            "TSLA": {"close": 215.30, "open": 208.40, "high": 218.90, "low": 206.10, "vol": 64500000, "name": "Tesla Inc.", "sector": "Automotive / EV"}
        }
        data = mock_prices.get(symbol, {"close": 150.0, "open": 148.0, "high": 152.0, "low": 147.0, "vol": 15000000, "name": f"{symbol} Corp", "sector": "General"})
        return {
            "ticker": str(symbol),
            "close_price": float(data["close"]),
            "open_price": float(data["open"]),
            "high_price": float(data["high"]),
            "low_price": float(data["low"]),
            "volume": int(data["vol"]),
            "name": str(data.get("name", symbol)),
            "sector": str(data.get("sector", "Technology")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_status": "FALLBACK_SANDBOX"
        }

    def get_news(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news articles for a ticker with full rate limit backoff."""
        ticker = ticker.upper()
        url = f"{self.base_url}/v2/reference/news"
        params = {"ticker": ticker, "limit": limit, "order": "desc"}
        try:
            resp = self._execute_get_with_retry(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    return [
                        {
                            "article_id": f"{ticker}_news_{idx}_{item.get('id', idx)}",
                            "ticker": ticker,
                            "title": item.get("title", "Market Update"),
                            "description": item.get("description", "Financial analysis and earnings announcement."),
                            "article_url": item.get("article_url", "https://example.com/finance"),
                            "publisher": item.get("publisher", {}).get("name", "MarketWatch"),
                            "published_utc": item.get("published_utc", datetime.now(timezone.utc).isoformat()),
                            "sentiment": item.get("insights", [{}])[0].get("sentiment", "bullish"),
                            "api_status": "200_OK_LIVE"
                        }
                        for idx, item in enumerate(results)
                    ]
        except Exception as e:
            logger.warning(f"Live news API notice: {e}. Generating unstructured news feed.")

        # Rich unstructured sample news for semantic embedding / RAG testing
        now_iso = datetime.now(timezone.utc).isoformat()
        return [
            {
                "article_id": f"{ticker}_news_101",
                "ticker": ticker,
                "title": f"{ticker} Beats Q2 Earnings Expectations Driven by High Cloud & AI Demand",
                "description": f"{ticker} reported record quarterly revenue growth of 28% year-over-year. Management cited massive enterprise adoption of AI server infrastructure and cloud data analytics platforms.",
                "article_url": f"https://finance-news.com/{ticker}/q2-earnings",
                "publisher": "Bloomberg Terminal",
                "author": "Sarah Jenkins",
                "published_utc": now_iso,
                "sentiment": "bullish",
                "sentiment_reasoning": "Strong top-line revenue beat and expanding profit margins in AI infrastructure.",
                "api_status": "FALLBACK_SANDBOX"
            },
            {
                "article_id": f"{ticker}_news_102",
                "ticker": ticker,
                "title": f"Federal Reserve Rate Outlook & Supply Chain Analysis for {ticker}",
                "description": f"Analysts assess how potential Federal Reserve interest rate cuts impact {ticker}'s capital expenditure plans and global supply chain logistics. Operating margins remain resilient.",
                "article_url": f"https://reuters.com/markets/{ticker}-fed-impact",
                "publisher": "Reuters",
                "author": "David Miller",
                "published_utc": now_iso,
                "sentiment": "neutral",
                "sentiment_reasoning": "Macroeconomic interest rate sensitivity balanced by strong cash flow.",
                "api_status": "FALLBACK_SANDBOX"
            },
            {
                "article_id": f"{ticker}_news_103",
                "ticker": ticker,
                "title": f"{ticker} Announces Strategic Partnership for Next-Gen Data Center Expansion",
                "description": f"{ticker} has entered into a multi-billion dollar partnership to build energy-efficient data centers powering large language model inference workloads worldwide.",
                "article_url": f"https://wsj.com/tech/{ticker}-datacenter-deal",
                "publisher": "Wall Street Journal",
                "author": "Elena Rostova",
                "published_utc": now_iso,
                "sentiment": "bullish",
                "sentiment_reasoning": "Strategic footprint expansion targeting long-term enterprise AI compute demand.",
                "api_status": "FALLBACK_SANDBOX"
            }
        ]

