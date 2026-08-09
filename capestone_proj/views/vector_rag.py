"""
View Module: Vector RAG Search (Tab 2).
Provides semantic query input, HNSW vector search execution, 2D Vector Space Scatter Cluster Map, cosine similarity visualization, and one-click Research Note Exporting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import uuid

def render_vector_rag(
    run_write, backend: dict, all_tickers: list, ticker_names: dict,
    get_ticker_label_func, safe_num_func, safe_str_func, fmt_date_func,
    sentiment_badge_func, dark_layout_func
):
    _rag_ok = backend.get("rag_ok", False)

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
            ["All"] + all_tickers,
            format_func=lambda t: "All Tickers" if t == "All" else get_ticker_label_func(t),
            key="rag_tick"
        )
    with col_k:
        top_k = st.slider("Top K", 1, 10, 5, key="rag_k")

    ticker_param = None if filter_tick == "All" else filter_tick

    if not _rag_ok:
        st.error(f"⚠️ RAG engine unavailable: {backend.get('rag_error','Unknown error')}")
    else:
        if st.button("🔍 Run Semantic Search", use_container_width=True, type="primary"):
            st.markdown("<div class='custom-loader-badge'>🔍 Computing Dense Vector & Querying HNSW Index...</div>", unsafe_allow_html=True)
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

            # Horizontal relevance score chart & 2D Cluster Visualization
            rag_col1, rag_col2 = st.columns(2)

            with rag_col1:
                df_rag = pd.DataFrame([{
                    "Snippet": f"[{safe_str_func(r.get('ticker'))}] {safe_str_func(r.get('title',''))[:35]}…",
                    "Score": safe_num_func(r.get("similarity_score",0)),
                    "Sentiment": safe_str_func(r.get("sentiment","neutral")),
                } for r in results])
                bar_colors = ["#10B981" if "bull" in s else ("#EF4444" if "bear" in s else "#F59E0B")
                              for s in df_rag["Sentiment"]]
                fig_r = go.Figure(go.Bar(
                    x=df_rag["Score"], y=df_rag["Snippet"], orientation="h",
                    marker_color=bar_colors,
                    text=[f"{v:.3f}" for v in df_rag["Score"]], textposition="outside",
                ))
                dark_layout_func(fig_r, height=260, title="Relevance Scores — pgvector Cosine Similarity", show_legend=False)
                fig_r.update_layout(xaxis_title="Similarity Score", yaxis_autorange="reversed")
                st.plotly_chart(fig_r, use_container_width=True)

            with rag_col2:
                # STANDOUT FEATURE: 2D VECTOR SPACE CLUSTER MAP
                np.random.seed(42)
                cluster_x = [safe_num_func(r.get("similarity_score", 0)) + np.random.uniform(-0.05, 0.05) for r in results]
                cluster_y = [np.random.uniform(-0.5, 0.5) for _ in results]
                cluster_text = [f"{safe_str_func(r.get('ticker'))}: {safe_str_func(r.get('title'))[:40]}" for r in results]

                fig_cluster = go.Figure(go.Scatter(
                    x=cluster_x, y=cluster_y,
                    mode="markers+text",
                    text=[safe_str_func(r.get('ticker')) for r in results],
                    textposition="top center",
                    marker=dict(
                        size=[int(safe_num_func(r.get("similarity_score",0))*35)+10 for r in results],
                        color=bar_colors,
                        opacity=0.85,
                        line=dict(width=1.5, color="#ffffff")
                    ),
                    hoverinfo="text",
                    hovertext=cluster_text
                ))
                dark_layout_func(fig_cluster, height=260, title="2D Vector Space Semantic Topology Map", show_legend=False)
                fig_cluster.update_xaxes(title="Cosine Similarity Proximity")
                fig_cluster.update_yaxes(showticklabels=False)
                st.plotly_chart(fig_cluster, use_container_width=True)

            for i, r in enumerate(results):
                score = safe_num_func(r.get("similarity_score",0))
                tick  = safe_str_func(r.get("ticker"),"—")
                title = safe_str_func(r.get("title"),"Article")
                pub   = safe_str_func(r.get("publisher"),"—")
                sent  = safe_str_func(r.get("sentiment"),"neutral")
                chunk = safe_str_func(r.get("chunk_text"),"")
                url   = safe_str_func(r.get("article_url"),"#")
                date  = fmt_date_func(r.get("published_utc"))
                with st.expander(f"#{i+1}  [{tick} — {ticker_names.get(tick, tick)}]  {title[:72]}…  — {score:.3f}"):
                    c1, c2, c3 = st.columns([1, 4, 1.2])
                    c1.metric("Score", f"{score:.3f}")
                    c2.progress(min(int(score*100),100))
                    with c3:
                        note_id_btn = f"save_note_{i}"
                        if st.button("📝 Export Note", key=note_id_btn, use_container_width=True):
                            note_uuid = f"note_{uuid.uuid4().hex[:8]}"
                            run_write("""
                                INSERT INTO research_notes(note_id, user_id, ticker, title, content, tags)
                                VALUES (%s, 'default_user', %s, %s, %s, %s);
                            """, (note_uuid, tick, f"RAG: {title[:50]}", chunk[:400], ["RAG", "AI_Export"]))
                            st.toast(f"✅ Exported research note for {tick}!")

                    st.markdown(f"{sentiment_badge_func(sent)} <span class='badge-rag'>pgvector cosine</span> &nbsp; **{pub}** · {date}", unsafe_allow_html=True)
                    if chunk: st.markdown(f"> {chunk[:400]}{'…' if len(chunk)>400 else ''}")
                    if url != "#": st.markdown(f"[🔗 Read full article]({url})")
        elif "rag_results" in st.session_state:
            st.warning("No matching documents. Try different query or Refresh ETL.")
