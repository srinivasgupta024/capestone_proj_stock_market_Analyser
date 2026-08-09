"""
CSS Design System & Terminal Styling Module.
Provides dark glassmorphism, animated pulse loaders, topnav positioning, custom scrollbars, and high-density metric styles.
"""

import streamlit as st

def inject_terminal_styles():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

      /* FORCE DARK ENGINE */
      html, body { background:#0C0E16!important; color:#E8EDFF!important; }
      .stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],
      [data-testid="stToolbar"] {
        background:#0C0E16!important;
        font-family:'Inter',sans-serif!important;
      }
      [data-testid="stHeader"],[data-testid="stDecoration"] { display:none!important; }

      /* TOP PADDING TO PREVENT FIXED NAVBAR OVERLAP */
      [data-testid="block-container"] {
        padding-top: 76px !important;
        padding-bottom: 24px !important;
      }

      /* SIDEBAR - SLEEK INFORMATIONAL TERMINAL */
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

      /* PERMANENTLY FIXED STICKY TOP NAVBAR */
      .topnav {
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        left: 21rem !important;
        z-index: 99999 !important;
        background: rgba(10, 13, 26, 0.95) !important;
        backdrop-filter: blur(14px) !important;
        border-bottom: 1px solid rgba(99, 102, 241, 0.25) !important;
        padding: 10px 24px !important;
        height: 62px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
      }
      @media (max-width: 992px) {
        .topnav { left: 0 !important; }
      }

      .topnav-brand { font-size:1.20rem; font-weight:800; color:#E8EDFF; letter-spacing:-0.5px; }
      .topnav-sub   { font-size:0.70rem; color:#6B7280; margin-top:1px; }
      .topnav-right { display:flex; align-items:center; gap:14px; }
      .topnav-stat  { text-align:right; }
      .topnav-stat-val { font-size:1.02rem; font-weight:700; color:#E8EDFF; }
      .topnav-stat-lbl { font-size:0.66rem; color:#6B7280; text-transform:uppercase; letter-spacing:0.06em; }

      /* TABS AS NAV */
      .stTabs [data-baseweb="tab-list"] {
        background:rgba(255,255,255,0.02)!important;
        border-radius:12px; padding:4px; gap:4px;
        border:1px solid rgba(255,255,255,0.06);
      }
      .stTabs [data-baseweb="tab"] {
        border-radius:9px; padding:8px 18px;
        font-weight:600; font-size:0.85rem;
        color:#8892A4!important; background:transparent!important;
        border:none!important; transition:all 0.2s;
      }
      .stTabs [aria-selected="true"] {
        background:rgba(99,102,241,0.22)!important;
        color:#A5B4FC!important;
        box-shadow:0 2px 12px rgba(99,102,241,0.2);
      }

      /* HIGH-DENSITY COMPACT METRIC CARDS */
      [data-testid="stMetric"] {
        background:linear-gradient(145deg,rgba(25,28,52,0.95),rgba(15,18,36,0.95))!important;
        border:1px solid rgba(99,102,241,0.20)!important;
        border-radius:12px!important; padding:12px 14px!important;
        box-shadow:0 4px 16px rgba(0,0,0,0.4); transition:all 0.2s;
      }
      [data-testid="stMetric"]:hover {
        transform:translateY(-2px);
        border-color:rgba(99,102,241,0.45)!important;
      }
      [data-testid="stMetricLabel"]>div {
        font-size:0.68rem!important; color:#8892A4!important;
        text-transform:uppercase; letter-spacing:0.06em; font-weight:600;
      }
      [data-testid="stMetricValue"]>div {
        font-size:1.35rem!important; font-weight:800!important; color:#E8EDFF!important;
      }
      [data-testid="stMetricDelta"]>div { font-size:0.78rem!important; }

      /* BUTTONS */
      .stButton>button {
        border-radius:10px!important; font-weight:600!important;
        font-size:0.85rem!important; padding:8px 16px!important;
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

      /* DATAFRAME & DATA EDITOR DARK OVERRIDES */
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
      hr { border-color:rgba(255,255,255,0.07)!important; margin:16px 0!important; }

      /* BADGES */
      .badge-bullish { background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.35); padding:2px 8px; border-radius:16px; font-size:0.72rem; font-weight:700; display:inline-block; }
      .badge-bearish { background:rgba(239,68,68,0.15);  color:#F87171; border:1px solid rgba(239,68,68,0.35);  padding:2px 8px; border-radius:16px; font-size:0.72rem; font-weight:700; display:inline-block; }
      .badge-neutral { background:rgba(245,158,11,0.15); color:#FCD34D; border:1px solid rgba(245,158,11,0.35); padding:2px 8px; border-radius:16px; font-size:0.72rem; font-weight:700; display:inline-block; }
      .badge-action  { background:rgba(99,102,241,0.18); color:#A5B4FC; border:1px solid rgba(99,102,241,0.4);  padding:2px 10px; border-radius:16px; font-size:0.76rem; font-weight:700; display:inline-block; margin:2px 0; }
      .badge-rag     { background:rgba(14,165,233,0.15); color:#38BDF8; border:1px solid rgba(14,165,233,0.35); padding:2px 8px; border-radius:16px; font-size:0.72rem; font-weight:700; display:inline-block; }
      .badge-sess    { background:rgba(139,92,246,0.18); color:#C4B5FD; border:1px solid rgba(139,92,246,0.4);  padding:2px 10px; border-radius:16px; font-size:0.72rem; font-weight:700; display:inline-block; }

      /* COMPACT NEWS CARD */
      .news-card {
        background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
        border-radius:10px; padding:10px 12px; margin-bottom:8px; transition:border-color 0.2s;
      }
      .news-card:hover { border-color:rgba(99,102,241,0.35); }
      .news-title { font-size:0.85rem; font-weight:600; color:#E8EDFF; line-height:1.35; }
      .news-meta  { font-size:0.72rem; color:#8892A4; margin-top:4px; }

      /* TOOL ROW */
      .tool-row { padding:8px 12px; border-radius:8px; background:rgba(255,255,255,0.03);
        border-left:3px solid rgba(99,102,241,0.5); margin-bottom:6px;
        font-size:0.82rem; color:#C8D0E0; }

      /* SIDEBAR LABELS & STATUS DOTS */
      .sb-label { font-size:0.67rem; font-weight:700; letter-spacing:0.10em;
        text-transform:uppercase; color:#4B5568; margin:14px 0 6px 0; display:block; }
      .sb-status-row { display:flex; align-items:center; gap:8px; padding:6px 10px;
        border-radius:8px; background:rgba(255,255,255,0.025); margin-bottom:5px;
        font-size:0.82rem; color:#C8D0E0; }
      .dot-g { width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 6px #10B981; flex-shrink:0; }
      .dot-y { width:8px; height:8px; border-radius:50%; background:#F59E0B; box-shadow:0 0 6px #F59E0B; flex-shrink:0; }
      .dot-r { width:8px; height:8px; border-radius:50%; background:#EF4444; box-shadow:0 0 6px #EF4444; flex-shrink:0; }

      /* CUSTOM HTML TABLE */
      .health-table { width:100%; border-collapse:collapse; font-size:0.84rem; }
      .health-table th {
        background:rgba(99,102,241,0.12); color:#A5B4FC; padding:9px 12px;
        text-align:left; font-weight:700; font-size:0.72rem; text-transform:uppercase;
        letter-spacing:0.06em; border-bottom:1px solid rgba(99,102,241,0.2);
      }
      .health-table td {
        padding:9px 12px; border-bottom:1px solid rgba(255,255,255,0.05);
        color:#C8D0E0; vertical-align:middle;
      }
      .health-table tr:hover td { background:rgba(255,255,255,0.025); }
      .health-table tr:last-child td { border-bottom:none; }
      .ht-ok   { color:#34D399; font-weight:700; }
      .ht-warn { color:#FCD34D; font-weight:700; }
      .ht-err  { color:#F87171; font-weight:700; }
      .table-wrap {
        background:rgba(15,18,36,0.95); border:1px solid rgba(255,255,255,0.07);
        border-radius:12px; overflow:hidden; margin-bottom:14px;
      }

      /* CUSTOM PULSE ANIMATED LOADER */
      @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0); }
        100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
      }
      .custom-loader-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 14px; background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 20px;
        color: #A5B4FC; font-size: 0.78rem; font-weight: 600;
        animation: pulseGlow 1.8s infinite;
      }

      /* CUSTOM SCROLLBARS */
      ::-webkit-scrollbar { width: 6px; height: 6px; }
      ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 4px; }
      ::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.35); border-radius: 4px; }
      ::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.6); }
    </style>
    """, unsafe_allow_html=True)
