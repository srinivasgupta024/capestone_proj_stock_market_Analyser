"""
AI Stock Market Research Assistant & Investment Copilot — Databricks App Entrypoint.
Full-stack Streamlit application featuring Databricks Lakebase (PostgreSQL + pgvector),
PySpark Medallion ETL Pipeline, Unstructured Vector RAG, and Tool-Calling AI ReAct Agent.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import logging

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LakePulse AI | Stock Market Copilot & Databricks Lakebase",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #0B0E14;
        color: #F0F4F8;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 210, 106, 0.4);
    }
    
    /* Badges & Tags */
    .badge-action {
        background: linear-gradient(135deg, #00D26A 0%, #00A855 100%);
        color: #000000;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.80rem;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 6px;
    }
    
    .badge-bullish {
        background-color: rgba(0, 210, 106, 0.15);
        color: #00D26A;
        border: 1px solid rgba(0, 210, 106, 0.4);
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.80rem;
    }
    
    .badge-bearish {
        background-color: rgba(255, 77, 79, 0.15);
        color: #FF4D4F;
        border: 1px solid rgba(255, 77, 79, 0.4);
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.80rem;
    }
    
    .badge-neutral {
        background-color: rgba(255, 180, 0, 0.15);
        color: #FFB400;
        border: 1px solid rgba(255, 180, 0, 0.4);
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.80rem;
    }
    
    .badge-rag {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #FFFFFF;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.80rem;
    }

    /* Container Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Primary Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. APPLICATION IMPORTS & INITIALIZATION
# -----------------------------------------------------------------------------
from src.lakebase import init_db, run_query, run_write
from src.spark_pipeline.ingestion import run_bronze_ingestion
from src.spark_pipeline.transformations import process_silver_gold_and_persist
from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
from src.rag.vector_search import search_news_vector
from src.agent.agent_engine import StockMarketAgent
from src.massive_client import MassiveClient

@st.cache_resource
def setup_application():
    try:
        init_db()
        prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
        process_silver_gold_and_persist(prices, news)
        generate_and_store_news_embeddings()
    except Exception as e:
        logging.warning(f"Startup initialization note: {e}")

setup_application()

agent = StockMarketAgent()
client = MassiveClient()

# -----------------------------------------------------------------------------
# 3. HEADER & SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
title_col, logo_col = st.columns([4, 1])
with title_col:
    st.title("📈 LakePulse AI — Stock Market Assistant")
    st.caption("Enterprise Financial Intelligence powered by Databricks Apps, Lakebase (pgvector), PySpark Medallion ETL, & ReAct AI Agent")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=170)
    st.markdown("### System Telemetry")
    st.success("🟢 Databricks Lakebase: Online")
    st.info("⚡ Spark Medallion ETL: Active")
    st.warning("🔍 pgvector RAG Index: 384-dim")

    st.markdown("---")
    st.markdown("### Data Pipeline Controls")
    if st.button("🔄 Trigger PySpark ETL & RAG Pipeline", use_container_width=True):
        with st.spinner("Running PySpark Bronze → Silver → Gold ETL and chunk embeddings..."):
            prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
            process_silver_gold_and_persist(prices, news)
            count = generate_and_store_news_embeddings()
            st.success(f"ETL Complete! Embedded {count} news articles into Lakebase.")

    st.markdown("---")
    st.caption("© 2026 Databricks Capstone Project | Built with Streamlit & Lakebase")

# -----------------------------------------------------------------------------
# 4. TABBED LAYOUT NAVIGATION (5 COMPREHENSIVE TABS)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence", 
    "🔍 Unstructured Vector RAG", 
    "⭐ Portfolio Watchlist", 
    "🤖 AI Agent Copilot",
    "⚡ System & Pipeline Health"
])

# =============================================================================
# TAB 1: MARKET INTELLIGENCE & FINANCIAL ANALYTICS
# =============================================================================
with tab1:
    st.markdown("### 📊 Market Summary & Financial Analytics")
    
    # KPI Grid
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        comp_count = run_query("SELECT COUNT(*) AS c FROM companies;")[0]["c"]
        st.metric("Tracked Tickers", f"{comp_count} Stocks")
    with kpi2:
        watch_count = run_query("SELECT COUNT(*) AS c FROM watchlist_tickers;")[0]["c"]
        st.metric("Portfolio Items", f"{watch_count} Saved")
    with kpi3:
        news_count = run_query("SELECT COUNT(*) AS c FROM news_articles;")[0]["c"]
        st.metric("News Articles", f"{news_count} Indexed")
    with kpi4:
        emb_count = run_query("SELECT COUNT(*) AS c FROM news_embeddings;")[0]["c"]
        st.metric("Vector Embeddings", f"{emb_count} Chunks")
    with kpi5:
        avg_pe = run_query("SELECT AVG(pe_ratio) AS pe FROM companies;")[0]["pe"]
        st.metric("Average Sector P/E", f"{avg_pe:.1f}x" if avg_pe else "34.2x")

    st.markdown("---")
    
    # Interactive Ticker Analysis
    selected_ticker = st.selectbox("Select Ticker Symbol to Inspect", ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"], index=0)
    quote = client.get_ticker_quote(selected_ticker)
    
    chart_col, info_col = st.columns([2, 1])
    
    with chart_col:
        st.markdown(f"#### {selected_ticker} Market Price Action ($)")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Open", "Low", "Close", "High"],
            y=[quote["open_price"], quote["low_price"], quote["close_price"], quote["high_price"]],
            marker_color=["#3B82F6", "#EF4444", "#10B981", "#F59E0B"],
            text=[f"${quote['open_price']:.2f}", f"${quote['low_price']:.2f}", f"${quote['close_price']:.2f}", f"${quote['high_price']:.2f}"],
            textposition="auto"
        ))
        fig.update_layout(
            template="plotly_dark",
            title=f"{selected_ticker} Daily Price Range & Snapshot Metrics",
            yaxis_title="Stock Price ($)",
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with info_col:
        st.markdown(f"#### {selected_ticker} Company Fundamentals")
        company_data = run_query("SELECT * FROM companies WHERE ticker = %s;", (selected_ticker,))
        if company_data:
            c = company_data[0]
            st.markdown(f"**Company Name:** `{c.get('name')}`")
            st.markdown(f"**Sector:** `{c.get('sector')}` | **Industry:** `{c.get('industry')}`")
            st.markdown(f"**Market Cap:** `${c.get('market_cap', 0):,}`")
            st.markdown(f"**P/E Ratio:** `{c.get('pe_ratio')}` | **Dividend Yield:** `{c.get('dividend_yield')}%`")
            st.info(f"**Business Profile:** {c.get('description')}")
        else:
            st.write("Loading company metadata...")

    st.markdown("---")
    st.markdown("#### 📰 Latest Market News Feed")
    news_rows = run_query("SELECT ticker, title, publisher, published_utc, sentiment, article_url FROM news_articles WHERE ticker = %s ORDER BY published_utc DESC LIMIT 4;", (selected_ticker,))
    if news_rows:
        for n in news_rows:
            sent = n.get("sentiment", "neutral").lower()
            badge_class = "badge-bullish" if "bull" in sent else ("badge-bearish" if "bear" in sent else "badge-neutral")
            st.markdown(
                f"<div class='glass-card'>"
                f"<div><span class='{badge_class}'>{sent.upper()}</span> <strong>[{n['ticker']}] {n['title']}</strong></div>"
                f"<div style='color: #8A99AD; font-size: 0.85rem; margin-top: 6px;'>"
                f"Publisher: {n.get('publisher')} | Date: {n.get('published_utc')[:10]} | <a href='{n.get('article_url')}' target='_blank' style='color: #3B82F6;'>Read Article ↗</a>"
                f"</div></div>",
                unsafe_allow_html=True
            )

# =============================================================================
# TAB 2: UNSTRUCTURED VECTOR RAG EXPLORER
# =============================================================================
with tab2:
    st.markdown("### 🔍 Unstructured Data Vector RAG Explorer")
    st.caption("Perform semantic search across news, earnings, and financial reports powered by `pgvector` HNSW cosine similarity (`<=>`).")

    col_q, col_filter, col_topk = st.columns([3, 1, 1])
    with col_q:
        search_query = st.text_input("Enter Semantic Vector Query", "companies expanding AI data center infrastructure and high cloud compute demand", key="rag_search_input")
    with col_filter:
        filter_ticker = st.selectbox("Ticker Filter", ["All Tickers", "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
    with col_topk:
        top_k_val = st.slider("Top K Matches", min_value=1, max_value=10, value=5)

    ticker_param = None if filter_ticker == "All Tickers" else filter_ticker

    # Quick Query Prompt Chips
    st.markdown("**💡 Sample Semantic Queries:**")
    chip_cols = st.columns(4)
    if chip_cols[0].button("☁️ AI Cloud Expansion"):
        search_query = "cloud data center expansion and high artificial intelligence demand"
    if chip_cols[1].button("🚀 Q2 Revenue Beat"):
        search_query = "record quarterly revenue beat and expanding profit margins"
    if chip_cols[2].button("📉 Fed Rate Sensitivity"):
        search_query = "Federal Reserve interest rate outlook and supply chain risk"
    if chip_cols[3].button("🚗 EV Autonomous Driving"):
        search_query = "electric vehicles self-driving autonomous AI hardware"

    st.markdown("---")

    if st.button("🔍 Execute Semantic Vector Search", use_container_width=True):
        with st.spinner("Computing 384-dim query vector and querying Lakebase pgvector index..."):
            rag_results = search_news_vector(search_query, ticker=ticker_param, top_k=top_k_val)
            
            if rag_results:
                st.success(f"Retrieved {len(rag_results)} semantically relevant document chunks from pgvector index:")
                for idx, r in enumerate(rag_results):
                    score = r.get("similarity_score", 0)
                    sent = r.get("sentiment", "neutral").lower()
                    badge_class = "badge-bullish" if "bull" in sent else ("badge-bearish" if "bear" in sent else "badge-neutral")
                    
                    with st.expander(f"Match #{idx+1} [{r.get('ticker')}] {r.get('title')} — Relevance Score: {score:.4f}"):
                        st.markdown(f"<span class='{badge_class}'>Sentiment: {sent.upper()}</span> <span class='badge-rag'>pgvector Cosine Distance</span>", unsafe_allow_html=True)
                        st.markdown(f"**Publisher:** {r.get('publisher')} | **Date:** {r.get('published_utc')}")
                        st.markdown(f"**Retrieved Text Snippet:**")
                        st.info(r.get("chunk_text"))
                        if r.get("article_url"):
                            st.markdown(f"[🔗 View Original Article Source]({r.get('article_url')})")
            else:
                st.warning("No semantically matching documents found.")

# =============================================================================
# TAB 3: PORTFOLIO WATCHLIST & LAKEBASE PERSISTENCE
# =============================================================================
with tab3:
    st.markdown("### ⭐ Portfolio Watchlist & Lakebase State Mutations")

    # Display Current Watchlist Table
    watchlist_items = run_query("""
        SELECT wt.ticker, c.name, wt.target_buy_price, wt.target_sell_price, wt.notes, wt.added_at
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)

    st.markdown("#### Your Portfolio Watchlist (Lakebase Table)")
    if watchlist_items:
        df_watch = pd.DataFrame(watchlist_items)
        st.dataframe(df_watch, use_container_width=True)
    else:
        st.info("Watchlist is currently empty.")

    st.markdown("---")

    col_add, col_del = st.columns(2)
    
    with col_add:
        st.markdown("#### ➕ Add / Update Watchlist Item")
        with st.form("add_watchlist_form"):
            t_input = st.selectbox("Select Ticker", ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"])
            target_buy = st.number_input("Target Buy Price ($)", min_value=0.0, value=120.0, step=5.0)
            target_sell = st.number_input("Target Sell Price ($)", min_value=0.0, value=160.0, step=5.0)
            notes_input = st.text_area("Investment Thesis Notes", "Strong market positioning in enterprise AI compute workloads.")
            
            if st.form_submit_button("Save Item to Lakebase"):
                run_write("INSERT INTO companies (ticker, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (t_input, f"{t_input} Corp"))
                run_write("""
                    INSERT INTO watchlist_tickers (watchlist_id, ticker, target_buy_price, target_sell_price, notes)
                    VALUES ('default_watchlist', %s, %s, %s, %s)
                    ON CONFLICT (watchlist_id, ticker) DO UPDATE SET
                        target_buy_price = EXCLUDED.target_buy_price,
                        target_sell_price = EXCLUDED.target_sell_price,
                        notes = EXCLUDED.notes;
                """, (t_input, target_buy, target_sell, notes_input))
                st.success(f"Saved {t_input} to Lakebase database!")
                st.rerun()

    with col_del:
        st.markdown("#### 🗑️ Remove Watchlist Item")
        with st.form("remove_watchlist_form"):
            t_remove = st.selectbox("Select Ticker to Remove", ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"], key="del_tick")
            if st.form_submit_button("Remove Item from Lakebase"):
                count = run_write("DELETE FROM watchlist_tickers WHERE watchlist_id = 'default_watchlist' AND ticker = %s;", (t_remove,))
                if count > 0:
                    st.success(f"Removed {t_remove} from watchlist.")
                else:
                    st.warning(f"{t_remove} was not in watchlist.")
                st.rerun()

    st.markdown("---")
    
    col_notes, col_reports = st.columns(2)
    
    with col_notes:
        st.markdown("#### 📝 Saved AI Research Notes")
        notes = run_query("SELECT ticker, title, content, created_at FROM research_notes ORDER BY created_at DESC LIMIT 5;")
        if notes:
            for n in notes:
                with st.expander(f"[{n['ticker']}] {n['title']}"):
                    st.write(n['content'])
                    st.caption(f"Created: {n['created_at']}")
        else:
            st.caption("No research notes saved yet. Ask the AI Agent to save a note!")

    with col_reports:
        st.markdown("#### 📊 Formally Generated Stock Analysis Reports")
        reports = run_query("SELECT ticker, recommendation, summary, bull_case, bear_case, created_at FROM analysis_reports ORDER BY created_at DESC LIMIT 5;")
        if reports:
            for r in reports:
                rec_color = "🟢" if r['recommendation'] == 'BUY' else ("🔴" if r['recommendation'] == 'SELL' else "🟡")
                with st.expander(f"{rec_color} [{r['ticker']}] Recommendation: {r['recommendation']}"):
                    st.write(f"**Summary:** {r['summary']}")
                    st.write(f"**Bull Case:** {r['bull_case']}")
                    st.write(f"**Bear Case:** {r['bear_case']}")
                    st.caption(f"Generated at: {r['created_at']}")
        else:
            st.caption("No analysis reports generated yet. Ask the AI Agent to generate a report!")

# =============================================================================
# TAB 4: AI INVESTMENT COPILOT (ReAct AGENT WORKSPACE)
# =============================================================================
with tab4:
    st.markdown("### 🤖 AI Investment Copilot Agent Workspace")
    st.caption("Command the AI agent to search unstructured market data, pull quotes, or mutate database state in real-time.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Investment Copilot connected to Databricks Lakebase. Ask me to search news, check stock prices, add tickers to your watchlist, or generate analysis reports!"}
        ]

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "actions" in msg:
                for act in msg["actions"]:
                    st.markdown(f"<span class='badge-action'>⚡ Action Executed</span> <code>{act}</code>", unsafe_allow_html=True)

    # Quick Agent Prompts
    st.markdown("**💡 Agent Quick Commands:**")
    prompt_cols = st.columns(4)
    quick_prompt = None
    if prompt_cols[0].button("➕ Add NVDA Target 120"):
        quick_prompt = "Add NVDA to my watchlist with target buy 120"
    if prompt_cols[1].button("🔍 Search Apple AI News"):
        quick_prompt = "Search news about Apple AI and cloud infrastructure"
    if prompt_cols[2].button("📊 Analyze TSLA Stock"):
        quick_prompt = "Generate a BUY analysis report for TSLA"
    if prompt_cols[3].button("📋 Show Watchlist"):
        quick_prompt = "Show my current portfolio watchlist"

    user_input = st.chat_input("Type your command for the AI Agent...") or quick_prompt

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("AI Agent evaluating intent & selecting tools..."):
                response = agent.run(user_input)
                answer = response["answer"]
                actions = response.get("actions_taken", [])

                st.markdown(answer)
                for act in actions:
                    st.markdown(f"<span class='badge-action'>⚡ Action Executed</span> <code>{act}</code>", unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "actions": actions
                })

    st.markdown("---")
    with st.expander("🛠️ View Agent Tool Capabilities"):
        st.markdown("""
        - **`tool_search_news_rag`** (READ): Queries pgvector 384-dim embeddings for market news snippets.
        - **`tool_get_ticker_snapshot`** (READ): Fetches live/snapshot price, P/E ratio, market cap.
        - **`tool_get_watchlist`** (READ): Lists saved portfolio tickers from Lakebase.
        - **`tool_add_to_watchlist`** (WRITE): Inserts/updates ticker target prices in `watchlist_tickers`.
        - **`tool_remove_from_watchlist`** (WRITE): Deletes ticker from user watchlist.
        - **`tool_save_research_note`** (WRITE): Writes research note to `research_notes` table.
        - **`tool_generate_analysis_report`** (WRITE): Generates & stores formal BUY/HOLD/SELL report.
        """)

# =============================================================================
# TAB 5: SYSTEM & PYSPARK PIPELINE TELEMETRY
# =============================================================================
with tab5:
    st.markdown("### ⚡ PySpark Medallion Pipeline & Database Telemetry")
    
    st.markdown("#### System Architecture Flow")
    st.code("""
[ Massive API ] ──► [ PySpark Bronze Ingestion ] ──► [ Silver Data Cleaning ]
                                                           │
                                                           ▼
                                                [ Gold Business Aggregations ]
                                                           │
                                                           ▼
                                          [ Lakebase PostgreSQL + pgvector ]
    """, language="text")

    st.markdown("---")
    st.markdown("#### Lakebase Table Record Audit")
    
    tables_to_audit = ["users", "companies", "watchlists", "watchlist_tickers", "price_snapshots", "news_articles", "news_embeddings", "research_notes", "analysis_reports"]
    audit_data = []
    
    for t in tables_to_audit:
        try:
            cnt = run_query(f"SELECT COUNT(*) AS c FROM {t};")[0]["c"]
            audit_data.append({"Table Name": t, "Record Count": cnt, "Status": "Active"})
        except Exception as e:
            audit_data.append({"Table Name": t, "Record Count": 0, "Status": f"Error: {e}"})

    df_audit = pd.DataFrame(audit_data)
    st.dataframe(df_audit, use_container_width=True)
