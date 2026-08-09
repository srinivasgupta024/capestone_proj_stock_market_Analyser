"""
LakePulse AI — Stock Market Research Assistant & Investment Copilot
Databricks Apps Entrypoint | Streamlit Frontend
Features:
  - Market Intelligence & Plotly Analytics
  - Unstructured Vector RAG (pgvector)
  - Portfolio Watchlist (Lakebase CRUD)
  - AI ReAct Agent Copilot
  - Pipeline & System Telemetry
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LakePulse AI | Stock Market Copilot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DESIGN SYSTEM CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

  /* Global background */
  .stApp { background: #0C0E16; }
  section[data-testid="stSidebar"] { background: #111420 !important; border-right: 1px solid rgba(255,255,255,0.06); }

  /* Sidebar logo area */
  .sidebar-brand { padding: 0 0 16px 0; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08); }

  /* Metric Cards */
  [data-testid="stMetric"] {
    background: linear-gradient(135deg,rgba(30,35,60,0.9) 0%,rgba(16,20,40,0.9) 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 14px;
    padding: 18px 22px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  }
  [data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.5);
  }
  [data-testid="stMetricLabel"] { font-size: 0.78rem !important; color: #8892A4 !important; letter-spacing: 0.04em; text-transform: uppercase; }
  [data-testid="stMetricValue"] { font-size: 1.7rem !important; font-weight: 700 !important; color: #E8EDFF !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 0.86rem;
    color: #8892A4;
    background: transparent !important;
    border: none !important;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.18) !important;
    color: #A5B4FC !important;
  }

  /* Buttons */
  .stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.87rem;
    padding: 9px 18px;
    border: 1px solid rgba(99,102,241,0.4);
    background: rgba(99,102,241,0.12);
    color: #A5B4FC;
    transition: all 0.18s ease;
  }
  .stButton > button:hover {
    background: rgba(99,102,241,0.28);
    border-color: rgba(99,102,241,0.7);
    transform: translateY(-1px);
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6366F1 0%,#4F46E5 100%);
    color: #fff;
    border: none;
  }

  /* Inputs */
  .stTextInput input, .stSelectbox div, .stNumberInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8EDFF !important;
  }
  .stSlider { padding: 4px 0; }

  /* Chat bubbles */
  [data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    margin-bottom: 10px;
  }

  /* Custom badges */
  .badge-bullish { background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.35); padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-bearish { background:rgba(239,68,68,0.15);  color:#F87171; border:1px solid rgba(239,68,68,0.35);  padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-neutral { background:rgba(245,158,11,0.15); color:#FCD34D; border:1px solid rgba(245,158,11,0.35); padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }
  .badge-action  { background:rgba(99,102,241,0.18); color:#A5B4FC; border:1px solid rgba(99,102,241,0.4); padding:3px 12px; border-radius:20px; font-size:0.80rem; font-weight:700; display:inline-block; margin:4px 0; }
  .badge-rag     { background:rgba(14,165,233,0.15); color:#38BDF8; border:1px solid rgba(14,165,233,0.35); padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:700; }

  /* Section headers */
  .section-header { font-size:1.12rem; font-weight:700; color:#E8EDFF; margin-bottom:4px; }
  .section-sub { font-size:0.82rem; color:#8892A4; margin-bottom:16px; }

  /* News card */
  .news-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.18s;
  }
  .news-card:hover { border-color: rgba(99,102,241,0.3); }
  .news-title { font-size: 0.93rem; font-weight: 600; color: #E8EDFF; }
  .news-meta  { font-size: 0.78rem; color: #8892A4; margin-top: 4px; }

  /* Tool panel */
  .tool-row { padding: 8px 14px; border-radius: 8px; background: rgba(255,255,255,0.03); border-left: 3px solid rgba(99,102,241,0.5); margin-bottom: 8px; font-size: 0.84rem; }

  /* Expander */
  .streamlit-expanderHeader { font-weight: 600; }

  /* Divider */
  hr { border-color: rgba(255,255,255,0.07) !important; margin: 24px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def fmt_date(val):
    """Safely format any date/datetime value to YYYY-MM-DD string."""
    if val is None:
        return "N/A"
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    try:
        return str(val)[:10]
    except Exception:
        return str(val)

def safe_str(val, fallback="N/A"):
    """Safely convert a value to string, returning fallback if None."""
    if val is None:
        return fallback
    return str(val)

def sentiment_badge(sentiment: str) -> str:
    """Return HTML badge markup for a sentiment string."""
    s = str(sentiment).lower() if sentiment else "neutral"
    if "bull" in s:
        return "<span class='badge-bullish'>BULLISH</span>"
    elif "bear" in s:
        return "<span class='badge-bearish'>BEARISH</span>"
    else:
        return "<span class='badge-neutral'>NEUTRAL</span>"

def sentiment_emoji(sentiment: str) -> str:
    s = str(sentiment).lower() if sentiment else ""
    if "bull" in s: return "🟢"
    if "bear" in s: return "🔴"
    return "🟡"

# ─── APP IMPORTS (guarded to show useful errors, not crash) ───────────────────
@st.cache_resource(show_spinner=False)
def load_backend():
    """Load all backend modules once and cache. Returns a dict of callables or errors."""
    modules = {}
    try:
        from src.lakebase import init_db, run_query, run_write
        modules["run_query"] = run_query
        modules["run_write"] = run_write
        modules["init_db"]   = init_db
        modules["db_ok"]     = True
    except Exception as e:
        modules["db_ok"]    = False
        modules["db_error"] = str(e)

    try:
        from src.massive_client import MassiveClient
        modules["client"]    = MassiveClient()
        modules["client_ok"] = True
    except Exception as e:
        modules["client_ok"]    = False
        modules["client_error"] = str(e)

    try:
        from src.rag.vector_search import search_news_vector
        modules["search_news_vector"] = search_news_vector
        modules["rag_ok"]             = True
    except Exception as e:
        modules["rag_ok"]    = False
        modules["rag_error"] = str(e)

    try:
        from src.agent.agent_engine import StockMarketAgent
        modules["agent"]    = StockMarketAgent()
        modules["agent_ok"] = True
    except Exception as e:
        modules["agent_ok"]    = False
        modules["agent_error"] = str(e)

    return modules


@st.cache_resource(show_spinner=False)
def init_pipeline():
    """Run DB init + data pipeline once on cold start (cached)."""
    try:
        from src.lakebase import init_db
        from src.spark_pipeline.ingestion import run_bronze_ingestion
        from src.spark_pipeline.transformations import process_silver_gold_and_persist
        from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
        init_db()
        prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
        process_silver_gold_and_persist(prices, news)
        generate_and_store_news_embeddings()
        return {"ok": True, "message": "Pipeline initialised successfully"}
    except Exception as e:
        return {"ok": False, "message": str(e)}


# ─── LOAD EVERYTHING ──────────────────────────────────────────────────────────
backend = load_backend()

# Run pipeline in background (non-blocking for UI)
if "pipeline_init" not in st.session_state:
    with st.spinner("🚀 Initialising LakePulse AI pipeline... (first-time only)"):
        result = init_pipeline()
    st.session_state["pipeline_init"] = result

# Convenience aliases
_db_ok      = backend.get("db_ok", False)
_client_ok  = backend.get("client_ok", False)
_rag_ok     = backend.get("rag_ok", False)
_agent_ok   = backend.get("agent_ok", False)

def run_query(sql, params=None):
    if not _db_ok:
        return []
    try:
        return backend["run_query"](sql, params)
    except Exception as e:
        logger.warning(f"run_query error: {e}")
        return []

def run_write(sql, params=None):
    if not _db_ok:
        return 0
    try:
        return backend["run_write"](sql, params)
    except Exception as e:
        logger.warning(f"run_write error: {e}")
        return 0

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
    try:
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=160)
    except Exception:
        st.markdown("### 🔥 Databricks")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### System Status")
    st.markdown(f"{'🟢' if _db_ok else '🔴'} **Lakebase (pgvector):** {'Online' if _db_ok else 'Error'}")
    st.markdown(f"{'🟢' if _client_ok else '🟡'} **Market Data Client:** {'Active' if _client_ok else 'Fallback Mode'}")
    st.markdown(f"{'🟢' if _rag_ok else '🔴'} **Vector RAG Engine:** {'384-dim HNSW' if _rag_ok else 'Unavailable'}")
    st.markdown(f"{'🟢' if _agent_ok else '🔴'} **AI ReAct Agent:** {'Online' if _agent_ok else 'Unavailable'}")

    if not backend.get("pipeline_init", {}).get("ok", True):
        st.warning(f"⚠️ Pipeline: {st.session_state.get('pipeline_init', {}).get('message', '')[:80]}")

    st.markdown("---")
    st.markdown("### Data Pipeline")
    if st.button("🔄 Refresh ETL & RAG Pipeline", use_container_width=True):
        with st.spinner("Running PySpark Bronze → Silver → Gold ETL..."):
            try:
                from src.spark_pipeline.ingestion import run_bronze_ingestion
                from src.spark_pipeline.transformations import process_silver_gold_and_persist
                from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
                prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
                process_silver_gold_and_persist(prices, news)
                count = generate_and_store_news_embeddings()
                st.success(f"✅ ETL complete — {count} embeddings refreshed")
                # Clear pipeline cache so it re-runs
                init_pipeline.clear()
            except Exception as e:
                st.error(f"Pipeline error: {e}")

    st.markdown("---")
    st.caption("© 2026 LakePulse AI — Databricks Capstone\nBuilt with Streamlit + Lakebase pgvector")

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("📈 LakePulse AI")
    st.caption("Enterprise-grade financial intelligence — Databricks Lakebase · PySpark Medallion ETL · pgvector RAG · ReAct AI Agent")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence",
    "🔍 Vector RAG Search",
    "⭐ Portfolio Watchlist",
    "🤖 AI Agent Copilot",
    "⚡ System Health",
])

TICKERS = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI row
    kpi = st.columns(5)
    kpi_data = [
        ("Tracked Tickers",   "SELECT COUNT(*) AS c FROM companies",          "c", lambda v: f"{v}"),
        ("Portfolio Items",   "SELECT COUNT(*) AS c FROM watchlist_tickers",  "c", lambda v: f"{v}"),
        ("News Articles",     "SELECT COUNT(*) AS c FROM news_articles",      "c", lambda v: f"{v}"),
        ("Vector Embeddings", "SELECT COUNT(*) AS c FROM news_embeddings",    "c", lambda v: f"{v}"),
        ("Price Snapshots",   "SELECT COUNT(*) AS c FROM price_snapshots",    "c", lambda v: f"{v}"),
    ]
    for col, (label, sql, field, fmt) in zip(kpi, kpi_data):
        rows = run_query(sql)
        val  = rows[0][field] if rows else 0
        col.metric(label, fmt(val))

    st.markdown("---")

    # Ticker selector + live quote
    sel_col, spacer = st.columns([1, 3])
    with sel_col:
        selected = st.selectbox("Select Ticker", TICKERS, index=0, label_visibility="collapsed",
                                help="Pick a stock to inspect")
    st.markdown(f"### {selected} — Daily Market Snapshot")

    # Fetch quote
    quote = {}
    if _client_ok:
        try:
            quote = backend["client"].get_ticker_quote(selected)
        except Exception as e:
            st.error(f"Could not load quote: {e}")

    if quote:
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Close Price", f"${quote.get('close_price', 0):.2f}")
        q2.metric("Open Price",  f"${quote.get('open_price', 0):.2f}")
        q3.metric("Day High",    f"${quote.get('high_price', 0):.2f}")
        q4.metric("Day Low",     f"${quote.get('low_price', 0):.2f}")

    chart_col, info_col = st.columns([3, 2])

    with chart_col:
        if quote:
            labels  = ["Open", "Low", "Close", "High"]
            values  = [quote.get("open_price",0), quote.get("low_price",0),
                       quote.get("close_price",0), quote.get("high_price",0)]
            colors  = ["#6366F1", "#EF4444", "#10B981", "#F59E0B"]

            fig = go.Figure(go.Bar(
                x=labels, y=values,
                marker=dict(color=colors, line=dict(width=0)),
                text=[f"${v:.2f}" for v in values],
                textposition="outside",
                textfont=dict(color="#E8EDFF", size=12),
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Price ($)"),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                margin=dict(l=10, r=10, t=20, b=10),
                height=280,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    with info_col:
        st.markdown("#### Company Fundamentals")
        comp_rows = run_query("SELECT * FROM companies WHERE ticker = %s;", (selected,))
        if comp_rows:
            c = comp_rows[0]
            st.markdown(f"**{safe_str(c.get('name'))}**")
            st.markdown(f"`{safe_str(c.get('sector'))}` · `{safe_str(c.get('industry'))}`")
            mcap = c.get('market_cap', 0) or 0
            st.markdown(f"Market Cap: **${mcap/1e12:.2f}T**")
            st.markdown(f"P/E Ratio: **{safe_str(c.get('pe_ratio'))}x** · Div Yield: **{safe_str(c.get('dividend_yield'))}%**")
            desc = safe_str(c.get('description'), "")
            if desc:
                st.info(desc)
        else:
            st.caption("Company data loading...")

    # News feed
    st.markdown("---")
    st.markdown("#### 📰 Latest News")
    news_rows = run_query(
        "SELECT ticker, title, publisher, published_utc, sentiment, article_url "
        "FROM news_articles WHERE ticker = %s ORDER BY published_utc DESC LIMIT 5;",
        (selected,)
    )
    if news_rows:
        for n in news_rows:
            badge = sentiment_badge(n.get("sentiment"))
            date  = fmt_date(n.get("published_utc"))
            url   = safe_str(n.get("article_url"), "#")
            title = safe_str(n.get("title"), "Market Update")
            pub   = safe_str(n.get("publisher"), "—")
            st.markdown(
                f"<div class='news-card'>"
                f"<div class='news-title'>{badge}&nbsp; {title}</div>"
                f"<div class='news-meta'>{pub} · {date} &nbsp;·&nbsp; "
                f"<a href='{url}' target='_blank' style='color:#6366F1;'>Read ↗</a></div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No news articles indexed for this ticker yet. Click **Refresh ETL** in the sidebar.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VECTOR RAG SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 Semantic Vector RAG Explorer")
    st.caption("Powered by `all-MiniLM-L6-v2` → 384-dim embeddings stored in Lakebase pgvector HNSW index.")

    # Quick-query chips
    CHIPS = {
        "☁️ AI Cloud Expansion":  "companies expanding AI data center infrastructure and high cloud compute demand",
        "🚀 Earnings Beat":       "record quarterly revenue beat and expanding profit margins",
        "📉 Rate Sensitivity":    "Federal Reserve interest rate outlook and supply chain risk analysis",
        "🚗 EV & Autonomy":       "electric vehicles self-driving autonomous AI hardware deployment",
    }

    chip_cols = st.columns(len(CHIPS))
    preset_query = None
    for col, (label, qtext) in zip(chip_cols, CHIPS.items()):
        if col.button(label, use_container_width=True):
            preset_query = qtext

    col_q, col_f, col_k = st.columns([4, 1, 1])
    with col_q:
        search_query = st.text_input(
            "Semantic query", 
            value=preset_query or "AI infrastructure data center high compute enterprise demand",
            key="rag_q"
        )
    with col_f:
        filter_ticker = st.selectbox("Ticker filter", ["All"] + TICKERS, key="rag_tick")
    with col_k:
        top_k = st.slider("Top K", 1, 10, 5, key="rag_k")

    ticker_param = None if filter_ticker == "All" else filter_ticker

    if not _rag_ok:
        st.error(f"⚠️ RAG engine unavailable: {backend.get('rag_error', 'Unknown error')}")
    else:
        if st.button("🔍 Run Semantic Search", use_container_width=True, type="primary"):
            with st.spinner("Computing query vector & searching pgvector index..."):
                try:
                    results = backend["search_news_vector"](search_query, ticker=ticker_param, top_k=top_k)
                    st.session_state["rag_results"] = results
                    st.session_state["rag_query"]   = search_query
                except Exception as e:
                    st.error(f"Vector search failed: {e}")
                    st.session_state["rag_results"] = []

        results = st.session_state.get("rag_results", [])
        if results:
            st.success(f"Found **{len(results)}** semantically relevant documents for: *\"{st.session_state.get('rag_query','')}\"*")
            for i, r in enumerate(results):
                score = r.get("similarity_score", 0) or 0
                tick  = safe_str(r.get("ticker"), "—")
                title = safe_str(r.get("title"), "Article")
                pub   = safe_str(r.get("publisher"), "—")
                sent  = safe_str(r.get("sentiment"), "neutral")
                chunk = safe_str(r.get("chunk_text"), "")
                url   = safe_str(r.get("article_url"), "#")
                date  = fmt_date(r.get("published_utc"))
                badge = sentiment_badge(sent)

                bar_pct = int(score * 100)
                with st.expander(f"#{i+1}  [{tick}] {title[:80]}...   — {score:.3f} relevance"):
                    c1, c2 = st.columns([1, 5])
                    c1.markdown(f"**{score:.3f}**\n\n<small>relevance</small>", unsafe_allow_html=True)
                    c2.progress(min(bar_pct, 100))
                    st.markdown(
                        f"{badge} <span class='badge-rag'>pgvector cosine</span> &nbsp; **{pub}** · {date}",
                        unsafe_allow_html=True
                    )
                    if chunk:
                        st.markdown(f"> {chunk[:400]}{'...' if len(chunk)>400 else ''}")
                    if url != "#":
                        st.markdown(f"[🔗 Read full article]({url})")
        elif "rag_results" in st.session_state:
            st.warning("No matching documents found. Try a different query or click **Refresh ETL** to re-embed news.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PORTFOLIO WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ⭐ Portfolio Watchlist")
    st.caption("Live read/write operations against Lakebase `watchlist_tickers` table.")

    # ── Live watchlist table ──
    wl_rows = run_query("""
        SELECT wt.ticker,
               COALESCE(c.name, wt.ticker) AS name,
               wt.target_buy_price,
               wt.target_sell_price,
               wt.notes,
               wt.added_at
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)

    if wl_rows:
        df_wl = pd.DataFrame(wl_rows)
        # Safely format date column
        if "added_at" in df_wl.columns:
            df_wl["added_at"] = df_wl["added_at"].apply(fmt_date)
        st.dataframe(
            df_wl.rename(columns={
                "ticker": "Ticker",
                "name": "Company",
                "target_buy_price": "Buy Target ($)",
                "target_sell_price": "Sell Target ($)",
                "notes": "Thesis Notes",
                "added_at": "Added Date",
            }),
            use_container_width=True,
            hide_index=True,
        )

        # Mini price bar chart for watchlist tickers
        if _client_ok and wl_rows:
            wl_tickers = [r["ticker"] for r in wl_rows]
            chart_data = []
            for t in wl_tickers:
                try:
                    q = backend["client"].get_ticker_quote(t)
                    chart_data.append({"Ticker": t, "Close ($)": q.get("close_price", 0)})
                except Exception:
                    pass
            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                fig2 = px.bar(
                    df_chart, x="Ticker", y="Close ($)",
                    color="Ticker", text="Close ($)",
                    color_discrete_sequence=["#6366F1","#10B981","#F59E0B","#EF4444","#3B82F6","#8B5CF6"],
                )
                fig2.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
                fig2.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    height=260,
                    showlegend=False,
                    margin=dict(l=10,r=10,t=20,b=10),
                )
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Your watchlist is empty. Add your first ticker below!")

    st.markdown("---")
    add_col, del_col = st.columns(2)

    with add_col:
        st.markdown("#### ➕ Add / Update Ticker")
        with st.form("wl_add_form", clear_on_submit=False):
            t_pick = st.selectbox("Ticker", TICKERS, key="wl_add_tick")
            buy_p  = st.number_input("Target Buy Price ($)", min_value=0.0, value=120.0, step=5.0)
            sell_p = st.number_input("Target Sell Price ($)", min_value=0.0, value=160.0, step=5.0)
            thesis = st.text_area("Investment Thesis", "Strong structural tailwinds in AI compute infrastructure.", height=80)
            if st.form_submit_button("💾 Save to Lakebase", use_container_width=True, type="primary"):
                run_write(
                    "INSERT INTO companies (ticker, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                    (t_pick, f"{t_pick} Corp")
                )
                run_write("""
                    INSERT INTO watchlist_tickers
                        (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
                    VALUES ('default_watchlist', %s, %s, %s, %s)
                    ON CONFLICT (watchlist_id, ticker) DO UPDATE SET
                        target_buy_price = EXCLUDED.target_buy_price,
                        target_sell_price = EXCLUDED.target_sell_price,
                        notes = EXCLUDED.notes;
                """, (t_pick, buy_p, sell_p, thesis))
                st.success(f"✅ {t_pick} saved to Lakebase watchlist!")
                st.rerun()

    with del_col:
        st.markdown("#### 🗑️ Remove Ticker")
        with st.form("wl_del_form", clear_on_submit=False):
            t_del = st.selectbox("Ticker to Remove", TICKERS, key="wl_del_tick")
            if st.form_submit_button("Remove from Watchlist", use_container_width=True):
                cnt = run_write(
                    "DELETE FROM watchlist_tickers WHERE watchlist_id='default_watchlist' AND ticker=%s;",
                    (t_del,)
                )
                if cnt > 0:
                    st.success(f"✅ Removed {t_del}")
                else:
                    st.warning(f"{t_del} was not in your watchlist")
                st.rerun()

    st.markdown("---")
    note_col, report_col = st.columns(2)

    with note_col:
        st.markdown("#### 📝 Research Notes")
        note_rows = run_query(
            "SELECT ticker, title, content, created_at FROM research_notes ORDER BY created_at DESC LIMIT 6;"
        )
        if note_rows:
            for n in note_rows:
                with st.expander(f"[{safe_str(n.get('ticker'))}] {safe_str(n.get('title'))[:60]}"):
                    st.write(safe_str(n.get("content")))
                    st.caption(f"📅 {fmt_date(n.get('created_at'))}")
        else:
            st.caption("No notes yet. Ask the AI Agent to save a research note!")

    with report_col:
        st.markdown("#### 📊 Analysis Reports")
        rep_rows = run_query(
            "SELECT ticker, recommendation, summary, bull_case, bear_case, created_at "
            "FROM analysis_reports ORDER BY created_at DESC LIMIT 6;"
        )
        if rep_rows:
            for r in rep_rows:
                rec = safe_str(r.get("recommendation"), "HOLD")
                ico = "🟢" if rec == "BUY" else ("🔴" if rec == "SELL" else "🟡")
                with st.expander(f"{ico} [{safe_str(r.get('ticker'))}] {rec} · {fmt_date(r.get('created_at'))}"):
                    st.write(f"**Summary:** {safe_str(r.get('summary'))}")
                    st.write(f"**Bull Case:** {safe_str(r.get('bull_case'))}")
                    st.write(f"**Bear Case:** {safe_str(r.get('bear_case'))}")
        else:
            st.caption("No reports yet. Ask the AI Agent to generate an analysis report!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI AGENT COPILOT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🤖 AI Investment Copilot")
    st.caption("ReAct agent with READ (RAG search, quotes, watchlist) and WRITE (add/remove, notes, reports) tools.")

    if not _agent_ok:
        st.error(f"⚠️ AI Agent unavailable: {backend.get('agent_error', 'Unknown error')}")
    else:
        # Chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    "Hi! I'm your AI Investment Copilot powered by Databricks Lakebase. "
                    "You can ask me to:\n"
                    "- 🔍 **Search** market news: *'Search AI infrastructure news for NVDA'*\n"
                    "- 📊 **Analyse** a stock: *'Generate a BUY report for AAPL'*\n"
                    "- ➕ **Add** to watchlist: *'Add MSFT to my watchlist at 420'*\n"
                    "- 📋 **Show** my portfolio: *'Show my watchlist'*\n"
                    "- 📝 **Save** a note: *'Save a research note for TSLA'*"
                ),
                "actions": []
            }]

        # Render chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                for act in msg.get("actions", []):
                    st.markdown(f"<span class='badge-action'>⚡ {act}</span>", unsafe_allow_html=True)

        # Quick command buttons
        st.markdown("**Quick Commands:**")
        qc = st.columns(4)
        qp = None
        if qc[0].button("➕ Add NVDA @ 120", use_container_width=True):   qp = "Add NVDA to my watchlist with target buy 120"
        if qc[1].button("🔍 AI News AAPL", use_container_width=True):     qp = "Search news about Apple artificial intelligence"
        if qc[2].button("📊 Analyse TSLA", use_container_width=True):     qp = "Generate a BUY analysis report for TSLA"
        if qc[3].button("📋 My Watchlist", use_container_width=True):     qp = "Show my current portfolio watchlist"

        user_input = st.chat_input("Ask the AI Agent anything about your portfolio or the market...") or qp

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input, "actions": []})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("AI Agent selecting tools and reasoning..."):
                    try:
                        response = backend["agent"].run(user_input)
                        answer   = safe_str(response.get("answer", ""), "No response.")
                        actions  = response.get("actions_taken", [])
                        st.markdown(answer)
                        for act in actions:
                            st.markdown(f"<span class='badge-action'>⚡ {act}</span>", unsafe_allow_html=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "actions": actions
                        })
                    except Exception as e:
                        err_msg = f"Agent error: {e}"
                        st.error(err_msg)
                        st.session_state.messages.append({"role": "assistant", "content": err_msg, "actions": []})

        st.markdown("---")
        with st.expander("🛠️ Available Agent Tools"):
            tools = [
                ("tool_search_news_rag",         "READ",  "Semantic vector search over pgvector 384-dim news embeddings"),
                ("tool_get_ticker_snapshot",      "READ",  "Live/fallback market price, volume, and company fundamentals"),
                ("tool_get_watchlist",            "READ",  "List portfolio tickers with target prices from Lakebase"),
                ("tool_add_to_watchlist",         "WRITE", "INSERT/UPSERT ticker into watchlist_tickers table"),
                ("tool_remove_from_watchlist",    "WRITE", "DELETE ticker from watchlist_tickers table"),
                ("tool_save_research_note",       "WRITE", "Write research note into research_notes table"),
                ("tool_generate_analysis_report", "WRITE", "Generate & persist BUY/HOLD/SELL report in analysis_reports table"),
            ]
            for name, rw, desc in tools:
                color = "#10B981" if rw == "READ" else "#6366F1"
                st.markdown(
                    f"<div class='tool-row'><code style='color:{color}'>{rw}</code> &nbsp; "
                    f"<strong>{name}</strong><br><span style='color:#8892A4'>{desc}</span></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SYSTEM HEALTH
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⚡ PySpark Medallion Pipeline & Database Health")

    st.markdown("#### Architecture")
    st.code("""
  Massive REST API
       │
       ▼
  [Bronze Layer]   ── PySpark raw ingestion (6 tickers × quotes + news)
       │
       ▼
  [Silver Layer]   ── Schema validation, sentiment enrichment, company upserts
       │
       ▼
  [Gold Layer]     ── Business aggregations, price snapshots
       │
       ▼
  Lakebase (PostgreSQL + pgvector)
       │
   ┌───┴────────────────────────────────┐
   │                                    │
   ▼                                    ▼
Relational Tables             news_embeddings (384-dim HNSW)
(companies, watchlist,        ← sentence-transformers all-MiniLM-L6-v2
 news_articles, reports…)     ← pgvector cosine similarity (<=>)
    """, language="text")

    st.markdown("---")
    st.markdown("#### Lakebase Table Record Audit")

    db_tables = [
        "users", "companies", "watchlists", "watchlist_tickers",
        "price_snapshots", "news_articles", "news_embeddings",
        "research_notes", "analysis_reports"
    ]
    audit = []
    for t in db_tables:
        try:
            r = run_query(f"SELECT COUNT(*) AS c FROM {t};")
            cnt = r[0]["c"] if r else 0
            audit.append({"Table": t, "Records": cnt, "Status": "✅ Active"})
        except Exception as ex:
            audit.append({"Table": t, "Records": 0, "Status": f"⚠️ {str(ex)[:40]}"})

    df_audit = pd.DataFrame(audit)
    st.dataframe(df_audit, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Pipeline Init Status")
    pi = st.session_state.get("pipeline_init", {})
    if pi.get("ok"):
        st.success(f"✅ {pi.get('message', 'Pipeline OK')}")
    else:
        st.error(f"⚠️ Pipeline Error: {pi.get('message', 'Unknown')}")
