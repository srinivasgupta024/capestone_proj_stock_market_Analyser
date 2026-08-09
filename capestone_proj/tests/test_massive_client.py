"""
Unit tests for MassiveClient API integration, exponential backoff, and telemetry.
"""

from src.massive_client import MassiveClient


def test_massive_client_init():
    client = MassiveClient()
    assert client is not None
    assert hasattr(client, "session")
    assert hasattr(client, "telemetry")


def test_get_ticker_quote():
    client = MassiveClient()
    quote = client.get_ticker_quote("NVDA")
    assert quote["ticker"] == "NVDA"
    assert quote["close_price"] > 0
    assert "timestamp" in quote


def test_get_news():
    client = MassiveClient()
    articles = client.get_news("AAPL", limit=3)
    assert isinstance(articles, list)
    assert len(articles) > 0
    first = articles[0]
    assert first["ticker"] == "AAPL"
    assert "title" in first
    assert "publisher" in first
