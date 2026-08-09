"""
LakePulse AI — Enterprise Stock Market Research Assistant & Investment Copilot
Databricks Apps Main Entrypoint.

Modular Production Architecture:
  components/  -> styles, navbar, sidebar
  views/       -> market_intelligence, vector_rag, portfolio_watchlist, ai_copilot, system_health
  src/         -> lakebase, massive_client, rag, agent, spark_pipeline
"""

import streamlit as st
from datetime import datetime
import uuid
import logging

from components.styles import inject_terminal_styles
from components.navbar import render_navbar
from components.sidebar import render_sidebar

from views.market_intelligence import render_market_intelligence
from views.vector_rag import render_vector_rag
from views.portfolio_watchlist import render_portfolio_watchlist
from views.ai_copilot import render_ai_copilot
from views.system_health import render_system_health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LakePulse AI | Enterprise Stock Copilot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SESSION IDENTITY ─────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8].upper()
if "session_started" not in st.session_state:
    st.session_state.session_started = datetime.now().strftime("%H:%M")
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello! I'm your **LakePulse AI Copilot**. You can ask me to:\n\n"
            "- 🔍 `Search AI infrastructure news for NVDA`\n"
            "- 📊 `Generate a BUY analysis report for AAPL`\n"
            "- ➕ `Add MSFT to my watchlist at 420`\n"
            "- 📋 `Show my current portfolio watchlist`\n"
            "- 📝 `Save a research note for TSLA`"
        ),
        "actions": [],
        "ts": datetime.now().strftime("%H:%M"),
    }]

SID = st.session_state.session_id

# ─── INJECT DESIGN SYSTEM STYLES ──────────────────────────────────────────────
inject_terminal_styles()

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def fmt_date(val):
    if val is None: return "—"
    if isinstance(val, datetime): return val.strftime("%Y-%m-%d")
    try: return str(val)[:10]
    except: return str(val)

def fmt_ts(val):
    if val is None: return "—"
    if isinstance(val, datetime): return val.strftime("%b %d, %H:%M")
    try: return str(val)[:16]
    except: return str(val)

def safe_str(val, fallback="—"):
    return fallback if val is None else str(val)

def safe_num(val, fallback=0.0):
    if val is None: return fallback
    try: return float(val)
    except: return fallback

def sentiment_badge(s):
    s = str(s).lower() if s else "neutral"
    if "bull" in s: return "<span class='badge-bullish'>BULLISH</span>"
    if "bear" in s: return "<span class='badge-bearish'>BEARISH</span>"
    return "<span class='badge-neutral'>NEUTRAL</span>"

def dark_layout(fig, height=300, title="", show_legend=True):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#E8EDFF", size=10),
        title=dict(text=title, font=dict(size=12, color="#A5B4FC"), x=0) if title else None,
        margin=dict(l=8, r=8, t=32 if title else 8, b=8),
        height=height, showlegend=show_legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.07)",
                    borderwidth=1, font=dict(size=9)),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="#4B5568", tickfont=dict(color="#4B5568", size=9))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="#4B5568", tickfont=dict(color="#4B5568", size=9))
    return fig

def simulate_history(close, high, low, _open, days=45, seed=42):
    import random
    random.seed(seed)
    rows = []
    price = close * 0.88
    for i in range(days):
        date   = datetime.today() - timedelta(days=days - i)
        chg    = random.uniform(-0.023, 0.026)
        price  = max(price * (1 + chg), 1.0)
        rng    = price * random.uniform(0.008, 0.022)
        o = price + random.uniform(-rng/2, rng/2)
        c = price + random.uniform(-rng/2, rng/2)
        h = max(o, c) + random.uniform(0, rng/2)
        l = min(o, c) - random.uniform(0, rng/2)
        vol = int(random.uniform(0.7, 1.5) * 35_000_000)
        rows.append({"date": date, "open": o, "high": h, "low": l, "close": c, "volume": vol})
    rows[-1].update({"open": _open, "high": high, "low": low, "close": close})
    return rows

