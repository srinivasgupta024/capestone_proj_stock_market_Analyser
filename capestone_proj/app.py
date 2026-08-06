"""
AI Stock Market Research Assistant - Databricks App Entrypoint.
Full-stack Streamlit frontend connecting to Databricks Lakebase,
PySpark ETL pipeline, Vector RAG, and ReAct AI Agent.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import logging

# Page Configuration
st.set_page_config(
    page_title="AI Stock Market Research Copilot | Databricks Lakebase",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling (Glassmorphism & Sleek Dark Mode Theme)
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .badge-action {
        background-color: #00D26A;
        color: #000000;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .badge-rag {
        background-color: #FF9900;
        color: #000000;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# App Imports
from src.lakebase import init_db, run_query, run_write
from src.spark_pipeline.ingestion import run_bronze_ingestion
from src.spark_pipeline.transformations import process_silver_gold_and_persist
from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
from src.rag.vector_search import search_news_vector
from src.agent.agent_engine import StockMarketAgent
from src.massive_client import MassiveClient

# Initialize DB Schema on Startup
@st.cache_resource
def setup_application():
    try:
        init_db()
        # Initial PySpark & Embedding Pipeline trigger
        prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
        process_silver_gold_and_persist(prices, news)
        generate_and_store_news_embeddings()
    except Exception as e:
        st.warning(f"Initial setup note: {e}")

setup_application()

# Instantiate Agent & API Client
agent = StockMarketAgent()
client = MassiveClient()

# Header & Sidebar Navigation
st.title("📈 AI Stock Market Research Assistant")
st.caption("Powered by Databricks Apps, Lakebase (Postgres + pgvector), PySpark ETL, & Tool-Calling AI Agent")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=180)
    st.subheader("System Status")
    st.success("🟢 Databricks Lakebase: Connected")
    st.info("⚡ Spark Pipeline: Medallion Active")
    st.warning("🔍 Vector RAG Engine: pgvector (384-dim)")

    st.markdown("---")
    st.subheader("Data Refresh Controls")
    if st.button("🔄 Trigger PySpark ETL & RAG Pipeline", use_container_width=True):
        with st.spinner("Executing PySpark Bronze → Silver → Gold ETL and chunk embeddings..."):
            prices, news = run_bronze_ingestion(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
            process_silver_gold_and_persist(prices, news)
            count = generate_and_store_news_embeddings()
            st.success(f"ETL completed! Embedded {count} news chunks into Lakebase.")

# Layout Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Intelligence", 
    "🔍 Unstructured Vector RAG", 
    "⭐ Portfolio Watchlist", 
    "🤖 AI Agent Copilot"
])

# --- TAB 1: MARKET INTELLIGENCE & ANALYTICS ---
with tab1:
    st.header("Real-Time Market Intelligence")
    
    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        comp_count = run_query("SELECT COUNT(*) AS c FROM companies;")[0]["c"]
        st.metric("Tracked Companies", f"{comp_count} Tickers")
    with col2:
        watch_count = run_query("SELECT COUNT(*) AS c FROM watchlist_tickers;")[0]["c"]
        st.metric("Portfolio Watchlist", f"{watch_count} Items")
    with col3:
        news_count = run_query("SELECT COUNT(*) AS c FROM news_articles;")[0]["c"]
        st.metric("News Index", f"{news_count} Articles")
    with col4:
        emb_count = run_query("SELECT COUNT(*) AS c FROM news_embeddings;")[0]["c"]
        st.metric("Vector Embeddings", f"{emb_count} Chunks")

    st.markdown("---")
    
    # Interactive Stock Selection & Plotly Chart
    selected_ticker = st.selectbox("Select Ticker to Analyze", ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"], index=0)
    
    quote = client.get_ticker_quote(selected_ticker)
    
    chart_col, info_col = st.columns([2, 1])
    
    with chart_col:
        st.subheader(f"{selected_ticker} Price Action & Indicators")
        # Generate price visualization
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Open", "Low", "Close", "High"],
            y=[quote["open_price"], quote["low_price"], quote["close_price"], quote["high_price"]],
            marker_color=["#1E88E5", "#E53935", "#43A047", "#FB8C00"]
        ))
        fig.update_layout(
            template="plotly_dark",
            title=f"{selected_ticker} Daily Snapshot Price Range ($)",
            yaxis_title="Stock Price ($)",
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

    with info_col:
        st.subheader("Fundamentals")
        company_data = run_query("SELECT * FROM companies WHERE ticker = %s;", (selected_ticker,))
        if company_data:
            c = company_data[0]
            st.write(f"**Name:** {c.get('name')}")
            st.write(f"**Sector:** {c.get('sector')}")
            st.write(f"**Market Cap:** ${c.get('market_cap', 0):,}")
            st.write(f"**P/E Ratio:** {c.get('pe_ratio')}")
            st.info(f"**Overview:** {c.get('description')}")
        else:
            st.write("Company details loading...")

# --- TAB 2: UNSTRUCTURED VECTOR RAG SEARCH ---
with tab2:
    st.header("Unstructured Data Vector RAG Explorer")
    st.caption("Search across financial news, earning reports, and analyst notes using pgvector semantic cosine similarity.")

    search_query = st.text_input("Enter Semantic Query", "companies expanding AI data center infrastructure and high cloud demand", key="rag_search")
    filter_ticker = st.selectbox("Filter by Ticker (Optional)", ["All Tickers", "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "TSLA"])
    
    ticker_param = None if filter_ticker == "All Tickers" else filter_ticker
    
    if st.button("🔍 Execute Semantic Vector Search"):
        with st.spinner("Computing 384-dimensional query vector and querying pgvector index..."):
            rag_results = search_news_vector(search_query, ticker=ticker_param, top_k=5)
            
            if rag_results:
                st.success(f"Found {len(rag_results)} semantically relevant documents:")
                for idx, r in enumerate(rag_results):
                    score = r.get("similarity_score", 0)
                    with st.expander(f"#{idx+1} [{r.get('ticker')}] {r.get('title')} — Similarity: {score:.4f}"):
                        st.markdown(f"**Publisher:** {r.get('publisher')} | **Sentiment:** `{r.get('sentiment')}`")
                        st.write(f"**Retrieved Text Chunk:** {r.get('chunk_text')}")
                        if r.get("article_url"):
                            st.markdown(f"[Read Source Article]({r.get('article_url')})")
            else:
                st.warning("No relevant articles found for this query.")

# --- TAB 3: PORTFOLIO WATCHLIST & DATABASE ACTIONS ---
with tab3:
    st.header("Portfolio Watchlist & Lakebase Persistence")

    # Display Current Watchlist
    watchlist_items = run_query("""
        SELECT wt.ticker, c.name, wt.target_buy_price, wt.target_sell_price, wt.notes, wt.added_at
        FROM watchlist_tickers wt
        LEFT JOIN companies c ON wt.ticker = c.ticker
        WHERE wt.watchlist_id = 'default_watchlist'
        ORDER BY wt.added_at DESC;
    """)

    st.subheader("Your Current Watchlist (Lakebase Table)")
    if watchlist_items:
        df_watch = pd.DataFrame(watchlist_items)
        st.dataframe(df_watch, use_container_width=True)
    else:
        st.info("Watchlist is currently empty.")

    st.markdown("---")

    col_add, col_notes = st.columns(2)
    
    with col_add:
        st.subheader("➕ Add / Update Watchlist Item")
        with st.form("add_watchlist_form"):
            t_input = st.selectbox("Ticker", ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"])
            target_buy = st.number_input("Target Buy Price ($)", min_value=0.0, value=120.0, step=5.0)
            target_sell = st.number_input("Target Sell Price ($)", min_value=0.0, value=160.0, step=5.0)
            notes_input = st.text_area("Investment Thesis Notes", "Strong growth prospects in generative AI enterprise workloads.")
            
            if st.form_submit_button("Save to Lakebase"):
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

    with col_notes:
        st.subheader("📝 Saved AI Research Notes")
        notes = run_query("SELECT ticker, title, content, created_at FROM research_notes ORDER BY created_at DESC LIMIT 5;")
        if notes:
            for n in notes:
                with st.expander(f"[{n['ticker']}] {n['title']}"):
                    st.write(n['content'])
                    st.caption(f"Created: {n['created_at']}")
        else:
            st.caption("No research notes saved yet. Ask the AI Agent to save a note!")

# --- TAB 4: AI INVESTMENT COPILOT AGENT WORKSPACE ---
with tab4:
    st.header("🤖 AI Agent Copilot")
    st.caption("Ask questions, perform semantic retrieval, or command the agent to modify your database in real-time.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Investment Copilot on Databricks Lakebase. You can ask me to search news, check stock prices, add tickers to your watchlist, or save research notes!"}
        ]

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "actions" in msg:
                for act in msg["actions"]:
                    st.markdown(f"<span class='badge-action'>⚡ Action Executed</span> `{act}`", unsafe_allow_html=True)

    # Sample Quick Prompts
    st.write("💡 **Quick Prompt Examples:**")
    prompt_cols = st.columns(4)
    quick_prompt = None
    if prompt_cols[0].button("Add NVDA to watchlist"):
        quick_prompt = "Add NVDA to my watchlist with target buy 120"
    if prompt_cols[1].button("Search AI news for Apple"):
        quick_prompt = "Search news about Apple AI and cloud infrastructure"
    if prompt_cols[2].button("Generate report for TSLA"):
        quick_prompt = "Generate a BUY analysis report for TSLA"
    if prompt_cols[3].button("Show my watchlist"):
        quick_prompt = "Show my current portfolio watchlist"

    user_input = st.chat_input("Type your command or question for the AI Agent...") or quick_prompt

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("AI Agent evaluating query and selecting tools..."):
                response = agent.run(user_input)
                answer = response["answer"]
                actions = response.get("actions_taken", [])

                st.markdown(answer)
                for act in actions:
                    st.markdown(f"<span class='badge-action'>⚡ Action Executed</span> `{act}`", unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "actions": actions
                })
