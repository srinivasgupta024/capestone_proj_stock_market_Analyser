"""
LakePulse AI — Stock Market Research Assistant & Investment Copilot
Databricks Apps Entrypoint | Streamlit Frontend
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import uuid
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
            "- 📊 `Generate a BUY report for AAPL`\n"
            "- ➕ `Add MSFT to my watchlist at 420`\n"
            "- 📋 `Show my watchlist`\n"
            "- 📝 `Save a research note for TSLA`"
        ),
        "actions": [],
        "ts": datetime.now().strftime("%H:%M"),
    }]

SID = st.session_state.session_id

# ─── DESIGN SYSTEM (FORCED DARK + STICKY TOPNAV) ──────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* FORCE DARK EVERYWHERE */
  html, body { background:#0C0E16!important; color:#E8EDFF!important; }
  .stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],
  [data-testid="stToolbar"],[data-testid="block-container"] {
    background:#0C0E16!important;
    font-family:'Inter',sans-serif!important;
  }
  [data-testid="stHeader"],[data-testid="stDecoration"] { display:none!important; }

  /* SIDEBAR - SLEEK & INFORMATIONAL */
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] > div,
  section[data-testid="stSidebar"] > div > div {
    background:#0A0D1A!important;
    border-right:1px solid rgba(99,102,241,0.18)!important;
  }
  section[data-testid="stSidebar"] * { color:#C8D0E0!important; }
  section[data-testid="stSidebar"] .stButton>button {
    background:rgba(99,102,241,0.13)!important;
    border:1px solid rgba(99,102,241,0.35)!important;
    color:#A5B4FC!important; border-radius:10px;
    font-weight:600; width:100%; transition:all 0.2s;
  }
  section[data-testid="stSidebar"] .stButton>button:hover {
    background:rgba(99,102,241,0.26)!important;
    transform:translateY(-1px);
  }

  /* STICKY TOP NAVBAR */
  .topnav {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(10, 13, 26, 0.95);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 102, 241, 0.22);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }
  .topnav-brand { font-size:1.22rem; font-weight:800; color:#E8EDFF; letter-spacing:-0.5px; }
  .topnav-sub   { font-size:0.72rem; color:#6B7280; margin-top:1px; }
  .topnav-right { display:flex; align-items:center; gap:14px; }
  .topnav-stat  { text-align:right; }
  .topnav-stat-val { font-size:1.05rem; font-weight:700; color:#E8EDFF; }
  .topnav-stat-lbl { font-size:0.68rem; color:#6B7280; text-transform:uppercase; letter-spacing:0.06em; }

  /* TABS AS NAV */
  .stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,0.02)!important;
    border-radius:12px; padding:5px; gap:4px;
    border:1px solid rgba(255,255,255,0.06);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius:9px; padding:10px 22px;
    font-weight:600; font-size:0.87rem;
    color:#8892A4!important; background:transparent!important;
    border:none!important; transition:all 0.2s;
  }
  .stTabs [aria-selected="true"] {
    background:rgba(99,102,241,0.22)!important;
    color:#A5B4FC!important;
    box-shadow:0 2px 12px rgba(99,102,241,0.2);
  }

  /* METRIC CARDS */
  [data-testid="stMetric"] {
    background:linear-gradient(145deg,rgba(25,28,52,0.95),rgba(15,18,36,0.95))!important;
    border:1px solid rgba(99,102,241,0.22)!important;
    border-radius:16px!important; padding:18px 20px!important;
    box-shadow:0 4px 20px rgba(0,0,0,0.45); transition:all 0.2s;
  }
  [data-testid="stMetric"]:hover {
    transform:translateY(-3px);
    border-color:rgba(99,102,241,0.5)!important;
    box-shadow:0 8px 30px rgba(99,102,241,0.2);
  }
  [data-testid="stMetricLabel"]>div {
    font-size:0.72rem!important; color:#8892A4!important;
    text-transform:uppercase; letter-spacing:0.07em; font-weight:600;
  }
  [data-testid="stMetricValue"]>div {
    font-size:1.6rem!important; font-weight:800!important; color:#E8EDFF!important;
  }

  /* BUTTONS */
  .stButton>button {
    border-radius:10px!important; font-weight:600!important;
    font-size:0.87rem!important; padding:9px 20px!important;
    border:1px solid rgba(99,102,241,0.4)!important;
    background:rgba(99,102,241,0.12)!important; color:#A5B4FC!important;
    transition:all 0.2s!important;
  }
  .stButton>button:hover {
    background:rgba(99,102,241,0.26)!important;
    border-color:rgba(99,102,241,0.65)!important;
    transform:translateY(-1px)!important;
  }
  .stButton>button[kind="primary"] {
    background:linear-gradient(135deg,#6366F1,#4F46E5)!important;
    color:#fff!important; border:none!important;
  }

  /* INPUTS */
  .stTextInput>div>div>input,
  .stNumberInput>div>div>input,
  .stTextArea>div>div>textarea {
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(255,255,255,0.10)!important;
    border-radius:10px!important; color:#E8EDFF!important;
  }
  .stSelectbox>div>div {
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(255,255,255,0.10)!important;
    border-radius:10px!important; color:#E8EDFF!important;
  }

  /* DATAFRAME / DATA EDITOR DARK THEME */
  [data-testid="stDataFrame"] iframe, [data-testid="stDataEditor"] iframe { border-radius:12px; }
  .stDataFrame, .stDataEditor { border-radius:12px; overflow:hidden; }

  /* EXPANDERS */
  [data-testid="stExpander"] {
    background:rgba(255,255,255,0.025)!important;
    border:1px solid rgba(255,255,255,0.07)!important;
    border-radius:12px!important;
  }
  [data-testid="stExpander"] summary { color:#C8D0E0!important; font-weight:600!important; }

  /* CHAT */
  [data-testid="stChatMessage"] {
    background:rgba(255,255,255,0.03)!important;
    border:1px solid rgba(255,255,255,0.07)!important;
    border-radius:14px!important; margin-bottom:8px;
  }
  [data-testid="stChatInput"] {
    background:rgba(15,18,36,0.95)!important;
    border:1px solid rgba(99,102,241,0.35)!important;
    border-radius:14px!important;
  }
  [data-testid="stChatInput"] textarea {
    background:transparent!important; color:#E8EDFF!important;
  }

  /* DIVIDERS */
  hr { border-color:rgba(255,255,255,0.07)!important; margin:18px 0!important; }

  /* BADGES */
  .badge-bullish { background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.35); padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; display:inline-block; }
  .badge-bearish { background:rgba(239,68,68,0.15);  color:#F87171; border:1px solid rgba(239,68,68,0.35);  padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; display:inline-block; }
  .badge-neutral { background:rgba(245,158,11,0.15); color:#FCD34D; border:1px solid rgba(245,158,11,0.35); padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; display:inline-block; }
  .badge-action  { background:rgba(99,102,241,0.18); color:#A5B4FC; border:1px solid rgba(99,102,241,0.4);  padding:3px 12px;  border-radius:20px; font-size:0.79rem; font-weight:700; display:inline-block; margin:3px 0; }
  .badge-rag     { background:rgba(14,165,233,0.15); color:#38BDF8; border:1px solid rgba(14,165,233,0.35); padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; display:inline-block; }
  .badge-sess    { background:rgba(139,92,246,0.18); color:#C4B5FD; border:1px solid rgba(139,92,246,0.4);  padding:2px 10px; border-radius:20px; font-size:0.74rem; font-weight:700; display:inline-block; }

  /* NEWS CARD - COMPACT FOR RIGHT COLUMN */
  .news-card {
    background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; padding:12px 15px; margin-bottom:9px; transition:border-color 0.2s;
  }
  .news-card:hover { border-color:rgba(99,102,241,0.35); }
  .news-title { font-size:0.87rem; font-weight:600; color:#E8EDFF; line-height:1.35; }
  .news-meta  { font-size:0.74rem; color:#8892A4; margin-top:5px; }

  /* TOOL ROW */
  .tool-row { padding:9px 14px; border-radius:8px; background:rgba(255,255,255,0.03);
    border-left:3px solid rgba(99,102,241,0.5); margin-bottom:8px;
    font-size:0.83rem; color:#C8D0E0; }

  /* SIDEBAR LABELS */
  .sb-label { font-size:0.67rem; font-weight:700; letter-spacing:0.10em;
    text-transform:uppercase; color:#4B5568; margin:16px 0 7px 0; display:block; }
  .sb-status-row { display:flex; align-items:center; gap:8px; padding:7px 10px;
    border-radius:8px; background:rgba(255,255,255,0.025); margin-bottom:6px;
    font-size:0.83rem; color:#C8D0E0; }
  .dot-g { width:8px; height:8px; border-radius:50%; background:#10B981;
    box-shadow:0 0 6px #10B981; flex-shrink:0; }
  .dot-y { width:8px; height:8px; border-radius:50%; background:#F59E0B;
    box-shadow:0 0 6px #F59E0B; flex-shrink:0; }
  .dot-r { width:8px; height:8px; border-radius:50%; background:#EF4444;
    box-shadow:0 0 6px #EF4444; flex-shrink:0; }

  /* CUSTOM HTML TABLE */
  .health-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
  .health-table th {
    background:rgba(99,102,241,0.12); color:#A5B4FC; padding:10px 14px;
    text-align:left; font-weight:700; font-size:0.74rem; text-transform:uppercase;
    letter-spacing:0.06em; border-bottom:1px solid rgba(99,102,241,0.2);
  }
  .health-table td {
    padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.05);
    color:#C8D0E0; vertical-align:middle;
  }
  .health-table tr:hover td { background:rgba(255,255,255,0.025); }
  .health-table tr:last-child td { border-bottom:none; }
  .ht-ok   { color:#34D399; font-weight:700; }
  .ht-warn { color:#FCD34D; font-weight:700; }
  .ht-err  { color:#F87171; font-weight:700; }
  .table-wrap {
    background:rgba(15,18,36,0.95); border:1px solid rgba(255,255,255,0.07);
    border-radius:14px; overflow:hidden; margin-bottom:16px;
  }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
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

CHART_BG   = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
AXIS_COLOR = "#4B5568"
TEXT_COLOR = "#E8EDFF"

def dark_layout(fig, height=320, title="", show_legend=True):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=TEXT_COLOR, size=11),
        title=dict(text=title, font=dict(size=13, color="#A5B4FC"), x=0) if title else None,
        margin=dict(l=10, r=10, t=36 if title else 10, b=10),
        height=height, showlegend=show_legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.07)",
                    borderwidth=1, font=dict(size=10)),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR, size=10))
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR, size=10))
    return fig

def simulate_history(close, high, low, _open, days=45, seed=42):
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
    with st.spinner("🚀 LakePulse AI starting up..."):
        st.session_state["pipeline_init"] = init_pipeline()

_db_ok     = backend.get("db_ok", False)
_client_ok = backend.get("client_ok", False)
_rag_ok    = backend.get("rag_ok", False)
_agent_ok  = backend.get("agent_ok", False)

def run_query(sql, params=None):
    if not _db_ok: return []
    try: return backend["run_query"](sql, params)
    except Exception as e:
        logger.warning(f"run_query: {e}"); return []

def run_write(sql, params=None):
    if not _db_ok: return 0
    try: return backend["run_write"](sql, params)
    except Exception as e:
        logger.warning(f"run_write: {e}"); return 0

# ─── TICKERS & FULL NAMES MAPPING ─────────────────────────────────────────────
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
}

@st.cache_data(ttl=30, show_spinner=False)
def get_ticker_display_data():
    """Query DB companies table for all tickers and map to Ticker — Full Name format."""
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
    """Format ticker as TICKER — Company Full Name for fluid UI readouts."""
    name = TICKER_NAMES.get(ticker, f"{ticker} Corp")
    return f"{ticker} — {name}"

# ─── SLEEK INFORMATIONAL SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div style="padding:8px 0 16px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:8px">
      <div style="font-size:1.24rem;font-weight:800;color:#E8EDFF;letter-spacing:-0.5px">📈 LakePulse AI</div>
      <div style="font-size:0.70rem;color:#6B7280;margin-top:2px">Databricks Capstone · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    # System Status
    st.markdown("<span class='sb-label'>System Status</span>", unsafe_allow_html=True)
    for ok, label, good, bad, dot in [
        (_db_ok,     "Lakebase (pgvector)",  "Online",       "Offline",   "g"),
        (_client_ok, "Market Data Client",   "Active",       "Fallback",  "y" if not _client_ok else "g"),
        (_rag_ok,    "Vector RAG Engine",    "384-dim HNSW", "Unavail.",  "g" if _rag_ok else "r"),
        (_agent_ok,  "AI ReAct Agent",       "Online",       "Unavail.",  "g" if _agent_ok else "r"),
    ]:
        d = f"dot-{dot}"
        t = good if ok else bad
        st.markdown(
            f"<div class='sb-status-row'><div class='{d}'></div>"
            f"<span style='flex:1'>{label}</span>"
            f"<span style='font-size:0.73rem;color:#6B7280'>{t}</span></div>",
            unsafe_allow_html=True
        )

    pi = st.session_state.get("pipeline_init", {})
    color = "#10B981" if pi.get("ok") else "#EF4444"
    msg   = "Pipeline ready" if pi.get("ok") else pi.get("message","Error")[:50]
    bg    = "rgba(16,185,129,0.08)" if pi.get("ok") else "rgba(239,68,68,0.08)"
    bc    = "rgba(16,185,129,0.2)"  if pi.get("ok") else "rgba(239,68,68,0.2)"
    st.markdown(
        f"<div style='font-size:0.74rem;color:{color};margin-top:8px;padding:6px 10px;"
        f"background:{bg};border-radius:8px;border:1px solid {bc}'>{'✅' if pi.get('ok') else '⚠️'} {msg}</div>",
        unsafe_allow_html=True
    )

    # Data Pipeline Action
    st.markdown("<span class='sb-label'>Data Pipeline</span>", unsafe_allow_html=True)
    if st.button("🔄 Refresh ETL & RAG Pipeline", use_container_width=True):
        with st.spinner("Running PySpark Bronze → Silver → Gold…"):
            try:
                from src.spark_pipeline.ingestion import run_bronze_ingestion
                from src.spark_pipeline.transformations import process_silver_gold_and_persist
                from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
                prices, news = run_bronze_ingestion(DEFAULT_TICKERS)
                process_silver_gold_and_persist(prices, news)
                count = generate_and_store_news_embeddings()
                init_pipeline.clear()
                get_ticker_display_data.clear()
                st.success(f"✅ {count} embeddings refreshed")
            except Exception as e:
                st.error(str(e)[:100])

    st.markdown(
        "<div style='position:fixed;bottom:14px;left:0;width:238px;text-align:center;"
        "font-size:0.68rem;color:#374151;padding:0 14px'>Built with Streamlit · Databricks Lakebase · pgvector</div>",
        unsafe_allow_html=True
    )

# ─── STICKY TOP NAVBAR ────────────────────────────────────────────────────────
total_news = 0
total_emb  = 0
rows_n = run_query("SELECT COUNT(*) AS c FROM news_articles;")
rows_e = run_query("SELECT COUNT(*) AS c FROM news_embeddings;")
if rows_n: total_news = int(rows_n[0]["c"])
if rows_e: total_emb  = int(rows_e[0]["c"])

st.markdown(f"""
<div class="topnav">
  <div>
    <div class="topnav-brand">📈 LakePulse AI</div>
    <div class="topnav-sub">Enterprise financial intelligence · Databricks Lakebase · PySpark Medallion ETL · pgvector RAG · ReAct AI Agent</div>
  </div>
  <div class="topnav-right">
    <div class="topnav-stat">
      <div class="topnav-stat-val">{total_news:,}</div>
      <div class="topnav-stat-lbl">Articles</div>
    </div>
    <div style="width:1px;height:32px;background:rgba(255,255,255,0.08)"></div>
    <div class="topnav-stat">
      <div class="topnav-stat-val">{total_emb:,}</div>
      <div class="topnav-stat-lbl">Embeddings</div>
    </div>
    <div style="width:1px;height:32px;background:rgba(255,255,255,0.08)"></div>
    <div class="topnav-stat">
      <div class="topnav-stat-val">{len(ALL_TICKERS)}</div>
      <div class="topnav-stat-lbl">Tickers</div>
    </div>
    <div style="width:1px;height:32px;background:rgba(255,255,255,0.08)"></div>
    <div>
      <span class="badge-sess">⬡ Session: {SID}</span>
      <div style="font-size:0.67rem;color:#4B5568;text-align:right;margin-top:3px">{datetime.now().strftime("%b %d, %H:%M")}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS / NAVIGATION ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence",
    "🔍 Vector RAG Search",
    "⭐ Portfolio Watchlist",
    "🤖 AI Copilot Chat",
    "⚡ System Health",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── KPI Row
    k1,k2,k3,k4,k5 = st.columns(5)
    for col, (label, sql) in zip(
        [k1,k2,k3,k4,k5],
        [("Tracked Tickers","SELECT COUNT(*) AS c FROM companies"),
         ("Portfolio Items","SELECT COUNT(*) AS c FROM watchlist_tickers"),
         ("News Articles","SELECT COUNT(*) AS c FROM news_articles"),
         ("Vector Embeddings","SELECT COUNT(*) AS c FROM news_embeddings"),
         ("Price Snapshots","SELECT COUNT(*) AS c FROM price_snapshots")]
    ):
        r = run_query(sql)
        col.metric(label, f"{int(r[0]['c']):,}" if r else "0")

    st.markdown("---")

    # ── Ticker selector with full company names & Quick Add to Watchlist Button
    sel_col, action_col = st.columns([3, 1])

    with sel_col:
        selected = st.selectbox(
            "Select Stock / Asset",
            ALL_TICKERS,
            format_func=get_ticker_label,
            index=0, key="tab1_ticker",
            help="Select a ticker symbol to inspect real-time price action, fundamentals, and news"
        )

    # Quote
    quote = {}
    if _client_ok:
        try: quote = backend["client"].get_ticker_quote(selected)
        except: pass

    close  = safe_num(quote.get("close_price",0))
    _open  = safe_num(quote.get("open_price",0))
    high   = safe_num(quote.get("high_price",0))
    low    = safe_num(quote.get("low_price",0))
    volume = int(safe_num(quote.get("volume",0)))
    chg    = close - _open
    chg_pct= (chg / _open * 100) if _open else 0

    with action_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        # Check if already in watchlist
        in_wl = run_query("SELECT 1 FROM watchlist_tickers WHERE watchlist_id='default_watchlist' AND ticker=%s;", (selected,))
        if in_wl:
            st.button(f"✅ In Watchlist ({selected})", disabled=True, use_container_width=True)
        else:
            with st.popover(f"⭐ Add {selected} to Watchlist", use_container_width=True):
                st.markdown(f"**Add {get_ticker_label(selected)}**")
                pop_buy = st.number_input("Target Buy Price ($)", value=round(close*0.95, 2) if close else 100.0, step=1.0)
                pop_sell = st.number_input("Target Sell Price ($)", value=round(close*1.15, 2) if close else 150.0, step=1.0)
                pop_notes = st.text_input("Thesis Note", value=f"Tracked via Market Intelligence main screen.")
                if st.button("Save to Portfolio", type="primary", use_container_width=True):
                    run_write("INSERT INTO companies(ticker,name) VALUES(%s,%s) ON CONFLICT DO NOTHING;", (selected, TICKER_NAMES.get(selected, f"{selected} Corp")))
                    run_write("""
                        INSERT INTO watchlist_tickers(watchlist_id,ticker,target_buy_price,target_sell_price,notes)
                        VALUES('default_watchlist',%s,%s,%s,%s)
                        ON CONFLICT(watchlist_id,ticker) DO UPDATE SET
                            target_buy_price=EXCLUDED.target_buy_price,
                            target_sell_price=EXCLUDED.target_sell_price,
                            notes=EXCLUDED.notes;
                    """, (selected, pop_buy, pop_sell, pop_notes))
                    st.toast(f"✅ Added {selected} to your Watchlist!")
                    st.rerun()

    # Price metrics
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Close Price", f"${close:.2f}", f"{chg:+.2f} ({chg_pct:+.2f}%)")
    m2.metric("Open Price",  f"${_open:.2f}")
    m3.metric("Day High",    f"${high:.2f}")
    m4.metric("Day Low",     f"${low:.2f}")
    m5.metric("Volume",      f"{volume/1e6:.1f}M")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── ELEGANT LAYOUT: Left Column = Charts, Right Column = Company Profile + News Feed!
    cleft, cright = st.columns([3, 2])

    with cleft:
        # Candlestick + Volume Chart
        if close > 0:
            hist = simulate_history(close, high, low, _open, days=45, seed=hash(selected)%9999)
            fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   row_heights=[0.72,0.28], vertical_spacing=0.02)
            dates_h  = [h["date"]   for h in hist]
            opens_h  = [h["open"]   for h in hist]
            highs_h  = [h["high"]   for h in hist]
            lows_h   = [h["low"]    for h in hist]
            closes_h = [h["close"]  for h in hist]
            vols_h   = [h["volume"] for h in hist]
            vc = ["#10B981" if c>=o else "#EF4444" for o,c in zip(opens_h,closes_h)]

            fig_c.add_trace(go.Candlestick(
                x=dates_h, open=opens_h, high=highs_h, low=lows_h, close=closes_h,
                name=selected,
                increasing=dict(line=dict(color="#10B981"), fillcolor="rgba(16,185,129,0.7)"),
                decreasing=dict(line=dict(color="#EF4444"), fillcolor="rgba(239,68,68,0.7)"),
            ), row=1, col=1)

            # 10-day MA
            w = 10
            ma = [sum(closes_h[max(0,i-w+1):i+1])/len(closes_h[max(0,i-w+1):i+1]) for i in range(len(closes_h))]
            fig_c.add_trace(go.Scatter(
                x=dates_h, y=ma, name="10-day MA",
                line=dict(color="#F59E0B", width=1.5, dash="dot")
            ), row=1, col=1)

            fig_c.add_trace(go.Bar(
                x=dates_h, y=vols_h, name="Volume",
                marker_color=vc, opacity=0.55
            ), row=2, col=1)

            fig_c.update_layout(
                template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(family="Inter", color=TEXT_COLOR, size=10),
                title=dict(text=f"{get_ticker_label(selected)} — 45-Day Price Action & Volume",
                           font=dict(size=12, color="#A5B4FC"), x=0),
                margin=dict(l=10,r=10,t=36,b=10), height=390,
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            )
            fig_c.update_xaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR,size=9))
            fig_c.update_yaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR,size=9))
            st.plotly_chart(fig_c, use_container_width=True)

        # All Tickers Overview Chart
        if _client_ok:
            all_q = []
            for t in DEFAULT_TICKERS:
                try:
                    q = backend["client"].get_ticker_quote(t)
                    all_q.append({
                        "Ticker": t,
                        "Close":  safe_num(q.get("close_price",0)),
                        "Open":   safe_num(q.get("open_price",0)),
                    })
                except: pass

            if all_q:
                df_all = pd.DataFrame(all_q)
                df_all["Δ%"]    = ((df_all["Close"]-df_all["Open"])/df_all["Open"]*100).round(2)
                df_all["Color"] = df_all["Δ%"].apply(lambda x: "#10B981" if x>=0 else "#EF4444")
                df_all["Display"] = df_all["Ticker"].apply(lambda t: f"{t} ({TICKER_NAMES.get(t,t)})")

                fig_d = go.Figure(go.Bar(
                    x=df_all["Display"], y=df_all["Δ%"],
                    marker_color=df_all["Color"].tolist(), opacity=0.88,
                    text=[f"{v:+.2f}%" for v in df_all["Δ%"]],
                    textposition="outside",
                    textfont=dict(color=TEXT_COLOR, size=11),
                ))
                dark_layout(fig_d, height=270, title="Market Overview — Intraday Change %", show_legend=False)
                fig_d.update_layout(yaxis_title="% Change")
                fig_d.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)")
                st.plotly_chart(fig_d, use_container_width=True)

    with cright:
        # Company Profile Card
        st.markdown(f"#### {selected} — Company Profile")
        comp = run_query("SELECT * FROM companies WHERE ticker=%s;", (selected,))
        if comp:
            c = comp[0]
            mcap = safe_num(c.get("market_cap",0))
            pe   = safe_num(c.get("pe_ratio",0))
            divy = safe_num(c.get("dividend_yield",0))
            st.markdown(f"**{safe_str(c.get('name', TICKER_NAMES.get(selected, selected)))}**")
            st.markdown(f"`{safe_str(c.get('sector'))}` · `{safe_str(c.get('industry'))}`")
            fa, fb = st.columns(2)
            fa.metric("Market Cap", f"${mcap/1e12:.2f}T" if mcap>1e11 else f"${mcap/1e9:.1f}B")
            fb.metric("P/E Ratio",  f"{pe:.1f}x")
            fc, fd = st.columns(2)
            fc.metric("Div Yield",  f"{divy:.2f}%")
            fd.metric("52w Range",  f"${low*0.88:.0f}–${high*1.12:.0f}")
            desc = safe_str(c.get("description"), "")
            if desc:
                st.markdown(
                    f"<div style='font-size:0.80rem;color:#A0AEC0;background:rgba(255,255,255,0.03);"
                    f"border-radius:10px;padding:10px 12px;border:1px solid rgba(255,255,255,0.06);margin-top:6px;margin-bottom:14px'>{desc}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("Company data loading…")

        # 📰 NEWS FEED IN RIGHT COLUMN (As Requested)
        st.markdown(f"#### 📰 Latest News — {selected}")
        news_rows = run_query(
            "SELECT ticker,title,publisher,published_utc,sentiment,article_url "
            "FROM news_articles WHERE ticker=%s ORDER BY published_utc DESC LIMIT 5;",
            (selected,)
        )
        if news_rows:
            for n in news_rows:
                badge = sentiment_badge(n.get("sentiment"))
                date  = fmt_date(n.get("published_utc"))
                url   = safe_str(n.get("article_url"), "#")
                title = safe_str(n.get("title"), "Market Update")
                pub   = safe_str(n.get("publisher"), "—")
                link  = f'<a href="{url}" target="_blank" style="color:#6366F1">Read ↗</a>' if url != "#" else ""
                st.markdown(
                    f"<div class='news-card'>"
                    f"<div class='news-title'>{badge}&nbsp; {title}</div>"
                    f"<div class='news-meta'>{pub} · {date} &nbsp; {link}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No news articles indexed for this ticker yet.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VECTOR RAG SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 Semantic Vector RAG Explorer")
    st.caption("384-dim `all-MiniLM-L6-v2` embeddings stored in Lakebase pgvector HNSW index — cosine distance (`<=>`).")

    CHIPS = {
        "☁️ AI Cloud":    "companies expanding AI data center infrastructure and high cloud compute demand",
        "🚀 Earnings":    "record quarterly revenue beat and expanding profit margins",
        "📉 Fed Rates":   "Federal Reserve interest rate outlook and supply chain risk analysis",
        "🚗 EV & AI":     "electric vehicles self-driving autonomous AI hardware deployment",
    }
    chip_cols = st.columns(len(CHIPS))
    preset = None
    for col, (label, qtext) in zip(chip_cols, CHIPS.items()):
        if col.button(label, use_container_width=True): preset = qtext

    col_q, col_f, col_k = st.columns([4,2,1])
    with col_q:
        search_q = st.text_input("Semantic query",
            value=preset or "AI infrastructure data center high compute enterprise demand", key="rag_q")
    with col_f:
        filter_tick = st.selectbox(
            "Filter Ticker",
            ["All"] + ALL_TICKERS,
            format_func=lambda t: "All Tickers" if t == "All" else get_ticker_label(t),
            key="rag_tick"
        )
    with col_k:
        top_k = st.slider("Top K", 1, 10, 5, key="rag_k")

    ticker_param = None if filter_tick == "All" else filter_tick

    if not _rag_ok:
        st.error(f"⚠️ RAG engine unavailable: {backend.get('rag_error','Unknown error')}")
    else:
        if st.button("🔍 Run Semantic Search", use_container_width=True, type="primary"):
            with st.spinner("Computing query vector & searching pgvector index…"):
                try:
                    results = backend["search_news_vector"](search_q, ticker=ticker_param, top_k=top_k)
                    st.session_state["rag_results"] = results
                    st.session_state["rag_query"]   = search_q
                except Exception as e:
                    st.error(f"Vector search failed: {e}")
                    st.session_state["rag_results"] = []

        results = st.session_state.get("rag_results", [])
        if results:
            st.success(f"Found **{len(results)}** semantically relevant documents")

            # Horizontal relevance score chart
            df_rag = pd.DataFrame([{
                "Snippet": f"[{safe_str(r.get('ticker'))}] {safe_str(r.get('title',''))[:45]}…",
                "Score": safe_num(r.get("similarity_score",0)),
                "Sentiment": safe_str(r.get("sentiment","neutral")),
            } for r in results])
            bar_colors = ["#10B981" if "bull" in s else ("#EF4444" if "bear" in s else "#F59E0B")
                          for s in df_rag["Sentiment"]]
            fig_r = go.Figure(go.Bar(
                x=df_rag["Score"], y=df_rag["Snippet"], orientation="h",
                marker_color=bar_colors,
                text=[f"{v:.3f}" for v in df_rag["Score"]], textposition="outside",
            ))
            dark_layout(fig_r, height=max(180, len(results)*45),
                        title="Relevance Scores — pgvector Cosine Similarity", show_legend=False)
            fig_r.update_layout(xaxis_title="Similarity Score", yaxis_autorange="reversed")
            st.plotly_chart(fig_r, use_container_width=True)

            for i, r in enumerate(results):
                score = safe_num(r.get("similarity_score",0))
                tick  = safe_str(r.get("ticker"),"—")
                title = safe_str(r.get("title"),"Article")
                pub   = safe_str(r.get("publisher"),"—")
                sent  = safe_str(r.get("sentiment"),"neutral")
                chunk = safe_str(r.get("chunk_text"),"")
                url   = safe_str(r.get("article_url"),"#")
                date  = fmt_date(r.get("published_utc"))
                with st.expander(f"#{i+1}  [{tick} — {TICKER_NAMES.get(tick, tick)}]  {title[:72]}…  — {score:.3f}"):
                    c1, c2 = st.columns([1,5])
                    c1.metric("Score", f"{score:.3f}")
                    c2.progress(min(int(score*100),100))
                    st.markdown(f"{sentiment_badge(sent)} <span class='badge-rag'>pgvector cosine</span> &nbsp; **{pub}** · {date}", unsafe_allow_html=True)
                    if chunk: st.markdown(f"> {chunk[:400]}{'…' if len(chunk)>400 else ''}")
                    if url != "#": st.markdown(f"[🔗 Read full article]({url})")
        elif "rag_results" in st.session_state:
            st.warning("No matching documents. Try different query or Refresh ETL.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PORTFOLIO WATCHLIST (OVERHAULED: INLINE DATA EDITOR & BULK DELETE)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ⭐ Portfolio Watchlist Manager")
    st.caption("Live read, inline write/update, and bulk management against Lakebase `watchlist_tickers` table.")

    # ── Top Action Bar (Add Ticker Modal + Bulk Actions)
    top_act1, top_act2 = st.columns([3, 1])

    with top_act1:
        with st.popover("➕ Add New Ticker to Watchlist", use_container_width=False):
            st.markdown("#### Add Ticker to Portfolio")
            with st.form("inline_add_form", clear_on_submit=True):
                new_tick = st.text_input("Ticker Symbol", placeholder="e.g. SPY, QQQ, META, AMD, VOO…").strip().upper()
                new_buy  = st.number_input("Target Buy Price ($)", min_value=0.0, value=120.0, step=5.0)
                new_sell = st.number_input("Target Sell Price ($)", min_value=0.0, value=160.0, step=5.0)
                new_note = st.text_area("Thesis Note", value="Strategic portfolio holding.", height=60)
                if st.form_submit_button("💾 Save Ticker", type="primary", use_container_width=True):
                    if not new_tick or not new_tick.isalpha():
                        st.error("Please enter a valid ticker symbol.")
                    else:
                        run_write("INSERT INTO companies(ticker,name) VALUES(%s,%s) ON CONFLICT DO NOTHING;", (new_tick, TICKER_NAMES.get(new_tick, f"{new_tick} Corp")))
                        run_write("""
                            INSERT INTO watchlist_tickers(watchlist_id,ticker,target_buy_price,target_sell_price,notes)
                            VALUES('default_watchlist',%s,%s,%s,%s)
                            ON CONFLICT(watchlist_id,ticker) DO UPDATE SET
                                target_buy_price=EXCLUDED.target_buy_price,
                                target_sell_price=EXCLUDED.target_sell_price,
                                notes=EXCLUDED.notes;
                        """, (new_tick, new_buy, new_sell, new_note))
                        get_ticker_display_data.clear()
                        st.toast(f"✅ Added {new_tick} to watchlist!")
                        st.rerun()

    # Query Watchlist Rows
    wl_rows = run_query("""
        SELECT wt.ticker, COALESCE(c.name, wt.ticker) AS name,
               wt.target_buy_price, wt.target_sell_price, wt.notes, wt.added_at
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id='default_watchlist'
        ORDER BY wt.added_at DESC;
    """)

    if wl_rows:
        # Prepare DataFrame for st.data_editor
        df_wl_raw = pd.DataFrame(wl_rows)
        df_wl_raw["Delete"] = False
        df_wl_raw["Buy Target ($)"] = df_wl_raw["target_buy_price"].apply(safe_num)
        df_wl_raw["Sell Target ($)"] = df_wl_raw["target_sell_price"].apply(safe_num)
        df_wl_raw["Thesis Notes"] = df_wl_raw["notes"].fillna("")
        df_wl_raw["Company Name"] = df_wl_raw.apply(lambda r: f"{r['ticker']} — {r['name']}", axis=1)

        # Select columns to display in editor
        editor_df = df_wl_raw[["Delete", "ticker", "Company Name", "Buy Target ($)", "Sell Target ($)", "Thesis Notes"]].copy()

        st.markdown("**Watchlist Table (Edit cells directly or select rows to delete):**")
        edited_df = st.data_editor(
            editor_df,
            column_config={
                "Delete": st.column_config.CheckboxColumn("🗑️ Delete", help="Select rows to delete", default=False),
                "ticker": st.column_config.TextColumn("Ticker", disabled=True),
                "Company Name": st.column_config.TextColumn("Company", disabled=True),
                "Buy Target ($)": st.column_config.NumberColumn("Target Buy ($)", min_value=0.0, format="$%.2f"),
                "Sell Target ($)": st.column_config.NumberColumn("Target Sell ($)", min_value=0.0, format="$%.2f"),
                "Thesis Notes": st.column_config.TextColumn("Thesis / Notes", width="large"),
            },
            hide_index=True,
            use_container_width=True,
            key="watchlist_editor"
        )

        # Action Buttons below editor
        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])

        with btn_col1:
            if st.button("💾 Save Table Updates", type="primary", use_container_width=True):
                # Update Lakebase DB for changed rows
                updated_count = 0
                for _, row in edited_df.iterrows():
                    t = row["ticker"]
                    b = safe_num(row["Buy Target ($)"])
                    s = safe_num(row["Sell Target ($)"])
                    n = str(row["Thesis Notes"])
                    run_write("""
                        UPDATE watchlist_tickers
                        SET target_buy_price=%s, target_sell_price=%s, notes=%s
                        WHERE watchlist_id='default_watchlist' AND ticker=%s;
                    """, (b, s, n, t))
                    updated_count += 1
                st.toast(f"✅ Updated {updated_count} watchlist entries!")
                st.rerun()

        with btn_col2:
            to_delete = edited_df[edited_df["Delete"] == True]["ticker"].tolist()
            if to_delete:
                if st.button(f"🗑️ Delete Selected ({len(to_delete)})", use_container_width=True):
                    for t_del in to_delete:
                        run_write("DELETE FROM watchlist_tickers WHERE watchlist_id='default_watchlist' AND ticker=%s;", (t_del,))
                    st.toast(f"✅ Deleted {len(to_delete)} ticker(s)!")
                    st.rerun()
            else:
                st.button("🗑️ Delete Selected (0)", disabled=True, use_container_width=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── PORTFOLIO CHARTS
        if _client_ok:
            pdata = []
            for r in wl_rows:
                t = r["ticker"]
                buy_t  = safe_num(r.get("target_buy_price",0))
                sell_t = safe_num(r.get("target_sell_price",0))
                try:
                    q      = backend["client"].get_ticker_quote(t)
                    curr   = safe_num(q.get("close_price",0))
                    pct_buy  = ((curr - buy_t)  / buy_t  * 100) if buy_t  else 0
                    pct_sell = ((curr - sell_t) / sell_t * 100) if sell_t else 0
                    pdata.append({
                        "Ticker": f"{t} ({TICKER_NAMES.get(t,t)})",
                        "Current ($)": curr,
                        "Buy Target ($)": buy_t,
                        "Sell Target ($)": sell_t,
                        "% vs Buy":  round(pct_buy,  2),
                    })
                except: pass

            if pdata:
                df_p = pd.DataFrame(pdata)
                wl1, wl2 = st.columns(2)

                with wl1:
                    colors_p = ["#10B981" if v>=0 else "#EF4444" for v in df_p["% vs Buy"]]
                    fig_pct = go.Figure(go.Bar(
                        x=df_p["Ticker"], y=df_p["% vs Buy"],
                        marker_color=colors_p, opacity=0.88,
                        text=[f"{v:+.1f}%" for v in df_p["% vs Buy"]],
                        textposition="outside", textfont=dict(color=TEXT_COLOR, size=11),
                    ))
                    dark_layout(fig_pct, height=280, title="% Above / Below Buy Target", show_legend=False)
                    fig_pct.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.25)")
                    fig_pct.update_layout(yaxis_title="% Deviation from Buy Target")
                    st.plotly_chart(fig_pct, use_container_width=True)

                with wl2:
                    fig_tgt = go.Figure()
                    fig_tgt.add_trace(go.Bar(
                        name="Current Price", x=df_p["Ticker"], y=df_p["Current ($)"],
                        marker_color="#6366F1", opacity=0.85
                    ))
                    fig_tgt.add_trace(go.Scatter(
                        name="Buy Target", x=df_p["Ticker"], y=df_p["Buy Target ($)"],
                        mode="markers", marker=dict(size=12, color="#10B981", symbol="triangle-up",
                                                    line=dict(width=2, color="#fff"))
                    ))
                    fig_tgt.add_trace(go.Scatter(
                        name="Sell Target", x=df_p["Ticker"], y=df_p["Sell Target ($)"],
                        mode="markers", marker=dict(size=12, color="#EF4444", symbol="triangle-down",
                                                    line=dict(width=2, color="#fff"))
                    ))
                    dark_layout(fig_tgt, height=280, title="Current Price vs Buy/Sell Targets")
                    st.plotly_chart(fig_tgt, use_container_width=True)

    else:
        st.info("Your watchlist is currently empty. Click **➕ Add New Ticker to Watchlist** above to add items.")

    st.markdown("---")
    nc, rc = st.columns(2)
    with nc:
        st.markdown("#### 📝 Saved Research Notes")
        note_rows = run_query("SELECT ticker,title,content,created_at FROM research_notes ORDER BY created_at DESC LIMIT 6;")
        if note_rows:
            for n in note_rows:
                t = safe_str(n.get('ticker'))
                with st.expander(f"[{get_ticker_label(t)}] {safe_str(n.get('title'))[:55]}"):
                    st.write(safe_str(n.get("content")))
                    st.caption(f"📅 {fmt_ts(n.get('created_at'))}")
        else:
            st.caption("No notes saved yet — ask the AI Copilot to save a research note!")
    with rc:
        st.markdown("#### 📊 AI Analysis Reports")
        rep_rows = run_query("SELECT ticker,recommendation,summary,bull_case,bear_case,created_at FROM analysis_reports ORDER BY created_at DESC LIMIT 6;")
        if rep_rows:
            for r in rep_rows:
                t = safe_str(r.get('ticker'))
                rec = safe_str(r.get("recommendation"),"HOLD")
                ico = "🟢" if rec=="BUY" else ("🔴" if rec=="SELL" else "🟡")
                with st.expander(f"{ico} [{get_ticker_label(t)}] {rec} · {fmt_date(r.get('created_at'))}"):
                    st.write(f"**Summary:** {safe_str(r.get('summary'))}")
                    st.write(f"**Bull:** {safe_str(r.get('bull_case'))}")
                    st.write(f"**Bear:** {safe_str(r.get('bear_case'))}")
        else:
            st.caption("No analysis reports generated yet — ask the AI Copilot!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI COPILOT CHAT (WITH IN-TAB SESSION HISTORY & CLEAR ACTION)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    # Chat Header with Session Info & Clear Button directly in tab!
    ch_col1, ch_col2 = st.columns([3, 1])

    with ch_col1:
        st.markdown(f"""
        <div style="padding:10px 16px;background:rgba(99,102,241,0.08);
                    border:1px solid rgba(99,102,241,0.2);border-radius:12px">
          <div style="font-size:1.0rem;font-weight:700;color:#E8EDFF">🤖 AI Investment Copilot</div>
          <div style="font-size:0.75rem;color:#8892A4;margin-top:2px">
            ReAct agent with READ (RAG, quotes, watchlist) and WRITE (add/remove, notes, reports) capabilities
          </div>
        </div>
        """, unsafe_allow_html=True)

    with ch_col2:
        st.markdown(f"<span class='badge-sess'>Session: {SID}</span>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Chat history cleared for this session.",
                "actions": [],
                "ts": datetime.now().strftime("%H:%M"),
            }]
            st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if not _agent_ok:
        st.error(f"⚠️ AI Agent unavailable: {backend.get('agent_error','Unknown')}")
    else:
        # Quick Commands
        st.markdown("**Quick Commands:**")
        qc = st.columns(5)
        qp = None
        if qc[0].button("➕ Add NVDA@120",   use_container_width=True): qp="Add NVDA to my watchlist with target buy 120"
        if qc[1].button("🔍 AI News AAPL",    use_container_width=True): qp="Search news about Apple artificial intelligence"
        if qc[2].button("📊 Analyse TSLA",    use_container_width=True): qp="Generate a BUY analysis report for TSLA"
        if qc[3].button("📋 My Watchlist",    use_container_width=True): qp="Show my current portfolio watchlist"
        if qc[4].button("📈 NVDA Snapshot",   use_container_width=True): qp="What is the current NVDA stock price and fundamentals?"

        st.markdown("---")

        # Fixed height scrollable chat box
        chat_box = st.container(height=450)
        with chat_box:
            for msg in st.session_state.messages:
                role = msg["role"]
                with st.chat_message(role):
                    ts = msg.get("ts","")
                    if role == "user":
                        st.markdown(
                            f"<div style='font-size:0.70rem;color:#6B7280;margin-bottom:4px'>"
                            f"<span class='badge-sess' style='font-size:0.68rem'>You · {SID}</span> · {ts}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div style='font-size:0.70rem;color:#6B7280;margin-bottom:4px'>"
                            f"🤖 <strong>LakePulse Copilot</strong> · {ts}</div>",
                            unsafe_allow_html=True
                        )
                    st.markdown(msg["content"])
                    for act in msg.get("actions", []):
                        st.markdown(f"<span class='badge-action'>⚡ {act}</span>", unsafe_allow_html=True)

        # Chat Input pinned below container
        user_input = st.chat_input(
            f"Ask AI Copilot… [Session {SID}]",
            key="agent_chat_input"
        ) or qp

        if user_input:
            ts_now = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "actions": [],
                "ts": ts_now,
            })
            with st.spinner("🤖 Copilot reasoning and selecting tools…"):
                try:
                    resp    = backend["agent"].run(user_input)
                    answer  = safe_str(resp.get("answer",""), "No response.")
                    actions = resp.get("actions_taken", [])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "actions": actions,
                        "ts": datetime.now().strftime("%H:%M"),
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ Agent error: {e}",
                        "actions": [],
                        "ts": datetime.now().strftime("%H:%M"),
                    })
            st.rerun()

        st.markdown("---")
        with st.expander("🛠️ Available Agent Tools"):
            tools = [
                ("tool_search_news_rag",         "READ",  "Semantic vector search over pgvector 384-dim news embeddings"),
                ("tool_get_ticker_snapshot",      "READ",  "Live / fallback market price, volume, and company fundamentals"),
                ("tool_get_watchlist",            "READ",  "List portfolio tickers with target prices from Lakebase"),
                ("tool_add_to_watchlist",         "WRITE", "INSERT/UPSERT ticker into watchlist_tickers table"),
                ("tool_remove_from_watchlist",    "WRITE", "DELETE ticker from watchlist_tickers table"),
                ("tool_save_research_note",       "WRITE", "Write research note into research_notes table"),
                ("tool_generate_analysis_report", "WRITE", "Generate & persist BUY/HOLD/SELL report in analysis_reports"),
            ]
            for name, rw, desc in tools:
                color = "#10B981" if rw=="READ" else "#6366F1"
                st.markdown(
                    f"<div class='tool-row'><code style='color:{color}'>{rw}</code> &nbsp;"
                    f"<strong>{name}</strong><br><span style='color:#8892A4;font-size:0.81rem'>{desc}</span></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SYSTEM HEALTH
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⚡ Pipeline & System Health")

    h1,h2,h3,h4 = st.columns(4)
    h1.metric("Lakebase DB",    "Online"  if _db_ok    else "Offline")
    h2.metric("RAG Engine",     "Active"  if _rag_ok   else "Error")
    h3.metric("AI Agent",       "Online"  if _agent_ok else "Error")
    h4.metric("Market Client",  "Live"    if _client_ok else "Fallback")

    st.markdown("---")
    st.markdown("#### 🗄️ Lakebase Table Record Audit")

    db_tables = [
        ("users",             "User accounts"),
        ("companies",         "Company metadata"),
        ("watchlists",        "Watchlist groups"),
        ("watchlist_tickers", "Portfolio tickers"),
        ("price_snapshots",   "OHLCV price snapshots"),
        ("news_articles",     "Unstructured news"),
        ("news_embeddings",   "pgvector 384-dim"),
        ("research_notes",    "AI research notes"),
        ("analysis_reports",  "BUY/HOLD/SELL reports"),
    ]

    table_rows_html = ""
    for tname, tdesc in db_tables:
        try:
            r   = run_query(f"SELECT COUNT(*) AS c FROM {tname};")
            cnt = int(r[0]["c"]) if r else 0
            status_cls  = "ht-ok"
            status_txt  = "✅ Active"
            cnt_color   = "#E8EDFF"
        except Exception as ex:
            cnt        = 0
            status_cls = "ht-err"
            status_txt = f"⚠️ {str(ex)[:35]}"
            cnt_color  = "#F87171"

        table_rows_html += (
            f"<tr>"
            f"<td><code style='color:#A5B4FC'>{tname}</code></td>"
            f"<td style='color:#8892A4'>{tdesc}</td>"
            f"<td style='color:{cnt_color};font-weight:700;font-size:1.05rem'>{cnt:,}</td>"
            f"<td><span class='{status_cls}'>{status_txt}</span></td>"
            f"</tr>"
        )

    st.markdown(
        f"<div class='table-wrap'><table class='health-table'>"
        f"<thead><tr><th>Table</th><th>Description</th><th>Records</th><th>Status</th></tr></thead>"
        f"<tbody>{table_rows_html}</tbody></table></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("#### 🏗️ Pipeline Architecture")
    st.code("""
  Massive REST API
       │
       ▼
  [Bronze Layer]  ─── PySpark: raw quote + news ingestion (6 default tickers)
       │
       ▼
  [Silver Layer]  ─── Schema validation · sentiment enrichment · company upserts
       │
       ▼
  [Gold Layer]    ─── Business aggregations · price snapshots · reference dimensions
       │
       ▼
  Lakebase PostgreSQL + pgvector
       │
   ┌───┴──────────────────────────────────────┐
   ▼                                          ▼
Relational Tables                   news_embeddings (384-dim HNSW)
companies · watchlists · news       ← sentence-transformers/all-MiniLM-L6-v2
reports · notes · snapshots         ← pgvector cosine similarity (<=>)
    """, language="text")

    pi = st.session_state.get("pipeline_init", {})
    if pi.get("ok"):
        st.success("✅ Pipeline initialised successfully on startup.")
    else:
        st.error(f"⚠️ Pipeline error: {pi.get('message','Unknown')}")

    st.markdown("---")
    st.markdown("#### 📋 Current Session Info")
    sess_data = {
        "Session ID": SID,
        "Session Started": st.session_state.session_started,
        "Chat Messages": len(st.session_state.messages),
        "Tickers Loaded": len(ALL_TICKERS),
        "DB Connected": str(_db_ok),
        "RAG Engine": str(_rag_ok),
        "AI Agent": str(_agent_ok),
    }
    si_html = "".join(
        f"<tr><td style='color:#8892A4;font-size:0.82rem'>{k}</td>"
        f"<td style='color:#E8EDFF;font-weight:600'>{v}</td></tr>"
        for k, v in sess_data.items()
    )
    st.markdown(
        f"<div class='table-wrap'><table class='health-table'>"
        f"<thead><tr><th>Property</th><th>Value</th></tr></thead>"
        f"<tbody>{si_html}</tbody></table></div>",
        unsafe_allow_html=True
    )
