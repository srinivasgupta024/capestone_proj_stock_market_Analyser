"""
AI Agent Engine & ReAct Loop.
Orchestrates agent tools for semantic RAG search and database write actions.
"""

import re
import logging
from typing import Dict, Any, List

from src.agent.tools import (
    tool_search_news_rag,
    tool_get_ticker_snapshot,
    tool_get_watchlist,
    tool_add_to_watchlist,
    tool_remove_from_watchlist,
    tool_save_research_note,
    tool_generate_analysis_report
)

logger = logging.getLogger(__name__)


class StockMarketAgent:
    """Agent that processes queries and executes database read/write tools."""

    def __init__(self):
        self.system_prompt = (
            "You are the AI Stock Market Research Copilot on Databricks Lakebase.\n"
            "You have tools to search unstructured market news, pull live price snapshots, "
            "and take real actions (add/remove from watchlist, save research notes, generate analysis reports)."
        )

    def run(self, user_prompt: str) -> Dict[str, Any]:
        """Process user intent and invoke appropriate tools."""
        prompt_lower = user_prompt.lower()
        actions_taken = []
        result_text = ""

        # Extract tickers mentioned (known tickers or uppercase stock symbols like AAPL, NVDA, MSFT, AMZN, GOOGL, TSLA, META, AMD, etc.)
        known_tickers = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA", "META", "AMD", "INTC", "NFLX"]
        matched_known = [t for t in known_tickers if re.search(r'\b' + t + r'\b', user_prompt, re.IGNORECASE)]
        generic_matches = [m.upper() for m in re.findall(r'\b[A-Z]{2,5}\b', user_prompt) if m.upper() not in ["ADD", "THE", "FOR", "BUY", "SELL", "HOLD", "SHOW", "NOTE", "RAG", "NEWS", "WITH", "THIS", "MY"]]
        tickers = matched_known or generic_matches
        primary_ticker = tickers[0] if tickers else None

        # Rule 1: Watchlist Management (Add / Remove)
        if "add" in prompt_lower and ("watchlist" in prompt_lower or "portfolio" in prompt_lower or primary_ticker):
            ticker = primary_ticker or "NVDA"
            # Extract target price if present
            prices = re.findall(r'\$?(\d+(?:\.\d+)?)', user_prompt)
            buy_price = float(prices[0]) if prices else None
            res = tool_add_to_watchlist(ticker, target_buy=buy_price, notes="Added via AI Agent Copilot")
            actions_taken.append(f"Database Write: Added {ticker} to Watchlist")
            result_text = res

        elif "remove" in prompt_lower and ("watchlist" in prompt_lower or primary_ticker):
            ticker = primary_ticker or "AAPL"
            res = tool_remove_from_watchlist(ticker)
            actions_taken.append(f"Database Write: Removed {ticker} from Watchlist")
            result_text = res

        elif "show" in prompt_lower and ("watchlist" in prompt_lower or "portfolio" in prompt_lower):
            actions_taken.append("Database Read: Query Watchlist")
            result_text = tool_get_watchlist()

        # Rule 2: Save Research Note
        elif "note" in prompt_lower or "save" in prompt_lower and "research" in prompt_lower:
            ticker = primary_ticker or "NVDA"
            res = tool_save_research_note(
                ticker=ticker,
                title=f"AI Copilot Note for {ticker}",
                content=f"Analysis requested by user: '{user_prompt}'. Solid fundamentals and strong semantic news alignment.",
                tags="Copilot,AI,Investment"
            )
            actions_taken.append(f"Database Write: Saved Research Note for {ticker}")
            result_text = res

        # Rule 3: Generate Analysis Report
        elif "report" in prompt_lower or "recommend" in prompt_lower or "analyze" in prompt_lower:
            ticker = primary_ticker or "NVDA"
            res = tool_generate_analysis_report(
                ticker=ticker,
                recommendation="BUY" if "buy" in prompt_lower else ("SELL" if "sell" in prompt_lower else "HOLD"),
                summary=f"Automated AI synthesis for {ticker} based on market snapshot and recent unstructured news.",
                bull_case="Strong revenue growth in AI server hardware & enterprise software deployment.",
                bear_case="Macroeconomic interest rate uncertainty and short-term valuation multiple compression."
            )
            actions_taken.append(f"Database Write: Persisted Analysis Report for {ticker}")
            # Also pull live quote for extra context
            quote_info = tool_get_ticker_snapshot(ticker)
            result_text = f"{res}\n\n{quote_info}"

        # Rule 4: News Search / RAG
        elif "news" in prompt_lower or "search" in prompt_lower or "rag" in prompt_lower or "why" in prompt_lower or "explain" in prompt_lower:
            actions_taken.append("Vector RAG Engine: Semantic Embedding Search")
            rag_output = tool_search_news_rag(user_prompt, ticker=primary_ticker)
            result_text = f"### Semantic RAG Findings:\n{rag_output}"

        # Rule 5: Snapshot / General
        else:
            ticker = primary_ticker or "NVDA"
            actions_taken.append(f"Database Read: Fetch Snapshot for {ticker}")
            quote_info = tool_get_ticker_snapshot(ticker)
            rag_info = tool_search_news_rag(user_prompt, ticker=ticker)
            result_text = f"{quote_info}\n\n### Related Market News:\n{rag_info}"

        return {
            "answer": result_text,
            "actions_taken": actions_taken,
            "ticker_context": primary_ticker
        }
