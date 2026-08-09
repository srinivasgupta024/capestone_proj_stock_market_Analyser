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

# ─── HARD LOCK DARK MODE + FULL DESIGN SYSTEM ─────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* ── Force dark on every element Streamlit touches ── */
  html, body { background: #0C0E16 !important; color: #E8EDFF !important; }
  .stApp, .stApp > *, [data-testid="stAppViewContainer"],
  [data-testid="stHeader"], [data-testid="stToolbar"],
  [data-testid="block-container"] {
    background: #0C0E16 !important;
    font-family: 'Inter', sans-serif !important;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] > div,
  section[data-testid="stSidebar"] > div > div {
    background: #0D1020 !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
  }
  section[data-testid="stSidebar"] * { color: #C8D0E0 !important; }
  section[data-testid="stSidebar"] .stButton > button {
    background: rgba(99,102,241,0.14) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    color: #A5B4FC !important;
    border-radius: 10px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s ease;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.28) !important;
    border-color: rgba(99,102,241,0.6) !important;
    transform: translateY(-1px);
  }

  /* ── Kill the hamburger & top decorations ── */
  [data-testid="stHeader"] { display: none !important; }
  [data-testid="stDecoration"] { display: none !important; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.025) !important;
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 9px 20px;
    font-weight: 600;
    font-size: 0.86rem;
    color: #8892A4 !important;
    background: transparent !important;
    border: none !important;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.22) !important;
    color: #A5B4FC !important;
  }

  /* ── Metric cards ── */
  [data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(25,28,52,0.95) 0%, rgba(15,18,36,0.95) 100%) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    border-radius: 16px !important;
    padding: 20px 22px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.45);
    transition: all 0.2s ease;
  }
  [data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.2);
  }
  [data-testid="stMetricLabel"] > div {
    font-size: 0.75rem !important;
    color: #8892A4 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
  }
  [data-testid="stMetricValue"] > div {
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: #E8EDFF !important;
  }
  [data-testid="stMetricDelta"] > div { font-size: 0.82rem !important; }

  /* ── Buttons (main area) ── */
  .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    padding: 9px 20px !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    background: rgba(99,102,241,0.12) !important;
    color: #A5B4FC !important;
    transition: all 0.2s ease !important;
  }
  .stButton > button:hover {
    background: rgba(99,102,241,0.26) !important;
    border-color: rgba(99,102,241,0.65) !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6366F1 0%,#4F46E5 100%) !important;
    color: #fff !important;
    border: none !important;
  }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #E8EDFF !important;
  }
  .stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #E8EDFF !important;
  }

  /* ── DataFrames ── */
  [data-testid="stDataFrame"], [data-testid="stDataFrame"] * {
    background: rgba(15,18,36,0.95) !important;
    color: #E8EDFF !important;
  }

  /* ── Expanders ── */
  [data-testid="stExpander"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
  }
  [data-testid="stExpander"] summary { color: #C8D0E0 !important; font-weight: 600 !important; }

  /* ── Chat ── */
  [data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    margin-bottom: 10px;
  }

  /* ── Alerts / info boxes ── */
  [data-testid="stAlert"] { border-radius: 10px !important; }

  /* ── Dividers ── */
  hr { border-color: rgba(255,255,255,0.07) !important; margin: 20px 0 !important; }

  /* ── Custom components ── */
  .badge-bullish { background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.35); padding:2px 10px; border-radius:20px; font-size:0.76rem; font-weight:700; display:inline-block; }
  .badge-bearish { background:rgba(239,68,68,0.15);  color:#F87171; border:1px solid rgba(239,68,68,0.35);  padding:2px 10px; border-radius:20px; font-size:0.76rem; font-weight:700; display:inline-block; }
  .badge-neutral { background:rgba(245,158,11,0.15); color:#FCD34D; border:1px solid rgba(245,158,11,0.35); padding:2px 10px; border-radius:20px; font-size:0.76rem; font-weight:700; display:inline-block; }
  .badge-action  { background:rgba(99,102,241,0.18); color:#A5B4FC; border:1px solid rgba(99,102,241,0.4); padding:3px 12px; border-radius:20px; font-size:0.80rem; font-weight:700; display:inline-block; margin:4px 0; }
  .badge-rag     { background:rgba(14,165,233,0.15); color:#38BDF8; border:1px solid rgba(14,165,233,0.35); padding:2px 10px; border-radius:20px; font-size:0.76rem; font-weight:700; display:inline-block; }

  .stat-card {
    background: linear-gradient(145deg, rgba(25,28,52,0.9) 0%, rgba(15,18,36,0.9) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
  }
  .news-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
  }
  .news-card:hover { border-color: rgba(99,102,241,0.35); }
  .news-title { font-size: 0.92rem; font-weight: 600; color: #E8EDFF; line-height: 1.4; }
  .news-meta  { font-size: 0.77rem; color: #8892A4; margin-top: 6px; }

  .tool-row { padding: 9px 14px; border-radius: 8px; background: rgba(255,255,255,0.03); border-left: 3px solid rgba(99,102,241,0.5); margin-bottom: 8px; font-size: 0.84rem; color: #C8D0E0; }

  /* Sidebar sections */
  .sb-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #4B5568;
    margin: 18px 0 8px 0;
  }
  .sb-status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 8px;
    background: rgba(255,255,255,0.025);
    margin-bottom: 6px;
    font-size: 0.84rem;
    color: #C8D0E0;
  }
  .sb-status-dot-green  { width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow: 0 0 6px #10B981; flex-shrink:0; }
  .sb-status-dot-yellow { width:8px; height:8px; border-radius:50%; background:#F59E0B; box-shadow: 0 0 6px #F59E0B; flex-shrink:0; }
  .sb-status-dot-red    { width:8px; height:8px; border-radius:50%; background:#EF4444; box-shadow: 0 0 6px #EF4444; flex-shrink:0; }

  /* Page title */
  .page-title { font-size: 1.9rem; font-weight: 800; color: #E8EDFF; margin: 0; }
  .page-sub   { font-size: 0.82rem; color: #8892A4; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fmt_date(val):
    if val is None: return "N/A"
    if isinstance(val, datetime): return val.strftime("%Y-%m-%d")
    try: return str(val)[:10]
    except: return str(val)

def safe_str(val, fallback="N/A"):
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

def dark_layout(fig, height=340, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=TEXT_COLOR),
        title=dict(text=title, font=dict(size=14, color="#A5B4FC"), x=0),
        margin=dict(l=12, r=12, t=36 if title else 12, b=12),
        height=height,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.07)",
            borderwidth=1,
            font=dict(size=11),
        ),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR))
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR))
    return fig


def simulate_history(close, high, low, _open, days=30, seed=42):
    """Generate synthetic OHLCV history anchored at today's snapshot for candlestick chart."""
    random.seed(seed)
    prices, dates = [], []
    price = close * 0.88
    for i in range(days):
        date = datetime.today() - timedelta(days=days - i)
        change = random.uniform(-0.025, 0.028)
        price = max(price * (1 + change), 1)
        day_range = price * random.uniform(0.008, 0.025)
        o = price + random.uniform(-day_range / 2, day_range / 2)
        c = price + random.uniform(-day_range / 2, day_range / 2)
        h = max(o, c) + random.uniform(0, day_range / 2)
        l = min(o, c) - random.uniform(0, day_range / 2)
        vol = int(random.uniform(0.7, 1.4) * 35_000_000)
        dates.append(date)
        prices.append({"date": date, "open": o, "high": h, "low": l, "close": c, "volume": vol})
    # Anchor last candle to real snapshot
    prices[-1].update({"open": _open, "high": high, "low": low, "close": close})
    return prices


# ─── BACKEND LOADING ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_backend():
    m = {}
    for key, loader in [
        ("db",     lambda: __import__("src.lakebase", fromlist=["init_db","run_query","run_write"])),
        ("client", lambda: __import__("src.massive_client", fromlist=["MassiveClient"])),
        ("rag",    lambda: __import__("src.rag.vector_search", fromlist=["search_news_vector"])),
        ("agent",  lambda: __import__("src.agent.agent_engine", fromlist=["StockMarketAgent"])),
    ]:
        try:
            mod = loader()
            if key == "db":
                m["run_query"] = mod.run_query
                m["run_write"] = mod.run_write
                m["init_db"]   = mod.init_db
                m["db_ok"]     = True
            elif key == "client":
                m["client"]    = mod.MassiveClient()
                m["client_ok"] = True
            elif key == "rag":
                m["search_news_vector"] = mod.search_news_vector
                m["rag_ok"]             = True
            elif key == "agent":
                m["agent"]    = mod.StockMarketAgent()
                m["agent_ok"] = True
        except Exception as e:
            m[f"{key}_ok"]    = False
            m[f"{key}_error"] = str(e)
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
        return {"ok": True, "message": "Pipeline initialised successfully"}
    except Exception as e:
        return {"ok": False, "message": str(e)}

backend = load_backend()

if "pipeline_init" not in st.session_state:
    with st.spinner("🚀 Initialising LakePulse AI... (first start only)"):
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

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
TICKERS = ["NVDA","AAPL","MSFT","AMZN","GOOGL","TSLA"]

with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding: 6px 0 20px 0; border-bottom: 1px solid rgba(99,102,241,0.2); margin-bottom: 4px;">
      <div style="font-size:1.3rem; font-weight:800; letter-spacing:-0.5px; color:#E8EDFF;">
        📈 LakePulse AI
      </div>
      <div style="font-size:0.72rem; color:#6B7280; margin-top:2px;">
        Databricks Capstone · 2026
      </div>
    </div>
    """, unsafe_allow_html=True)

    # System Status
    st.markdown("<div class='sb-section-label'>System Status</div>", unsafe_allow_html=True)

    status_items = [
        (_db_ok,     "Lakebase (pgvector)",  "Online",       "Offline"),
        (_client_ok, "Market Data Client",   "Active",       "Fallback"),
        (_rag_ok,    "Vector RAG Engine",    "384-dim HNSW", "Unavailable"),
        (_agent_ok,  "AI ReAct Agent",       "Online",       "Unavailable"),
    ]
    for ok, label, good, bad in status_items:
        dot = "green" if ok else ("yellow" if label == "Market Data Client" else "red")
        txt = good if ok else bad
        st.markdown(
            f"<div class='sb-status-row'>"
            f"<div class='sb-status-dot-{dot}'></div>"
            f"<span style='flex:1'>{label}</span>"
            f"<span style='font-size:0.74rem; color:#6B7280'>{txt}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    pi = st.session_state.get("pipeline_init", {})
    if pi.get("ok"):
        st.markdown(
            "<div style='font-size:0.75rem; color:#10B981; margin-top:8px; padding: 6px 10px; "
            "background:rgba(16,185,129,0.08); border-radius:8px; border:1px solid rgba(16,185,129,0.2)'>"
            "✅ Pipeline initialised</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='font-size:0.75rem; color:#F87171; margin-top:8px; padding: 6px 10px; "
            f"background:rgba(239,68,68,0.08); border-radius:8px; border:1px solid rgba(239,68,68,0.2)'>"
            f"⚠️ {pi.get('message','Pipeline error')[:60]}</div>", unsafe_allow_html=True
        )

    # Quick Ticker Selector
    st.markdown("<div class='sb-section-label'>Quick Ticker</div>", unsafe_allow_html=True)
    sb_ticker = st.selectbox("", TICKERS, key="sb_ticker", label_visibility="collapsed")

    # Data Pipeline
    st.markdown("<div class='sb-section-label'>Data Pipeline</div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh ETL & RAG Pipeline", use_container_width=True):
        with st.spinner("Running PySpark Bronze → Silver → Gold ETL..."):
            try:
                from src.spark_pipeline.ingestion import run_bronze_ingestion
                from src.spark_pipeline.transformations import process_silver_gold_and_persist
                from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
                prices, news = run_bronze_ingestion(TICKERS)
                process_silver_gold_and_persist(prices, news)
                count = generate_and_store_news_embeddings()
                init_pipeline.clear()
                st.success(f"✅ {count} embeddings refreshed")
            except Exception as e:
                st.error(str(e)[:100])

    # Footer
    st.markdown(
        "<div style='position:fixed; bottom:16px; left:0; width:240px; text-align:center; "
        "font-size:0.70rem; color:#374151; padding: 0 16px;'>"
        "Built with Streamlit · Databricks Lakebase · pgvector"
        "</div>", unsafe_allow_html=True
    )

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 20px 0;">
  <div class="page-title">📈 LakePulse AI</div>
  <div class="page-sub">
    Enterprise financial intelligence — Databricks Lakebase · PySpark Medallion ETL · pgvector RAG · ReAct AI Agent
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence",
    "🔍 Vector RAG Search",
    "⭐ Portfolio Watchlist",
    "🤖 AI Agent Copilot",
    "⚡ System Health",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── KPI Row ──
    kpis = st.columns(5)
    kpi_queries = [
        ("Tracked Tickers",   "SELECT COUNT(*) AS c FROM companies"),
        ("Portfolio Items",   "SELECT COUNT(*) AS c FROM watchlist_tickers"),
        ("News Articles",     "SELECT COUNT(*) AS c FROM news_articles"),
        ("Vector Embeddings", "SELECT COUNT(*) AS c FROM news_embeddings"),
        ("Price Snapshots",   "SELECT COUNT(*) AS c FROM price_snapshots"),
    ]
    for col, (label, sql) in zip(kpis, kpi_queries):
        rows = run_query(sql)
        val  = int(rows[0]["c"]) if rows else 0
        col.metric(label, f"{val:,}")

    st.markdown("---")

    # ── Ticker Selector ──
    left, right = st.columns([1, 4])
    with left:
        selected = st.selectbox("Ticker", TICKERS, index=0, key="tab1_ticker")
    with right:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Fetch quote
    quote = {}
    if _client_ok:
        try: quote = backend["client"].get_ticker_quote(selected)
        except: pass

    close  = safe_num(quote.get("close_price", 0))
    _open  = safe_num(quote.get("open_price", 0))
    high   = safe_num(quote.get("high_price", 0))
    low    = safe_num(quote.get("low_price", 0))
    volume = int(safe_num(quote.get("volume", 0)))
    chg    = close - _open
    chg_pct= (chg / _open * 100) if _open else 0

    # Price metric row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Close Price",  f"${close:.2f}", f"{chg:+.2f} ({chg_pct:+.2f}%)")
    m2.metric("Open Price",   f"${_open:.2f}")
    m3.metric("Day High",     f"${high:.2f}")
    m4.metric("Day Low",      f"${low:.2f}")
    m5.metric("Volume",       f"{volume/1e6:.1f}M")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── CHARTS ROW ──
    chart_left, chart_right = st.columns([3, 2])

    with chart_left:
        # ── CANDLESTICK CHART (simulated 30-day history) ──
        if close > 0:
            history = simulate_history(close, high, low, _open, days=30, seed=hash(selected) % 999)
            fig_candle = go.Figure()

            # Volume bars (secondary axis)
            fig_candle = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.72, 0.28],
                vertical_spacing=0.03,
            )

            dates_h  = [h["date"] for h in history]
            opens_h  = [h["open"] for h in history]
            highs_h  = [h["high"] for h in history]
            lows_h   = [h["low"]  for h in history]
            closes_h = [h["close"] for h in history]
            vols_h   = [h["volume"] for h in history]
            colors_v = ["#10B981" if c >= o else "#EF4444" for o, c in zip(opens_h, closes_h)]

            fig_candle.add_trace(go.Candlestick(
                x=dates_h, open=opens_h, high=highs_h, low=lows_h, close=closes_h,
                name=selected,
                increasing=dict(line=dict(color="#10B981"), fillcolor="#10B981"),
                decreasing=dict(line=dict(color="#EF4444"), fillcolor="#EF4444"),
            ), row=1, col=1)

            # 7-day moving average
            window = 7
            ma7 = [sum(closes_h[max(0,i-window+1):i+1])/len(closes_h[max(0,i-window+1):i+1]) for i in range(len(closes_h))]
            fig_candle.add_trace(go.Scatter(
                x=dates_h, y=ma7, name="7-day MA",
                line=dict(color="#F59E0B", width=1.5, dash="dot"),
            ), row=1, col=1)

            fig_candle.add_trace(go.Bar(
                x=dates_h, y=vols_h,
                name="Volume",
                marker_color=colors_v,
                opacity=0.6,
            ), row=2, col=1)

            fig_candle.update_layout(
                template="plotly_dark",
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(family="Inter", color=TEXT_COLOR),
                title=dict(text=f"{selected} — 30-Day Price Action & Volume", font=dict(size=13, color="#A5B4FC"), x=0),
                margin=dict(l=12, r=12, t=36, b=12),
                height=380,
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
                showlegend=True,
            )
            fig_candle.update_xaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR))
            fig_candle.update_yaxes(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(color=AXIS_COLOR))
            st.plotly_chart(fig_candle, use_container_width=True)

    with chart_right:
        # ── COMPANY FUNDAMENTALS ──
        st.markdown(f"#### {selected} Company Profile")
        comp_rows = run_query("SELECT * FROM companies WHERE ticker = %s;", (selected,))
        if comp_rows:
            c = comp_rows[0]
            mcap = safe_num(c.get("market_cap", 0))
            pe   = safe_num(c.get("pe_ratio", 0))
            divy = safe_num(c.get("dividend_yield", 0))
            st.markdown(f"**{safe_str(c.get('name'))}**")
            st.markdown(f"`{safe_str(c.get('sector'))}` · `{safe_str(c.get('industry'))}`")

            f1, f2 = st.columns(2)
            f1.metric("Market Cap", f"${mcap/1e12:.2f}T" if mcap > 1e9 else f"${mcap/1e9:.1f}B")
            f2.metric("P/E Ratio",  f"{pe:.1f}x")
            f3, f4 = st.columns(2)
            f3.metric("Div Yield",  f"{divy:.2f}%")
            f4.metric("Day Range",  f"${low:.0f}–${high:.0f}")

            desc = safe_str(c.get("description"), "")
            if desc:
                st.markdown(
                    f"<div style='font-size:0.83rem; color:#A0AEC0; background:rgba(255,255,255,0.03); "
                    f"border-radius:10px; padding:12px; border:1px solid rgba(255,255,255,0.06); margin-top:8px'>"
                    f"{desc}</div>", unsafe_allow_html=True
                )
        else:
            st.caption("Company data loading...")

    # ── ALL TICKERS COMPARISON ──
    st.markdown("---")
    st.markdown("#### 📊 All Tickers — Price Comparison")
    if _client_ok:
        all_quotes = []
        for t in TICKERS:
            try:
                q = backend["client"].get_ticker_quote(t)
                all_quotes.append({
                    "Ticker": t,
                    "Close ($)": safe_num(q.get("close_price", 0)),
                    "Open ($)":  safe_num(q.get("open_price", 0)),
                    "High ($)":  safe_num(q.get("high_price", 0)),
                    "Low ($)":   safe_num(q.get("low_price", 0)),
                })
            except: pass

        if all_quotes:
            df_all = pd.DataFrame(all_quotes)
            df_all["Δ ($)"]   = df_all["Close ($)"] - df_all["Open ($)"]
            df_all["Δ (%)"]   = (df_all["Δ ($)"] / df_all["Open ($)"] * 100).round(2)
            df_all["Color"]   = df_all["Δ ($)"].apply(lambda x: "#10B981" if x >= 0 else "#EF4444")

            cmp1, cmp2 = st.columns(2)

            with cmp1:
                # Grouped OHLC bar chart
                fig_cmp = go.Figure()
                for field, color in [("Open ($)", "#6366F1"), ("Close ($)", "#10B981"), ("High ($)", "#F59E0B"), ("Low ($)", "#EF4444")]:
                    fig_cmp.add_trace(go.Bar(
                        name=field.replace(" ($)",""),
                        x=df_all["Ticker"],
                        y=df_all[field],
                        marker_color=color,
                        opacity=0.85,
                    ))
                fig_cmp.update_layout(barmode="group")
                dark_layout(fig_cmp, height=300, title="OHLC Comparison Across All Tickers")
                st.plotly_chart(fig_cmp, use_container_width=True)

            with cmp2:
                # Day change % bar chart
                fig_chg = go.Figure(go.Bar(
                    x=df_all["Ticker"],
                    y=df_all["Δ (%)"],
                    marker_color=df_all["Color"].tolist(),
                    text=[f"{v:+.2f}%" for v in df_all["Δ (%)"]],
                    textposition="outside",
                    textfont=dict(color=TEXT_COLOR, size=11),
                ))
                dark_layout(fig_chg, height=300, title="Intraday Change % (Open → Close)")
                fig_chg.update_layout(yaxis_title="% Change", showlegend=False)
                st.plotly_chart(fig_chg, use_container_width=True)

    # ── LATEST NEWS ──
    st.markdown("---")
    st.markdown(f"#### 📰 Latest News — {selected}")
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
                f"<div class='news-meta'>{pub} &middot; {date}"
                f"{'&nbsp;&nbsp;<a href=' + chr(39) + url + chr(39) + ' target=_blank style=color:#6366F1>Read ↗</a>' if url != '#' else ''}"
                f"</div></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No news yet. Click **Refresh ETL & RAG Pipeline** in the sidebar.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VECTOR RAG SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 Semantic Vector RAG Explorer")
    st.caption("384-dim `all-MiniLM-L6-v2` embeddings stored in Lakebase pgvector HNSW index — cosine distance (`<=>`).")

    CHIPS = {
        "☁️ AI Cloud Expansion":  "companies expanding AI data center infrastructure and high cloud compute demand",
        "🚀 Earnings Beat":       "record quarterly revenue beat and expanding profit margins",
        "📉 Rate Sensitivity":    "Federal Reserve interest rate outlook and supply chain risk analysis",
        "🚗 EV & Autonomy":       "electric vehicles self-driving autonomous AI hardware deployment",
    }
    chip_cols = st.columns(len(CHIPS))
    preset = None
    for col, (label, qtext) in zip(chip_cols, CHIPS.items()):
        if col.button(label, use_container_width=True): preset = qtext

    col_q, col_f, col_k = st.columns([4, 1, 1])
    with col_q:
        search_q = st.text_input("Semantic query",
            value=preset or "AI infrastructure data center high compute enterprise demand", key="rag_q")
    with col_f:
        filter_tick = st.selectbox("Ticker filter", ["All"] + TICKERS, key="rag_tick")
    with col_k:
        top_k = st.slider("Top K", 1, 10, 5, key="rag_k")

    ticker_param = None if filter_tick == "All" else filter_tick

    if not _rag_ok:
        st.error(f"⚠️ RAG engine unavailable: {backend.get('rag_error', 'Unknown error')}")
    else:
        if st.button("🔍 Run Semantic Search", use_container_width=True, type="primary"):
            with st.spinner("Computing query vector & searching pgvector index..."):
                try:
                    results = backend["search_news_vector"](search_q, ticker=ticker_param, top_k=top_k)
                    st.session_state["rag_results"] = results
                    st.session_state["rag_query"]   = search_q
                except Exception as e:
                    st.error(f"Vector search failed: {e}")
                    st.session_state["rag_results"] = []

        results = st.session_state.get("rag_results", [])
        if results:
            st.success(f"Found **{len(results)}** documents matching: *\"{st.session_state.get('rag_query','')}\"*")

            # Relevance score bar chart
            df_rag = pd.DataFrame([{
                "Ticker": safe_str(r.get("ticker")),
                "Title":  safe_str(r.get("title",""))[:50] + "…",
                "Score":  safe_num(r.get("similarity_score", 0)),
                "Sentiment": safe_str(r.get("sentiment","neutral")),
            } for r in results])
            colors_rag = ["#10B981" if "bull" in s else ("#EF4444" if "bear" in s else "#F59E0B")
                          for s in df_rag["Sentiment"]]
            fig_rag = go.Figure(go.Bar(
                x=df_rag["Score"], y=df_rag["Title"],
                orientation="h",
                marker_color=colors_rag,
                text=[f"{v:.3f}" for v in df_rag["Score"]],
                textposition="outside",
            ))
            dark_layout(fig_rag, height=220, title="Relevance Scores (pgvector cosine similarity)")
            fig_rag.update_layout(yaxis_autorange="reversed", showlegend=False, xaxis_title="Score")
            st.plotly_chart(fig_rag, use_container_width=True)

            for i, r in enumerate(results):
                score = safe_num(r.get("similarity_score", 0))
                tick  = safe_str(r.get("ticker"), "—")
                title = safe_str(r.get("title"), "Article")
                pub   = safe_str(r.get("publisher"), "—")
                sent  = safe_str(r.get("sentiment"), "neutral")
                chunk = safe_str(r.get("chunk_text"), "")
                url   = safe_str(r.get("article_url"), "#")
                date  = fmt_date(r.get("published_utc"))
                badge = sentiment_badge(sent)
                with st.expander(f"#{i+1}  [{tick}]  {title[:75]}…  — {score:.3f}"):
                    c1, c2 = st.columns([1, 5])
                    c1.metric("Score", f"{score:.3f}")
                    c2.progress(min(int(score * 100), 100))
                    st.markdown(f"{badge} <span class='badge-rag'>pgvector cosine</span> &nbsp; **{pub}** · {date}", unsafe_allow_html=True)
                    if chunk:
                        st.markdown(f"> {chunk[:400]}{'...' if len(chunk)>400 else ''}")
                    if url != "#":
                        st.markdown(f"[🔗 Read full article]({url})")
        elif "rag_results" in st.session_state:
            st.warning("No matching documents. Try a different query or click **Refresh ETL** in the sidebar.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PORTFOLIO WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ⭐ Portfolio Watchlist")
    st.caption("Live read/write operations against Lakebase `watchlist_tickers` table.")

    wl_rows = run_query("""
        SELECT wt.ticker,
               COALESCE(c.name, wt.ticker) AS name,
               wt.target_buy_price, wt.target_sell_price,
               wt.notes, wt.added_at
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)

    if wl_rows:
        df_wl = pd.DataFrame(wl_rows)
        if "added_at" in df_wl.columns:
            df_wl["added_at"] = df_wl["added_at"].apply(fmt_date)
        for col in ["target_buy_price", "target_sell_price"]:
            if col in df_wl.columns:
                df_wl[col] = df_wl[col].apply(lambda v: safe_num(v))
        st.dataframe(
            df_wl.rename(columns={
                "ticker": "Ticker", "name": "Company",
                "target_buy_price": "Buy Target ($)", "target_sell_price": "Sell Target ($)",
                "notes": "Thesis Notes", "added_at": "Added Date",
            }),
            use_container_width=True, hide_index=True,
        )

        # Portfolio chart — current price vs buy/sell targets
        if _client_ok and wl_rows:
            chart_data = []
            for r in wl_rows:
                t = r["ticker"]
                try:
                    q = backend["client"].get_ticker_quote(t)
                    chart_data.append({
                        "Ticker": t,
                        "Current ($)": safe_num(q.get("close_price", 0)),
                        "Buy Target ($)": safe_num(r.get("target_buy_price", 0)),
                        "Sell Target ($)": safe_num(r.get("target_sell_price", 0)),
                    })
                except: pass

            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                fig_wl = go.Figure()
                fig_wl.add_trace(go.Bar(name="Current Price", x=df_chart["Ticker"], y=df_chart["Current ($)"], marker_color="#6366F1", opacity=0.9))
                fig_wl.add_trace(go.Scatter(name="Buy Target", x=df_chart["Ticker"], y=df_chart["Buy Target ($)"],
                    mode="markers+lines", marker=dict(size=10, color="#10B981", symbol="triangle-up"), line=dict(color="#10B981", dash="dot", width=1.5)))
                fig_wl.add_trace(go.Scatter(name="Sell Target", x=df_chart["Ticker"], y=df_chart["Sell Target ($)"],
                    mode="markers+lines", marker=dict(size=10, color="#EF4444", symbol="triangle-down"), line=dict(color="#EF4444", dash="dot", width=1.5)))
                dark_layout(fig_wl, height=300, title="Portfolio — Current Price vs. Buy/Sell Targets")
                st.plotly_chart(fig_wl, use_container_width=True)
    else:
        st.info("Your watchlist is empty. Add your first ticker below!")

    st.markdown("---")
    add_col, del_col = st.columns(2)

    with add_col:
        st.markdown("#### ➕ Add / Update Ticker")
        with st.form("wl_add_form", clear_on_submit=True):
            t_raw   = st.text_input("Ticker Symbol", placeholder="e.g. NVDA, SPY, QQQ, META, AMD…",
                                    help="Any valid stock ticker — not limited to the 6 defaults")
            buy_p   = st.number_input("Target Buy Price ($)",  min_value=0.0, value=120.0, step=5.0)
            sell_p  = st.number_input("Target Sell Price ($)", min_value=0.0, value=160.0, step=5.0)
            thesis  = st.text_area("Investment Thesis", "Strong structural tailwinds in AI compute infrastructure.", height=80)
            if st.form_submit_button("💾 Save to Lakebase", use_container_width=True, type="primary"):
                t = t_raw.strip().upper()
                if not t:
                    st.error("Enter a ticker symbol.")
                elif not t.isalpha() or len(t) > 6:
                    st.error("Ticker must be 1–6 letters (e.g. NVDA, SPY).")
                else:
                    run_write("INSERT INTO companies (ticker, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (t, f"{t} Corp"))
                    run_write("""
                        INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
                        VALUES ('default_watchlist', %s, %s, %s, %s)
                        ON CONFLICT (watchlist_id, ticker) DO UPDATE SET
                            target_buy_price=EXCLUDED.target_buy_price,
                            target_sell_price=EXCLUDED.target_sell_price,
                            notes=EXCLUDED.notes;
                    """, (t, buy_p, sell_p, thesis))
                    st.success(f"✅ {t} saved to Lakebase!")
                    st.rerun()

    with del_col:
        st.markdown("#### 🗑️ Remove Ticker")
        existing = [r["ticker"] for r in (wl_rows or [])]
        if not existing:
            st.info("Watchlist is empty — nothing to remove.")
        else:
            with st.form("wl_del_form", clear_on_submit=False):
                t_del = st.selectbox("Select Ticker to Remove", existing, key="wl_del_tick",
                                     help="Shows only tickers currently in your watchlist")
                if st.form_submit_button("🗑️ Remove from Watchlist", use_container_width=True):
                    cnt = run_write("DELETE FROM watchlist_tickers WHERE watchlist_id='default_watchlist' AND ticker=%s;", (t_del,))
                    st.success(f"✅ Removed {t_del}") if cnt > 0 else st.warning(f"{t_del} not found")
                    st.rerun()

    st.markdown("---")
    note_col, rep_col = st.columns(2)

    with note_col:
        st.markdown("#### 📝 Research Notes")
        note_rows = run_query("SELECT ticker, title, content, created_at FROM research_notes ORDER BY created_at DESC LIMIT 6;")
        if note_rows:
            for n in note_rows:
                with st.expander(f"[{safe_str(n.get('ticker'))}] {safe_str(n.get('title'))[:55]}"):
                    st.write(safe_str(n.get("content")))
                    st.caption(f"📅 {fmt_date(n.get('created_at'))}")
        else:
            st.caption("No notes yet — ask the AI Agent to save one!")

    with rep_col:
        st.markdown("#### 📊 Analysis Reports")
        rep_rows = run_query("SELECT ticker, recommendation, summary, bull_case, bear_case, created_at FROM analysis_reports ORDER BY created_at DESC LIMIT 6;")
        if rep_rows:
            for r in rep_rows:
                rec = safe_str(r.get("recommendation"), "HOLD")
                ico = "🟢" if rec == "BUY" else ("🔴" if rec == "SELL" else "🟡")
                with st.expander(f"{ico} [{safe_str(r.get('ticker'))}] {rec} · {fmt_date(r.get('created_at'))}"):
                    st.write(f"**Summary:** {safe_str(r.get('summary'))}")
                    st.write(f"**Bull:** {safe_str(r.get('bull_case'))}")
                    st.write(f"**Bear:** {safe_str(r.get('bear_case'))}")
        else:
            st.caption("No reports yet — ask the AI Agent to generate one!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI AGENT COPILOT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🤖 AI Investment Copilot")
    st.caption("ReAct agent with READ (RAG search, quotes, watchlist) and WRITE (add/remove, notes, reports) tools.")

    if not _agent_ok:
        st.error(f"⚠️ AI Agent unavailable: {backend.get('agent_error', 'Unknown')}")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    "Hi! I'm your AI Investment Copilot on Databricks Lakebase. Try:\n\n"
                    "- 🔍 `Search AI infrastructure news for NVDA`\n"
                    "- 📊 `Generate a BUY report for AAPL`\n"
                    "- ➕ `Add MSFT to my watchlist at 420`\n"
                    "- 📋 `Show my watchlist`\n"
                    "- 📝 `Save a research note for TSLA`"
                ), "actions": []
            }]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                for act in msg.get("actions", []):
                    st.markdown(f"<span class='badge-action'>⚡ {act}</span>", unsafe_allow_html=True)

        st.markdown("**Quick Commands:**")
        qc = st.columns(4)
        qp = None
        if qc[0].button("➕ Add NVDA @ 120", use_container_width=True): qp = "Add NVDA to my watchlist with target buy 120"
        if qc[1].button("🔍 AI News AAPL", use_container_width=True):   qp = "Search news about Apple artificial intelligence"
        if qc[2].button("📊 Analyse TSLA", use_container_width=True):   qp = "Generate a BUY analysis report for TSLA"
        if qc[3].button("📋 My Watchlist", use_container_width=True):   qp = "Show my current portfolio watchlist"

        user_input = st.chat_input("Ask the AI Agent about your portfolio or the market...") or qp

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input, "actions": []})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("AI Agent reasoning and selecting tools..."):
                    try:
                        resp    = backend["agent"].run(user_input)
                        answer  = safe_str(resp.get("answer", ""), "No response.")
                        actions = resp.get("actions_taken", [])
                        st.markdown(answer)
                        for act in actions:
                            st.markdown(f"<span class='badge-action'>⚡ {act}</span>", unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": answer, "actions": actions})
                    except Exception as e:
                        err = f"Agent error: {e}"
                        st.error(err)
                        st.session_state.messages.append({"role": "assistant", "content": err, "actions": []})

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
                color = "#10B981" if rw == "READ" else "#6366F1"
                st.markdown(
                    f"<div class='tool-row'><code style='color:{color}'>{rw}</code> &nbsp; "
                    f"<strong>{name}</strong><br><span style='color:#8892A4; font-size:0.82rem'>{desc}</span></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SYSTEM HEALTH
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⚡ PySpark Medallion Pipeline & System Health")

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("DB Status",      "Online"  if _db_ok    else "Offline",  delta=None)
    h2.metric("RAG Engine",     "Active"  if _rag_ok   else "Error")
    h3.metric("AI Agent",       "Online"  if _agent_ok else "Error")
    h4.metric("Market Client",  "Live"    if _client_ok else "Fallback")

    st.markdown("---")
    st.markdown("#### Architecture")
    st.code("""
  Massive REST API
       │
       ▼
  [Bronze Layer]  ─── PySpark: raw quote + news ingestion (6 tickers)
       │
       ▼
  [Silver Layer]  ─── Schema validation, sentiment enrichment, company upserts
       │
       ▼
  [Gold Layer]    ─── Business aggregations, price snapshots
       │
       ▼
  Lakebase PostgreSQL + pgvector
       │
   ┌───┴──────────────────────────────────┐
   ▼                                      ▼
Relational Tables                 news_embeddings (384-dim HNSW)
companies, watchlists, news…      ← sentence-transformers/all-MiniLM-L6-v2
reports, notes, snapshots         ← pgvector cosine similarity (<=>)
    """, language="text")

    st.markdown("---")
    st.markdown("#### Lakebase Table Record Audit")
    db_tables = ["users","companies","watchlists","watchlist_tickers",
                 "price_snapshots","news_articles","news_embeddings","research_notes","analysis_reports"]
    audit = []
    for t in db_tables:
        try:
            r   = run_query(f"SELECT COUNT(*) AS c FROM {t};")
            cnt = int(r[0]["c"]) if r else 0
            audit.append({"Table": t, "Records": cnt, "Status": "✅ Active"})
        except Exception as ex:
            audit.append({"Table": t, "Records": 0, "Status": f"⚠️ {str(ex)[:40]}"})
    st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)

    pi = st.session_state.get("pipeline_init", {})
    st.markdown("---")
    if pi.get("ok"):
        st.success(f"✅ {pi.get('message', 'Pipeline OK')}")
    else:
        st.error(f"⚠️ {pi.get('message', 'Unknown error')}")
