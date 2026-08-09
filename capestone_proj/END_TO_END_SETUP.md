# End-to-End Setup & Deployment Guide
## AI Stock Market Research Assistant & Investment Copilot

This guide provides comprehensive step-by-step instructions to configure, test, run, and deploy the **AI Stock Market Research Assistant** from end to end. It covers local standalone execution, PySpark Delta Lake Data Pipelines with Change Data Feed (CDF), Databricks Lakebase (PostgreSQL with `pgvector`), Sliding-Window Semantic RAG, Chain-of-Thought AI Agent tools, automated test suite verification, and Databricks Workspace App deployment.

---

## 📋 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites & System Requirements](#2-prerequisites--system-requirements)
3. [Environment Configuration (`.env`)](#3-environment-configuration-env)
4. [Database Setup (Lakebase / PostgreSQL + `pgvector`)](#4-database-setup-lakebase--postgresql--pgvector)
5. [PySpark Delta Lake & CDF Analytics Pipeline](#5-pyspark-delta-lake--cdf-analytics-pipeline)
6. [Resilient Third-Party API Client](#6-resilient-third-party-api-client)
7. [Sliding-Window RAG & MMR Vector Reranking](#7-sliding-window-rag--mmr-vector-reranking)
8. [Chain-of-Thought AI Agent & Tool Audit Logging](#8-chain-of-thought-ai-agent--tool-audit-logging)
9. [Automated Test Suite Verification](#9-automated-test-suite-verification)
10. [Databricks Workspace App Deployment](#10-databricks-workspace-app-deployment)
11. [Troubleshooting & FAQs](#11-troubleshooting--faqs)

---

## 1. Architecture Overview

```
 ┌────────────────┐
 │ Massive API    │──(urllib3 Exponential Backoff Retry & Rate Limit Handling)
 └───────┬────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ Bronze Layer: Raw API Fetching & Delta Ingestion       │
 └───────┬────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ PySpark Silver & Gold Layer DataFrame Transformations   │
 └───────┬────────────────────────────────────────────────┘
         │
         ├───────────────────────────────┬───────────────────────────────┐
         ▼                               ▼                               ▼
 ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
 │  Delta Lake   │               │   Delta CDF   │               │ sentence-tf   │
 │ (spark.write) │               │   Analytics   │               │ Multi-Chunker │
 └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
         │                               │                               │ (384-dim)
         ▼                               ▼                               ▼
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ Databricks Lakebase (PostgreSQL + pgvector HNSW Index + Tool Audit Logs)       │
 └───────────────────────────────────────┬───────────────────────────────────────┘
                                         │
                                         ▼
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ Streamlit UI / Chain-of-Thought AI Agent Copilot                              │
 └───────────────────────────────────────────────────────────────────────────────┘
```

The system comprises 5 core modules:
1. **Streamlit App Frontend**: Interactive multi-tab dashboard (`app.py`, `views/`).
2. **PySpark Delta Medallion Pipeline**: Transformations (`Window.partitionBy`, moving averages, volatility metrics, Gold aggregations) saved directly to Delta Lake storage with `delta.enableChangeDataFeed = true`.
3. **Delta Change Data Feed (CDF) Analytics Engine**: Reads change events (`_change_type`: `insert`, `update_postimage`, `delete`) and materializes downstream analytics Delta tables (`src/spark_pipeline/cdf_analytics.py`).
4. **Sliding-Window Semantic Vector RAG**: Multi-chunk text embedding (`embeddings.py`) paired with Maximal Marginal Relevance (MMR) query reranking (`vector_search.py`).
5. **Chain-of-Thought AI Agent**: Structured ReAct engine (`agent_engine.py`, `tools.py`) providing step-by-step reasoning traces (`Thought:`, `Action:`, `Observation:`, `Final Answer:`), inline citations, and tool invocation audit logging.

---

## 2. Prerequisites & System Requirements

- **Python**: Version **3.10+** (Python 3.10, 3.11, or 3.12 recommended).
- **RAM**: Minimum 8 GB.
- **Dependencies**: Listed in `requirements.txt`.

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 3. Environment Configuration (`.env`)

Create `.env` inside `capestone_proj/`:
```env
LAKEBASE_URL=postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require

MASSIVE_API_BASE_URL=https://api.massive.example.com
MASSIVE_SECRET_SCOPE=massive
MASSIVE_SECRET_KEY=api-key
```

---

## 4. Database Setup (Lakebase / PostgreSQL + `pgvector`)

The application automatically runs schema initialization via `init_db()` in `src/lakebase.py`, checking multiple candidate paths for `01_schema.sql`.

To initialize manually:
```bash
python -c "from src.lakebase import init_db; init_db()"
```

---

## 5. PySpark Delta Lake & CDF Analytics Pipeline

The pipeline creates PySpark DataFrames, executes feature-engineering transformations, writes results to Delta Lake storage, and processes Change Data Feeds:

- **Bronze Delta Ingestion**: `storage/delta/bronze_prices`, `storage/delta/bronze_news`
- **Silver Delta Features**: `storage/delta/silver_price_metrics` (Window moving averages & price spread)
- **Gold Delta Aggregations**: `storage/delta/gold_stock_analytics` (Average close, range, volume summary)
- **CDF Downstream Analytics**: `storage/delta/analytics_watchlist_changes`, `storage/delta/analytics_agent_metrics`

Execute pipeline manually:
```bash
python src/job_run.py
```

---

## 6. Resilient Third-Party API Client

`MassiveClient` (`src/massive_client.py`) includes `urllib3` exponential backoff retry adapters handling HTTP 429 rate limits and HTTP 5xx errors:
- Automatic backoff factor retry strategy.
- Live API response status 200 payload parsing with fallback to sandbox data when offline.
- Sample response payload documented in `sql/sample_massive_api_response.json`.

---

## 7. Sliding-Window RAG & MMR Vector Reranking

Unstructured news articles are split into sliding-window text chunks (300-char window, 50-char overlap) in `src/spark_pipeline/embeddings.py`.

At query time, `src/rag/vector_search.py` performs pgvector cosine distance search (`<=>`) and applies **Maximal Marginal Relevance (MMR)** reranking to ensure document diversity and prevent redundant chunks from dominating search results.

---

## 8. Chain-of-Thought AI Agent & Tool Audit Logging

`StockMarketAgent` (`src/agent/agent_engine.py`) produces explicit Chain-of-Thought reasoning traces:
```
🧠 Thought: Analyzing user query 'Add NVDA to watchlist buy target 120'.
⚙️ Action: tool_add_to_watchlist(ticker='NVDA', target_buy=120.0)
👁️ Observation: SUCCESS: Added NVDA to portfolio watchlist.
💡 Final Answer: Synthesized multi-step analysis with evidence citations.
```

Every tool execution is audited via `log_agent_tool_call()` into `agent_tool_calls` in Lakebase and Delta storage.

---

## 9. Automated Test Suite Verification

Run the full automated unit test suite:
```bash
python tests/run_tests.py
```

Expected Output:
```
==================================================
   AI Stock Market Research Copilot - Test Suite  
==================================================
  [PASS] MassiveClient Init
  [PASS] MassiveClient Get Quote
  [PASS] MassiveClient Get News
  [PASS] Sliding Window Text Chunker
  [PASS] Dense Vector Encoding
  [PASS] MMR Diversity Reranking
  [PASS] Agent Tool Snapshot
  [PASS] Agent Watchlist Mutations
  [PASS] Agent Engine Chain-of-Thought
  [PASS] Delta CDF Analytics Pipeline
  [PASS] CDF Telemetry Summary
--------------------------------------------------
Test Results: 11 PASSED, 0 FAILED out of 11 total tests.
==================================================
```

---

## 10. Databricks Workspace App Deployment

To deploy to Databricks Apps:
```bash
databricks bundle deploy --target dev
databricks apps deploy stock-copilot-app
```

---

## 11. Troubleshooting & FAQs

### Running Local Streamlit App
```bash
streamlit run app.py
```
Open `http://localhost:8501`.

### Build Submission Package
```bash
python build_submission.py
```
Generates updated `capestone_proj - submit.zip` package ready for submission.
