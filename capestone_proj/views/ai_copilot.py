"""
View Module: AI Copilot Chat Interface (Tab 4).
Session-based ReAct agent chat interface with fixed scroll container, quick command chips, tool call badges, and in-tab session reset button.
"""

import streamlit as st
from datetime import datetime

def render_ai_copilot(backend: dict, session_id: str, safe_str_func):
    _agent_ok = backend.get("agent_ok", False)

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
        st.markdown(f"<span class='badge-sess'>Session: {session_id}</span>", unsafe_allow_html=True)
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
        st.markdown("**Quick Commands:**")
        qc = st.columns(5)
        qp = None
        if qc[0].button("➕ Add NVDA@120",   use_container_width=True): qp="Add NVDA to my watchlist with target buy 120"
        if qc[1].button("🔍 AI News AAPL",    use_container_width=True): qp="Search news about Apple artificial intelligence"
        if qc[2].button("📊 Analyse TSLA",    use_container_width=True): qp="Generate a BUY analysis report for TSLA"
        if qc[3].button("📋 My Watchlist",    use_container_width=True): qp="Show my current portfolio watchlist"
        if qc[4].button("📈 NVDA Snapshot",   use_container_width=True): qp="What is the current NVDA stock price and fundamentals?"

        if qp:
            st.session_state["pending_prompt"] = qp

        st.markdown("---")

        chat_box = st.container(height=450)
        with chat_box:
            for msg in st.session_state.messages:
                role = msg["role"]
                with st.chat_message(role):
                    ts = msg.get("ts","")
                    if role == "user":
                        st.markdown(
                            f"<div style='font-size:0.70rem;color:#6B7280;margin-bottom:4px'>"
                            f"<span class='badge-sess' style='font-size:0.68rem'>You · {session_id}</span> · {ts}</div>",
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

        chat_val = st.chat_input(
            f"Ask AI Copilot… [Session {session_id}]",
            key="agent_chat_input"
        )
        
        user_input = chat_val or st.session_state.pop("pending_prompt", None)

        if user_input:
            ts_now = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "actions": [],
                "ts": ts_now,
            })
            with st.spinner("🤖 AI Copilot executing Chain-of-Thought reasoning & ReAct tools..."):
                try:
                    resp    = backend["agent"].run(user_input)
                    answer  = safe_str_func(resp.get("answer",""), "No response.")
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
