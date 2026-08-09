"""
Sleek Informational Sidebar Component.
Renders branding, active system status indicators, pipeline trigger control, and environment info.
"""

import streamlit as st

def render_sidebar(backend: dict, init_pipeline_func, refresh_display_func, default_tickers: list):
    _db_ok     = backend.get("db_ok", False)
    _client_ok = backend.get("client_ok", False)
    _rag_ok    = backend.get("rag_ok", False)
    _agent_ok  = backend.get("agent_ok", False)

    with st.sidebar:
        st.markdown("""
        <div style="padding:4px 0 14px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:6px">
          <div style="font-size:1.20rem;font-weight:800;color:#E8EDFF;letter-spacing:-0.5px">📈 LakePulse AI</div>
          <div style="font-size:0.68rem;color:#6B7280;margin-top:1px">Databricks Capstone · 2026</div>
        </div>
        """, unsafe_allow_html=True)

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
                f"<span style='font-size:0.72rem;color:#6B7280'>{t}</span></div>",
                unsafe_allow_html=True
            )

        pi = st.session_state.get("pipeline_init", {})
        color = "#10B981" if pi.get("ok") else "#EF4444"
        msg   = "Pipeline ready" if pi.get("ok") else pi.get("message","Error")[:50]
        bg    = "rgba(16,185,129,0.08)" if pi.get("ok") else "rgba(239,68,68,0.08)"
        bc    = "rgba(16,185,129,0.2)"  if pi.get("ok") else "rgba(239,68,68,0.2)"
        st.markdown(
            f"<div style='font-size:0.72rem;color:{color};margin-top:6px;padding:5px 9px;"
            f"background:{bg};border-radius:8px;border:1px solid {bc}'>{'✅' if pi.get('ok') else '⚠️'} {msg}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<span class='sb-label'>Data Pipeline Control</span>", unsafe_allow_html=True)
        if st.button("🔄 Refresh ETL & RAG Pipeline", use_container_width=True):
            st.markdown("<div class='custom-loader-badge'>⚙️ Executing PySpark Medallion ETL...</div>", unsafe_allow_html=True)
            try:
                from src.spark_pipeline.ingestion import run_bronze_ingestion
                from src.spark_pipeline.transformations import process_silver_gold_and_persist
                from src.spark_pipeline.embeddings import generate_and_store_news_embeddings
                prices, news = run_bronze_ingestion(default_tickers)
                process_silver_gold_and_persist(prices, news)
                count = generate_and_store_news_embeddings()
                init_pipeline_func.clear()
                refresh_display_func.clear()
                st.success(f"✅ {count} vector embeddings synced!")
            except Exception as e:
                st.error(str(e)[:100])

        st.markdown(
            "<div style='position:fixed;bottom:12px;left:0;width:238px;text-align:center;"
            "font-size:0.68rem;color:#374151;padding:0 14px'>Built with Streamlit · Databricks Lakebase · pgvector</div>",
            unsafe_allow_html=True
        )
