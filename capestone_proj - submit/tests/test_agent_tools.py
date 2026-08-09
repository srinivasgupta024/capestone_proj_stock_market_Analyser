"""
Unit tests for AI Agent Engine, Chain-of-Thought traces, and database state mutation tools.
"""

from src.agent.tools import (
    tool_get_ticker_snapshot,
    tool_get_watchlist,
    tool_add_to_watchlist,
    tool_remove_from_watchlist,
    tool_save_research_note,
    tool_generate_analysis_report
)
from src.agent.agent_engine import StockMarketAgent


def test_tool_get_ticker_snapshot():
    res = tool_get_ticker_snapshot("NVDA")
    assert "NVDA" in res
    assert "Market Snapshot" in res


def test_tool_watchlist_mutations():
    add_res = tool_add_to_watchlist("NVDA", target_buy=120.0, notes="Test add")
    assert "SUCCESS" in add_res

    wl_res = tool_get_watchlist()
    assert "Watchlist" in wl_res

    rem_res = tool_remove_from_watchlist("NVDA")
    assert "SUCCESS" in rem_res or "not found" in rem_res


def test_agent_engine_cot():
    agent = StockMarketAgent()
    response = agent.run("Analyze NVDA and add to my watchlist with buy target $125")
    assert "answer" in response
    assert "actions_taken" in response
    assert "Chain-of-Thought" in response["answer"]
