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

import time

logger = logging.getLogger(__name__)
client = MassiveClient()


def log_agent_tool_call(tool_name: str, parameters: str, result_summary: str, status: str = "SUCCESS", latency_ms: float = 0.0):
    """
    Audit logger: Persists every agent tool execution to agent_tool_calls table in Lakebase
    and updates PySpark Delta Lake audit table to fuel Change Data Feed (CDF) analytics.
    """
    call_id = f"toolcall_{uuid.uuid4().hex[:10]}"
    try:
        run_write("""
            INSERT INTO agent_tool_calls (call_id, user_id, tool_name, parameters, result_summary, status, execution_time_ms)
            VALUES (%s, 'default_user', %s, %s, %s, %s, %s);
        """, (call_id, tool_name, str(parameters)[:255], str(result_summary)[:255], status, latency_ms))
    except Exception as e:
        logger.warning(f"Tool call audit log notice: {e}")


# --- READ TOOLS ---

def tool_search_news_rag(query: str, ticker: Optional[str] = None) -> str:
    """Agent tool to search unstructured market news using semantic vector RAG."""
    start_t = time.time()
    results = search_news_vector(query, ticker=ticker, top_k=4)
    latency_ms = round((time.time() - start_t) * 1000, 2)

    if not results:
        msg = f"No news articles found matching query '{query}'."
        log_agent_tool_call("tool_search_news_rag", f"query={query}, ticker={ticker}", msg, "EMPTY", latency_ms)
        return msg

    output = [f"Found {len(results)} relevant news articles:"]
    for r in results:
        score = f"{r.get('reranked_score', r.get('similarity_score', 0)):.2f}"
        output.append(
            f"- [{r.get('ticker')}] {r.get('title')} (MMR Score: {score}, Sentiment: {r.get('sentiment')})\n"
            f"  Publisher: {r.get('publisher')} | Citation URL: {r.get('article_url')}\n"
            f"  Snippet: {r.get('chunk_text')[:200]}..."
        )
    res_str = "\n".join(output)
    log_agent_tool_call("tool_search_news_rag", f"query={query}, ticker={ticker}", f"Found {len(results)} articles", "SUCCESS", latency_ms)
    return res_str



def tool_get_ticker_snapshot(ticker: str) -> str:
    """Agent tool to fetch current market price, volume, and company fundamentals."""
    start_t = time.time()
    ticker = ticker.upper()
    quote = client.get_ticker_quote(ticker)
    
    comp = run_query("SELECT name, sector, pe_ratio, market_cap FROM companies WHERE ticker = %s;", (ticker,))
    company_name = comp[0]["name"] if comp else ticker
    sector = comp[0]["sector"] if comp else "N/A"
    pe = comp[0]["pe_ratio"] if comp else "N/A"

    latency_ms = round((time.time() - start_t) * 1000, 2)
    res = (
        f"--- {company_name} ({ticker}) Market Snapshot ---\n"
        f"Sector: {sector} | P/E Ratio: {pe}\n"
        f"Latest Close: ${quote.get('close_price'):.2f} | Open: ${quote.get('open_price'):.2f}\n"
        f"High: ${quote.get('high_price'):.2f} | Low: ${quote.get('low_price'):.2f}\n"
        f"Volume: {quote.get('volume'):,} | Timestamp: {quote.get('timestamp')}"
    )
    log_agent_tool_call("tool_get_ticker_snapshot", f"ticker={ticker}", f"Snapshot close=${quote.get('close_price')}", "SUCCESS", latency_ms)
    return res


