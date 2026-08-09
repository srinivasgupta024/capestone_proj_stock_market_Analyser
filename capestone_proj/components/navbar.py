"""
Sticky Top Navigation Bar Component.
Renders a permanently fixed top header displaying live system metrics, articles count, embeddings count, and session badge.
"""

import streamlit as st
from datetime import datetime

def render_navbar(run_query, total_tickers: int, session_id: str):
    total_news = 0
    total_emb = 0
    rows_n = run_query("SELECT COUNT(*) AS c FROM news_articles;")
    rows_e = run_query("SELECT COUNT(*) AS c FROM news_embeddings;")
    if rows_n: total_news = int(rows_n[0]["c"])
    if rows_e: total_emb = int(rows_e[0]["c"])

    st.markdown(f"""
    <div class="topnav">
      <div>
        <div class="topnav-brand">📈 LakePulse AI</div>
        <div class="topnav-sub">Enterprise Financial Intelligence · Databricks Lakebase · PySpark Medallion ETL · pgvector RAG · ReAct Copilot</div>
      </div>
      <div class="topnav-right">
        <div class="topnav-stat">
          <div class="topnav-stat-val">{total_news:,}</div>
          <div class="topnav-stat-lbl">Articles</div>
        </div>
        <div style="width:1px;height:28px;background:rgba(255,255,255,0.08)"></div>
        <div class="topnav-stat">
          <div class="topnav-stat-val">{total_emb:,}</div>
          <div class="topnav-stat-lbl">Embeddings</div>
        </div>
        <div style="width:1px;height:28px;background:rgba(255,255,255,0.08)"></div>
        <div class="topnav-stat">
          <div class="topnav-stat-val">{total_tickers}</div>
          <div class="topnav-stat-lbl">Tickers</div>
        </div>
        <div style="width:1px;height:28px;background:rgba(255,255,255,0.08)"></div>
        <div>
          <span class="badge-sess">⬡ Session: {session_id}</span>
          <div style="font-size:0.65rem;color:#4B5568;text-align:right;margin-top:2px">{datetime.now().strftime("%b %d, %H:%M")}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