# ─── BACKEND LOADERS ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_backend():
    m = {}
    try:
        mod = __import__("src.lakebase", fromlist=["init_db","run_query","run_write"])
        m.update({"run_query": mod.run_query, "run_write": mod.run_write, "init_db": mod.init_db, "db_ok": True})
    except Exception as e:
        m.update({"db_ok": False, "db_error": str(e)})
    try:
        mod = __import__("src.massive_client", fromlist=["MassiveClient"])
        m.update({"client": mod.MassiveClient(), "client_ok": True})
    except Exception as e:
        m.update({"client_ok": False, "client_error": str(e)})
    try:
        mod = __import__("src.rag.vector_search", fromlist=["search_news_vector"])
        m.update({"search_news_vector": mod.search_news_vector, "rag_ok": True})
    except Exception as e:
        m.update({"rag_ok": False, "rag_error": str(e)})
    try:
        mod = __import__("src.agent.agent_engine", fromlist=["StockMarketAgent"])
        m.update({"agent": mod.StockMarketAgent(), "agent_ok": True})
    except Exception as e:
        m.update({"agent_ok": False, "agent_error": str(e)})
    return m

@st.cache_resource(show_spinner=False)
def init_pipeline():
    try:
        from src.lakebase import init_db
        from src.spark_pipeline.ingestion import run_bronze_ingestion
        from src.spark_pipeline.transformations import process_silver_gold_and_persist
        from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
        init_db()
        prices, news = run_bronze_ingestion(["AAPL","NVDA","MSFT","AMZN","GOOGL","TSLA"])
        process_silver_gold_and_persist(prices, news)
        generate_and_store_news_embeddings()
        return {"ok": True, "count": 1}
    except Exception as e:
        return {"ok": False, "message": str(e)}

backend = load_backend()
if "pipeline_init" not in st.session_state:
    st.session_state["pipeline_init"] = init_pipeline()

def run_query(sql, params=None):
    if not backend.get("db_ok", False): return []
    try: return backend["run_query"](sql, params)
    except Exception as e:
        logger.warning(f"run_query: {e}"); return []

def run_write(sql, params=None):
    if not backend.get("db_ok", False): return 0
    try: return backend["run_write"](sql, params)
    except Exception as e:
        logger.warning(f"run_write: {e}"); return 0

# ─── TICKERS & COMPANY FULL NAMES ─────────────────────────────────────────────
DEFAULT_TICKERS = ["NVDA","AAPL","MSFT","AMZN","GOOGL","TSLA"]
COMPANY_NAME_FALLBACKS = {
    "NVDA": "NVIDIA Corporation",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc.",
    "GOOGL": "Alphabet Inc.",
    "TSLA": "Tesla Inc.",
    "QQQ": "Invesco QQQ Trust",
    "SPY": "SPDR S&P 500 ETF",
    "META": "Meta Platforms Inc.",
    "AMD": "Advanced Micro Devices",
    "NFLX": "Netflix Inc.",
    "VXUS": "Vanguard Total International Stock ETF",
}

@st.cache_data(ttl=30, show_spinner=False)
def get_ticker_display_data():
    rows = run_query("SELECT ticker, name FROM companies ORDER BY ticker;")
    name_map = COMPANY_NAME_FALLBACKS.copy()
    tickers = list(DEFAULT_TICKERS)
    if rows:
        for r in rows:
            t = r["ticker"]
            n = r.get("name")
            if t not in tickers:
                tickers.append(t)
            if n:
                name_map[t] = n
    return tickers, name_map

ALL_TICKERS, TICKER_NAMES = get_ticker_display_data()

def get_ticker_label(ticker: str) -> str:
    name = TICKER_NAMES.get(ticker, f"{ticker} Corp")
    return f"{ticker} — {name}"

# ─── RENDER COMPONENTS ────────────────────────────────────────────────────────
render_sidebar(backend, init_pipeline, get_ticker_display_data, DEFAULT_TICKERS)
render_navbar(run_query, len(ALL_TICKERS), SID)

# ─── RENDER TAB VIEWS ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence",
    "🔍 Vector RAG Search",
    "⭐ Portfolio Watchlist",
    "🤖 AI Copilot Chat",
    "⚡ System Health",
])

with tab1:
    render_market_intelligence(
        run_query, run_write, backend,
        ALL_TICKERS, TICKER_NAMES, get_ticker_label,
        safe_num, safe_str, fmt_date, sentiment_badge,
        dark_layout, simulate_history, DEFAULT_TICKERS
    )

with tab2:
    render_vector_rag(
        run_write, backend, ALL_TICKERS, TICKER_NAMES,
        get_ticker_label, safe_num, safe_str, fmt_date,
        sentiment_badge, dark_layout
    )

with tab3:
    render_portfolio_watchlist(
        run_query, run_write, backend,
        TICKER_NAMES, get_ticker_label, get_ticker_display_data,
        safe_num, safe_str, fmt_date, fmt_ts, dark_layout
    )

with tab4:
    render_ai_copilot(backend, SID, safe_str)

with tab5:
    render_system_health(run_query, backend, SID, ALL_TICKERS)
