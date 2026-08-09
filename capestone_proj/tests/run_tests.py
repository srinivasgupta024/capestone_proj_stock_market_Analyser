"""
Standalone Test Runner Script.
Executes all unit tests across the test suite and reports PASS/FAIL status.
"""

import sys
import os
from pathlib import Path

# Set PYTHONPATH to project root
cwd = Path(__file__).resolve().parent.parent
if str(cwd) not in sys.path:
    sys.path.insert(0, str(cwd))

from tests.test_massive_client import test_massive_client_init, test_get_ticker_quote, test_get_news
from tests.test_vector_search import test_create_text_chunks, test_encode_text, test_apply_mmr_reranking
from tests.test_agent_tools import test_tool_get_ticker_snapshot, test_tool_watchlist_mutations, test_agent_engine_cot
from tests.test_cdf_analytics import test_process_cdf_analytics, test_get_cdf_analytics_summary


def run_all_tests():
    print("==================================================")
    print("   AI Stock Market Research Copilot - Test Suite  ")
    print("==================================================")
    
    tests = [
        ("MassiveClient Init", test_massive_client_init),
        ("MassiveClient Get Quote", test_get_ticker_quote),
        ("MassiveClient Get News", test_get_news),
        ("Sliding Window Text Chunker", test_create_text_chunks),
        ("Dense Vector Encoding", test_encode_text),
        ("MMR Diversity Reranking", test_apply_mmr_reranking),
        ("Agent Tool Snapshot", test_tool_get_ticker_snapshot),
        ("Agent Watchlist Mutations", test_tool_watchlist_mutations),
        ("Agent Engine Chain-of-Thought", test_agent_engine_cot),
        ("Delta CDF Analytics Pipeline", test_process_cdf_analytics),
        ("CDF Telemetry Summary", test_get_cdf_analytics_summary),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name} - Error: {e}")
            failed += 1

    print("--------------------------------------------------")
    print(f"Test Results: {passed} PASSED, {failed} FAILED out of {len(tests)} total tests.")
    print("==================================================")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
