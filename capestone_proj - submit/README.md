# AI Stock Market Research Assistant & Investment Copilot
### Databricks Capstone Project

A full-stack, enterprise-grade AI Data Engineering application built on **Databricks Apps**, **Lakebase (PostgreSQL with `pgvector`)**, **PySpark Medallion Data Pipelines**, **Semantic RAG**, and an **Action-Oriented AI Tool Agent**.

---

## 🌟 Highlights & Standout Features

- **Databricks Apps Integration**: Fully configured for Databricks Workspace App deployment (`app.py`, `app.yaml`, `databricks.yml`).
- **Lakebase Relational & Vector Store**: Managed PostgreSQL instance with 9 relational tables (`users`, `companies`, `watchlists`, `watchlist_tickers`, `price_snapshots`, `news_articles`, `news_embeddings`, `research_notes`, `analysis_reports`) and `pgvector` HNSW index.
- **PySpark Medallion Pipeline**:
  - **Bronze**: Raw API fetching from Massive Financial API.
  - **Silver**: Data cleaning, schema enforcement, sentiment enrichment, and text chunking.
  - **Gold**: Business metrics aggregation, company profile reference dimensions, and vector embeddings persistence.
- **Semantic Vector RAG**: 384-dimensional dense text embeddings generated via `sentence-transformers/all-MiniLM-L6-v2` with cosine distance (`<=>`) vector retrieval.
- **Action-Oriented AI Tool Agent**: LLM ReAct agent capable of both **reading** (semantic vector search, SQL queries, quote retrieval) and **writing** (adding/removing watchlist items, saving research notes, generating formal analysis reports).
- **Free Tier Optimized**: Designed to run seamlessly in local standalone mode, Databricks Community Edition, or Databricks Enterprise Workspaces without requiring paid serverless vector search endpoints.

---

## 🚀 Architectural Overview

```
[ Massive API ] ──► [ PySpark Bronze Ingestion ]
                            │
                            ▼
                  [ Silver Cleaning & Text Chunking ]
                            │
                            ▼
            ┌───────────────┴───────────────┐
            ▼                               ▼
 [ Gold Aggregations ]          [ sentence-transformers ]
            │                               │
            ▼                               ▼
 [ Lakebase Relational DB ]     [ Lakebase pgvector Index ]
            │                               │
            └───────────────┬───────────────┘
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
*(Note: `psycopg2-binary` is omitted from `requirements.txt` to avoid package conflicts in Databricks Apps, where `psycopg2` is pre-installed).*

### 2. Environment Configuration
The application reads database connection settings from `.env`:
```env
LAKEBASE_URL=postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require

MASSIVE_API_BASE_URL=https://api.massive.com
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

## ☁️ Databricks Deployment

To deploy to Databricks Apps using Databricks Asset Bundles (DABs):
```bash
databricks bundle deploy --target dev
databricks apps deploy stock-copilot-app
```

---

## 🧪 Verification & Testing

To test the PySpark pipeline and Agent database write actions:
1. Click **"Trigger PySpark ETL & RAG Pipeline"** in the sidebar.
2. Navigate to **"Unstructured Vector RAG"** and search for *"AI cloud data center expansion"*.
3. Go to **"AI Agent Copilot"** and enter `"Add NVDA to my watchlist with target buy 120"`.
4. Check **"Portfolio Watchlist"** to verify that Lakebase was mutated in real-time.