def tool_get_watchlist() -> str:
    """Agent tool to list all tickers currently saved in the user's watchlist."""
    start_t = time.time()
    rows = run_query("""
        SELECT wt.ticker, c.name, wt.target_buy_price, wt.target_sell_price, wt.notes
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)
    latency_ms = round((time.time() - start_t) * 1000, 2)
    if not rows:
        msg = "Your portfolio watchlist is currently empty."
        log_agent_tool_call("tool_get_watchlist", "watchlist_id=default_watchlist", msg, "EMPTY", latency_ms)
        return msg

    output = ["Your Portfolio Watchlist:"]
    for r in rows:
        output.append(
            f"- {r['ticker']} ({r.get('name', 'N/A')}): Target Buy: ${r.get('target_buy_price') or 'N/A'}, "
            f"Target Sell: ${r.get('target_sell_price') or 'N/A'} | Notes: {r.get('notes') or 'None'}"
        )
    res = "\n".join(output)
    log_agent_tool_call("tool_get_watchlist", "watchlist_id=default_watchlist", f"Returned {len(rows)} tickers", "SUCCESS", latency_ms)
    return res


# --- WRITE TOOLS (DATABASE STATE ACTIONS) ---

def tool_add_to_watchlist(ticker: str, target_buy: Optional[float] = None, target_sell: Optional[float] = None, notes: str = "") -> str:
    """Agent tool to ADD a ticker to the user's portfolio watchlist in Lakebase."""
    start_t = time.time()
    ticker = ticker.upper()
    run_write("INSERT INTO companies (ticker, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (ticker, f"{ticker} Corp"))

    count = run_write("""
        INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
        VALUES ('default_watchlist', %s, %s, %s, %s)
        ON CONFLICT (watchlist_id, ticker) DO UPDATE SET
            target_buy_price = EXCLUDED.target_buy_price,
            target_sell_price = EXCLUDED.target_sell_price,
            notes = EXCLUDED.notes;
    """, (ticker, target_buy, target_sell, notes))

    latency_ms = round((time.time() - start_t) * 1000, 2)
    res = f"SUCCESS: Added {ticker} to your portfolio watchlist with Target Buy: ${target_buy or 'N/A'} and Target Sell: ${target_sell or 'N/A'}."
    log_agent_tool_call("tool_add_to_watchlist", f"ticker={ticker}, buy={target_buy}", res, "SUCCESS", latency_ms)
    return res


def tool_remove_from_watchlist(ticker: str) -> str:
    """Agent tool to REMOVE a ticker from the user's watchlist."""
    start_t = time.time()
    ticker = ticker.upper()
    count = run_write("DELETE FROM watchlist_tickers WHERE watchlist_id = 'default_watchlist' AND ticker = %s;", (ticker,))
    latency_ms = round((time.time() - start_t) * 1000, 2)
    if count > 0:
        res = f"SUCCESS: Removed {ticker} from your portfolio watchlist."
        log_agent_tool_call("tool_remove_from_watchlist", f"ticker={ticker}", res, "SUCCESS", latency_ms)
        return res
    res = f"Ticker {ticker} was not found in your watchlist."
    log_agent_tool_call("tool_remove_from_watchlist", f"ticker={ticker}", res, "NOT_FOUND", latency_ms)
    return res


def tool_save_research_note(ticker: str, title: str, content: str, tags: str = "AI,Research") -> str:
    """Agent tool to write and save a research note into Lakebase for a specific ticker."""
    start_t = time.time()
    ticker = ticker.upper()
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    tag_array = [t.strip() for t in tags.split(",") if t.strip()]

    run_write("""
        INSERT INTO research_notes (note_id, user_id, ticker, title, content, tags)
        VALUES (%s, 'default_user', %s, %s, %s, %s);
    """, (note_id, ticker, title, content, tag_array))

    latency_ms = round((time.time() - start_t) * 1000, 2)
    res = f"SUCCESS: Saved research note '{title}' for {ticker} into Lakebase database (Note ID: {note_id})."
    log_agent_tool_call("tool_save_research_note", f"ticker={ticker}, note_id={note_id}", res, "SUCCESS", latency_ms)
    return res


def tool_generate_analysis_report(ticker: str, recommendation: str, summary: str, bull_case: str, bear_case: str) -> str:
    """Agent tool to generate and save a formal AI Stock Analysis Report into Lakebase."""
    start_t = time.time()
    ticker = ticker.upper()
    report_id = f"report_{uuid.uuid4().hex[:8]}"
    rec = recommendation.upper()
    if rec not in ["BUY", "HOLD", "SELL"]:
        rec = "HOLD"

    run_write("""
        INSERT INTO analysis_reports (report_id, user_id, ticker, recommendation, summary, bull_case, bear_case)
        VALUES (%s, 'default_user', %s, %s, %s, %s, %s);
    """, (report_id, ticker, rec, summary, bull_case, bear_case))

    latency_ms = round((time.time() - start_t) * 1000, 2)
    res = (
        f"SUCCESS: Generated & persisted AI Investment Analysis Report for {ticker}!\n"
        f"Recommendation: {rec}\n"
        f"Summary: {summary}\n"
        f"Report ID: {report_id}"
    )
    log_agent_tool_call("tool_generate_analysis_report", f"ticker={ticker}, rec={rec}", f"Report {report_id} generated", "SUCCESS", latency_ms)
    return res

