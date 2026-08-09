# AI Stock Market Research Assistant & Investment Copilot
### Databricks Capstone Project

A full-stack, enterprise-grade AI Data Engineering application built on **Databricks Apps**, **Delta Lake with Change Data Feed (CDF)**, **Lakebase (PostgreSQL with `pgvector`)**, **PySpark Medallion Data Pipelines**, **Sliding-Window Semantic RAG**, and an **Action-Oriented Chain-of-Thought AI Agent**.

---

## 🌟 Highlights & Key Upgrades

- **PySpark Delta Lake Pipeline**: Native PySpark DataFrame transformations (`Window.partitionBy`, moving averages, volatility metrics, Gold aggregations) with direct Delta Lake writes (`spark.write.format("delta")`).
- **Delta Change Data Feed (CDF) Analytics**: Delta tables created with `delta.enableChangeDataFeed = true`. Downstream analytics pipeline (`src/spark_pipeline/cdf_analytics.py`) reads change events (`_change_type`: `insert`, `update_postimage`, `delete`) and computes activity metrics displayed in System Health UI.
- **Robust Third-Party API Integration**: `MassiveClient` (`src/massive_client.py`) uses `urllib3` retry adapters with exponential backoff handling for HTTP 429 rate limits and 5xx errors, with raw API responses persisted in Bronze Delta storage.
- **Advanced Unstructured Processing & RAG**: Sliding-window text chunking (300-char windows with overlap) in `embeddings.py` paired with Maximal Marginal Relevance (MMR) query reranking and recency decay scoring in `vector_search.py`.
- **Chain-of-Thought AI Agent**: Upgraded `StockMarketAgent` featuring step-by-step reasoning traces (`Thought:`, `Action:`, `Action Input:`, `Observation:`, `Final Answer:`), inline citations, and tool call audit logging to `agent_tool_calls` and Delta storage.
- **Lakebase Relational & Vector Store**: PostgreSQL instance with 10 relational tables and pgvector HNSW index (`idx_news_embeddings_vector`).
- **Comprehensive Unit Test Suite**: Fully automated test suite (`tests/run_tests.py`) covering API retries, PySpark transformations, CDF analytics, MMR reranking, and Agent tools.

---

## 🚀 Architectural Overview

```
[ Massive API ] ──(Exponential Backoff Retry)──► [ PySpark Bronze Ingestion ]
                                                         │
                                                         ▼
                                          [ Silver & Gold PySpark Transforms ]
                                                         │
                                      ┌──────────────────┴──────────────────┐
                                      ▼                                     ▼
                          [ Delta Lake + CDF ]                    [ sentence-transformers ]
                         (watchlists, metrics)                              │
                                      │                                     ▼
                                      ▼                          [ Lakebase pgvector HNSW ]
                           [ CDF Analytics Pipeline ]                       │
                                      │                                     ▼
                                      └──────────────────┬──────────────────┘
                                                         │
                                                         ▼
                                            [ Databricks App UI / Agent ]
```

---

## 🛠️ Installation & Local Setup

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
The application reads database connection settings from `.env`:
```env
LAKEBASE_URL=postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require

MASSIVE_API_BASE_URL=https://api.massive.example.com
MASSIVE_SECRET_SCOPE=massive
MASSIVE_SECRET_KEY=api-key
```

### 3. Running the App
Run the Streamlit web application:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Verification & Testing

### 1. Run the Unit Test Suite
Execute the automated test suite:
```bash
python tests/run_tests.py
```

### 2. Run the Full Databricks Job Pipeline
Execute end-to-end ingestion, PySpark Delta writes, CDF analytics, and pgvector embeddings:
```bash
python src/job_run.py
```

### 3. Build Submission Zip Package
Sync code and build clean submission zip:
```bash
python build_submission.py
```

---

## ☁️ Databricks Workspace App Deployment

To deploy to Databricks Apps using Databricks Asset Bundles (DABs):
```bash
databricks bundle deploy --target dev
databricks apps deploy stock-copilot-app
```
