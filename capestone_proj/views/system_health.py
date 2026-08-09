"""
View Module: System & Data Telemetry (Tab 5).
Features live Lakebase record audit tables, Medallion lineage visualizer, and session diagnostic metrics.
"""

import streamlit as st

def render_system_health(run_query, backend: dict, session_id: str, all_tickers: list):
    _db_ok     = backend.get("db_ok", False)
    _client_ok = backend.get("client_ok", False)
    _rag_ok    = backend.get("rag_ok", False)
    _agent_ok  = backend.get("agent_ok", False)

    st.markdown("### ⚡ Pipeline & System Telemetry")

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
    st.markdown("#### 🏗️ Live Medallion Architecture Lineage")
    st.code("""
  Massive REST API
       │
       ▼
  [Bronze Layer]  ─── PySpark: Raw quote + news ingestion (REST API endpoint)
       │
       ▼
  [Silver Layer]  ─── Schema validation · NLP sentiment enrichment · text chunking
       │
       ▼
  [Gold Layer]    ─── Business aggregations · price snapshots · company reference dimensions
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
    st.markdown("#### 📋 Current Session Telemetry")
    sess_data = {
        "Session ID": session_id,
        "Session Started": st.session_state.session_started,
        "Chat Messages": len(st.session_state.messages),
        "Tickers Loaded": len(all_tickers),
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
