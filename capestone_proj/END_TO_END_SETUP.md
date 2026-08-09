# End-to-End Setup & Deployment Guide
## AI Stock Market Research Assistant & Investment Copilot

This guide provides step-by-step instructions to set up, configure, run, and deploy the **AI Stock Market Research Assistant** from end to end. It covers local standalone execution, Databricks Lakebase (PostgreSQL with `pgvector`), PySpark Medallion ETL, Sentence-Transformers RAG, ReAct AI Agent tools, and Databricks Workspace App deployment.

---

## 📋 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites & System Requirements](#2-prerequisites--system-requirements)
3. [Environment Configuration (`.env`)](#3-environment-configuration-env)
4. [Database Setup (Lakebase / PostgreSQL + `pgvector`)](#4-database-setup-lakebase--postgresql--pgvector)
5. [Local Standalone Setup & Execution](#5-local-standalone-setup--execution)
6. [PySpark Medallion ETL & Vector RAG Pipeline](#6-pyspark-medallion-etl--vector-rag-pipeline)
7. [AI Agent Copilot & ReAct Tools](#7-ai-agent-copilot--react-tools)
8. [Databricks Workspace App Deployment](#8-databricks-workspace-app-deployment)
9. [Verification & End-to-End Testing Checklist](#9-verification--end-to-end-testing-checklist)
10. [Troubleshooting & Common FAQs](#10-troubleshooting--common-faqs)

---

## 1. Architecture Overview

```
 ┌────────────────┐
 │ Massive API    │
 └───────┬────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ Bronze Layer: Raw Rest Fetching                        │
 └───────┬────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ Silver Layer: Cleaning, Validation & NLP Chunking      │
 └───────┬────────────────────────────────────────────────┘
         │
         ├───────────────────────────────┐
         ▼                               ▼
 ┌───────────────────────────────┐ ┌────────────────────────────────┐
 │ Gold Layer: Metrics Agg       │ │ SentenceTransformers Embedder │
 └───────┬───────────────────────┘ └───────┬────────────────────────┘
         │ (Relational Data)               │ (384-dim Dense Vectors)
         ▼                                 ▼
 ┌────────────────────────────────────────────────────────┐
 │ Databricks Lakebase (PostgreSQL + pgvector HNSW Index) │
 └───────┬────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ Streamlit UI / ReAct AI Agent Copilot                  │
 └────────────────────────────────────────────────────────┘
```

The system comprises 4 primary components:
1. **Frontend UI**: Built with Streamlit (`app.py`), featuring a sleek glassmorphic dark theme and Plotly charts across 4 tabs.
2. **Lakebase Database**: PostgreSQL managed instance with `pgvector` enabled, housing 9 relational and vector tables.
3. **Data Pipeline**: PySpark medallion pipeline (`ingestion.py`, `transformations.py`, `embeddings.py`) transforming raw market data into Silver facts and Gold dimensions.
4. **Action-Oriented AI Agent**: ReAct agent (`agent_engine.py`, `tools.py`) executing both **READ** (RAG vector search, price quotes, watchlists) and **WRITE** (watchlist additions/deletions, research note creation, formal analysis report generation) operations on Lakebase.

---

## 2. Prerequisites & System Requirements

### Hardware & OS
- **OS**: Windows 10/11, macOS, or Linux.
- **RAM**: Minimum 8 GB (16 GB recommended for running PySpark and local sentence-transformers models).
- **Disk Space**: ~2 GB for Python packages and pre-trained NLP models.

### Software Tooling
- **Python**: Version **3.10+** (Python 3.10, 3.11, or 3.12 recommended).
- **Git**: For version control.
- **Databricks CLI** (Optional, for Cloud App Deployment): Install via `winget install Databricks.DatabricksCLI` or `brew install databricks/tap/databricks`.

---

## 3. Environment Configuration (`.env`)

The project uses `python-dotenv` to load database credentials and API endpoints from a `.env` file in the root of `capestone_proj`.

### Step 3.1: Create `.env` File
Create a `.env` file inside `capestone_proj/`:

```env
# 1. Databricks Lakebase / PostgreSQL Connection String
LAKEBASE_URL=postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require

# 2. Market & News API Configuration
MASSIVE_API_BASE_URL=https://api.massive.com
MASSIVE_SECRET_SCOPE=massive
MASSIVE_SECRET_KEY=api-key

# 3. Optional LLM Provider Keys (for custom integrations)
OPENAI_API_KEY=
GEMINI_API_KEY=
```

> [!IMPORTANT]
> Ensure `sslmode=require` is present in the `LAKEBASE_URL` connection string to satisfy PostgreSQL SSL security requirements.

---

## 4. Database Setup (Lakebase / PostgreSQL + `pgvector`)

The application requires a PostgreSQL database with the `pgvector` extension installed.

### Database Tables (9 Tables)
1. `users`: System user profiles.
2. `companies`: Fundamental reference dimensions (market cap, P/E ratio, sector, description).
3. `watchlists`: User portfolio watchlists.
4. `watchlist_tickers`: Junction table tracking target buy/sell prices and notes.
5. `price_snapshots`: Fact table with daily open/high/low/close prices and volume.
6. `news_articles`: Fact table with unstructured financial news articles and sentiment tags.
7. `news_embeddings`: Vector store housing 384-dimensional text embeddings with HNSW cosine distance index (`vector_cosine_ops`).
8. `research_notes`: Agent action target storing user & AI generated notes.
9. `analysis_reports`: Agent action target storing formal stock analysis reports (BUY/HOLD/SELL).

### Step 4.1: Automated Schema Initialization
The application automatically runs schema initialization on startup via `init_db()` in `src/lakebase.py`, which reads and executes `sql/01_schema.sql`.

To manually verify or initialize the schema using Python:
```bash
python -c "from src.lakebase import init_db; init_db()"
```

### Step 4.2: Manual Schema Execution via `psql` (Optional)
If connecting directly via PostgreSQL command line client (`psql`):
```bash
psql "postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require" -f sql/01_schema.sql
```

---

## 5. Local Standalone Setup & Execution

Follow these steps to set up and run the application locally on your workstation.

### Step 5.1: Clone the Repository
```bash
git clone https://github.com/srinivasgupta024/capestone_proj_stock_market_Analyser.git
cd capestone_proj_stock_market_Analyser/capestone_proj
```

### Step 5.2: Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 5.3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> [!NOTE]
> For local development, if `psycopg2` is not already installed on your system, install `psycopg2-binary`:
> ```bash
> pip install psycopg2-binary
> ```
> *(Note: `psycopg2-binary` is excluded from `requirements.txt` to avoid package conflicts when deploying to Databricks Apps, where `psycopg2` is pre-installed).*

### Step 5.4: Launch the Streamlit App
```bash
streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## 6. PySpark Medallion ETL & Vector RAG Pipeline

The application features an enterprise Medallion Data Architecture (Bronze → Silver → Gold):

```
Raw API Payload ──► [ Bronze Ingestion ] ──► [ Silver Cleaning ] ──► [ Gold Aggregations ]
                                                   │
                                                   ▼
                                         [ Sentence Transformers ]
                                                   │
                                                   ▼
                                        [ Lakebase pgvector Store ]
```

### Execution Methods
1. **Interactive UI Button**: Click **"🔄 Trigger PySpark ETL & RAG Pipeline"** in the Streamlit sidebar.
2. **Programmatic Trigger**:
```python
from src.spark_pipeline.ingestion import run_bronze_ingestion
from src.spark_pipeline.transformations import process_silver_gold_and_persist
from src.spark_pipeline.embeddings import generate_and_store_news_embeddings

# 1. Ingest Bronze
prices, news = run_bronze_ingestion(["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"])

# 2. Transform Silver & Gold
process_silver_gold_and_persist(prices, news)

# 3. Generate 384-dim Embeddings & Store in pgvector
count = generate_and_store_news_embeddings()
print(f"Embedded {count} news articles into Lakebase pgvector table.")
```

### Vector Search Engine (`src/rag/vector_search.py`)
Queries execute semantic vector similarity using PostgreSQL's cosine operator `<=>`:
$$\text{Similarity Score} = 1 - (\text{embedding} \Leftrightarrow \text{query\_vector})$$

Example Vector Search Query:
```python
from src.rag.vector_search import search_news_vector

results = search_news_vector("AI data center expansion and high cloud compute demand", ticker="NVDA", top_k=5)
for r in results:
    print(r["title"], "| Similarity:", r["similarity_score"])
```

---

## 7. AI Agent Copilot & ReAct Tools

The AI Agent (`src/agent/agent_engine.py`) receives natural language user commands, parses intent, and selects from 7 specialized database tools:

| Tool Function | Type | Description |
| :--- | :--- | :--- |
| `tool_search_news_rag` | **READ** | Searches news text embeddings via pgvector cosine similarity |
| `tool_get_ticker_snapshot` | **READ** | Pulls real-time prices, volume, P/E ratio, and market cap |
| `tool_get_watchlist` | **READ** | Fetches the user's current watchlist from Lakebase |
| `tool_add_to_watchlist` | **WRITE** | Mutates Lakebase table to add/update stock watchlist targets |
| `tool_remove_from_watchlist`| **WRITE** | Deletes stock entry from user's watchlist |
| `tool_save_research_note` | **WRITE** | Inserts structured research note into `research_notes` table |
| `tool_generate_analysis_report`| **WRITE** | Generates & persists BUY/HOLD/SELL stock report into Lakebase |

### Example Agent Commands
- `"Add NVDA to my watchlist with target buy 120"`
- `"Search news about Apple AI data centers"`
- `"Generate a BUY analysis report for TSLA"`
- `"Show my current portfolio watchlist"`

---

## 8. Databricks Workspace App Deployment

To deploy this application natively as a **Databricks App** using Databricks Asset Bundles (DABs):

### Step 8.1: Authenticate Databricks CLI
```bash
databricks auth login --host https://<your-databricks-workspace-url>
```

### Step 8.2: Configure Secret Scope (Databricks Workspace)
Create the required secret scope in Databricks workspace:
```bash
databricks secrets create-scope massive
databricks secrets put-secret massive api-key --string-value "your_massive_api_key"

databricks secrets create-scope database
databricks secrets put-secret database lakebase-url --string-value "postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require"
```

### Step 8.3: Validate Bundle Config (`databricks.yml`)
Ensure `databricks.yml` is configured properly:
```yaml
bundle:
  name: capstone_stock_copilot

resources:
  apps:
    stock_copilot_app:
      name: stock-copilot-app
      target: dev
      source_code_path: .

targets:
  dev:
    mode: development
    default: true
```

### Step 8.4: Deploy to Databricks Workspace
Run the deployment commands:
```bash
databricks bundle deploy --target dev
databricks apps deploy stock-copilot-app
```

The Databricks CLI will output the deployed App URL in your workspace (e.g. `https://<workspace-url>/apps/stock-copilot-app`).

---

## 9. Verification & End-to-End Testing Checklist

To verify that all components are functioning properly:

1. **Database Check**: Run `python -c "from src.lakebase import run_query; print(run_query('SELECT count(*) FROM companies;'))"`. Should return count of companies.
2. **Streamlit App Launch**: Execute `streamlit run app.py`. Ensure app opens at `http://localhost:8501`.
3. **ETL Data Trigger**: In sidebar, click **"🔄 Trigger PySpark ETL & RAG Pipeline"**. Confirm green success banner indicating embeddings stored.
4. **Vector RAG Search**: Navigate to Tab 2 (**Unstructured Vector RAG**). Search for `"AI data center expansion"`. Confirm search results display with similarity scores > 0.40.
5. **AI Copilot Mutation**: Navigate to Tab 4 (**AI Agent Copilot**). Type `"Add NVDA to my watchlist with target buy 120"`. Confirm `⚡ Action Executed` badge appears.
6. **Watchlist Persistence**: Navigate to Tab 3 (**Portfolio Watchlist**). Confirm `NVDA` appears in the Lakebase table with Target Buy `$120.00`.

---

## 10. Troubleshooting & Common FAQs

### Issue 1: `ImportError: No module named 'psycopg2'` in Local Environment
- **Cause**: `psycopg2-binary` is omitted from `requirements.txt` to prevent conflicts on Databricks Apps.
- **Solution**: Install locally via `pip install psycopg2-binary`.

### Issue 2: `psycopg2.OperationalError: SSL error: certificate verify failed`
- **Cause**: Database connection URL missing SSL specification.
- **Solution**: Ensure `?sslmode=require` is appended to `LAKEBASE_URL` in `.env`.

### Issue 3: `pyspark` Not Installed Warning
- **Cause**: PySpark is optional in local standalone mode.
- **Solution**: The application gracefully falls back to local pandas processing when native `pyspark` is absent. For local PySpark execution, install Java 8/11 and run `pip install pyspark`.

### Issue 4: `sentence-transformers` Model Download Delays
- **Cause**: `all-MiniLM-L6-v2` downloads ~90 MB model weights on first execution.
- **Solution**: The model is cached automatically after first download. If offline, the code includes a deterministic hash-based fallback encoder (`embeddings.py`).

---

**Congratulations! Your AI Stock Market Research Assistant & Investment Copilot is fully configured and ready for production use on Databricks Apps & Lakebase.**
