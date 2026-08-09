"""
Unit tests for Delta Change Data Feed (CDF) analytics pipeline.
"""

from src.spark_pipeline.cdf_analytics import process_cdf_analytics, get_cdf_analytics_summary


def test_process_cdf_analytics():
    summary = process_cdf_analytics()
    assert isinstance(summary, dict)
    assert "status" in summary
    assert summary["status"] == "SUCCESS"
    assert "insert_count" in summary


def test_get_cdf_analytics_summary():
    summary = get_cdf_analytics_summary()
    assert isinstance(summary, dict)
    assert "processed_at" in summary
