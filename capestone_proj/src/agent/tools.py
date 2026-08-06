"""
Agent Tools Module.
Exposes both READ (retrieval/queries) and WRITE (database state mutation) capabilities.
"""

from typing import List, Dict, Any, Optional
import uuid
import logging

from src.lakebase import run_query, run_write
from src.rag.vector_search import search_news_vector
from src.massive_client import MassiveClient

logger = logging.getLogger(__name__)
client = MassiveClient()

# --- READ TOOLS ---

def tool_search_news_rag(query: str, ticker: Optional[str] = None) -> str:
    """Agent tool to search unstructured market news using semantic vector RAG."""
    results = search_news_vector(query, ticker=ticker, top_k=4)
    if not results:
        return f"No news articles found matching query '{query}'."

    output = [f"Found {len(results)} relevant news articles:"]
    for r in results:
        score = f"{r.get('similarity_score', 0):.2f}" if r.get('similarity_score') else "N/A"
        output.append(
            f"- [{r.get('ticker')}] {r.get('title')} (Relevance: {score}, Sentiment: {r.get('sentiment')})\n"
            f"  Publisher: {r.get('publisher')} | Snippet: {r.get('chunk_text')[:200]}..."
        )
    return "\n".join(output)


def tool_get_ticker_snapshot(ticker: str) -> str:
    """Agent tool to fetch current market price, volume, and company fundamentals."""
    ticker = ticker.upper()
    quote = client.get_ticker_quote(ticker)
    
    # Query fundamental metrics from company table
    comp = run_query("SELECT name, sector, pe_ratio, market_cap FROM companies WHERE ticker = %s;", (ticker,))
    company_name = comp[0]["name"] if comp else ticker
    sector = comp[0]["sector"] if comp else "N/A"
    pe = comp[0]["pe_ratio"] if comp else "N/A"

    return (
        f"--- {company_name} ({ticker}) Market Snapshot ---\n"
        f"Sector: {sector} | P/E Ratio: {pe}\n"
        f"Latest Close: ${quote.get('close_price'):.2f} | Open: ${quote.get('open_price'):.2f}\n"
        f"High: ${quote.get('high_price'):.2f} | Low: ${quote.get('low_price'):.2f}\n"
        f"Volume: {quote.get('volume'):,} | Timestamp: {quote.get('timestamp')}"
    )


def tool_get_watchlist() -> str:
    """Agent tool to list all tickers currently saved in the user's watchlist."""
    rows = run_query("""
        SELECT wt.ticker, c.name, wt.target_buy_price, wt.target_sell_price, wt.notes
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)
    if not rows:
        return "Your portfolio watchlist is currently empty."

    output = ["Your Portfolio Watchlist:"]
    for r in rows:
        output.append(
            f"- {r['ticker']} ({r.get('name', 'N/A')}): Target Buy: ${r.get('target_buy_price') or 'N/A'}, "
            f"Target Sell: ${r.get('target_sell_price') or 'N/A'} | Notes: {r.get('notes') or 'None'}"
        )
    return "\n".join(output)


# --- WRITE TOOLS (DATABASE STATE ACTIONS) ---

def tool_add_to_watchlist(ticker: str, target_buy: Optional[float] = None, target_sell: Optional[float] = None, notes: str = "") -> str:
    """Agent tool to ADD a ticker to the user's portfolio watchlist in Lakebase."""
    ticker = ticker.upper()
    # Ensure company exists
    run_write("INSERT INTO companies (ticker, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (ticker, f"{ticker} Corp"))

    count = run_write("""
        INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
        VALUES ('default_watchlist', %s, %s, %s, %s)
        ON CONFLICT (watchlist_id, ticker) DO UPDATE SET
            target_buy_price = EXCLUDED.target_buy_price,
            target_sell_price = EXCLUDED.target_sell_price,
            notes = EXCLUDED.notes;
    """, (ticker, target_buy, target_sell, notes))

    return f"SUCCESS: Added {ticker} to your portfolio watchlist with Target Buy: ${target_buy or 'N/A'} and Target Sell: ${target_sell or 'N/A'}."


def tool_remove_from_watchlist(ticker: str) -> str:
    """Agent tool to REMOVE a ticker from the user's watchlist."""
    ticker = ticker.upper()
    count = run_write("DELETE FROM watchlist_tickers WHERE watchlist_id = 'default_watchlist' AND ticker = %s;", (ticker,))
    if count > 0:
        return f"SUCCESS: Removed {ticker} from your portfolio watchlist."
    return f"Ticker {ticker} was not found in your watchlist."


def tool_save_research_note(ticker: str, title: str, content: str, tags: str = "AI,Research") -> str:
    """Agent tool to write and save a research note into Lakebase for a specific ticker."""
    ticker = ticker.upper()
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    tag_array = [t.strip() for t in tags.split(",") if t.strip()]

    run_write("""
        INSERT INTO research_notes (note_id, user_id, ticker, title, content, tags)
        VALUES (%s, 'default_user', %s, %s, %s, %s);
    """, (note_id, ticker, title, content, tag_array))

    return f"SUCCESS: Saved research note '{title}' for {ticker} into Lakebase database (Note ID: {note_id})."


def tool_generate_analysis_report(ticker: str, recommendation: str, summary: str, bull_case: str, bear_case: str) -> str:
    """Agent tool to generate and save a formal AI Stock Analysis Report into Lakebase."""
    ticker = ticker.upper()
    report_id = f"report_{uuid.uuid4().hex[:8]}"
    rec = recommendation.upper()
    if rec not in ["BUY", "HOLD", "SELL"]:
        rec = "HOLD"

    run_write("""
        INSERT INTO analysis_reports (report_id, user_id, ticker, recommendation, summary, bull_case, bear_case)
        VALUES (%s, 'default_user', %s, %s, %s, %s, %s);
    """, (report_id, ticker, rec, summary, bull_case, bear_case))

    return (
        f"SUCCESS: Generated & persisted AI Investment Analysis Report for {ticker}!\n"
        f"Recommendation: {rec}\n"
        f"Summary: {summary}\n"
        f"Report ID: {report_id}"
    )
