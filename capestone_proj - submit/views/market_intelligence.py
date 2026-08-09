"""
View Module: Market Intelligence (Tab 1).
Features Technical Analysis Suite (Bollinger Bands, RSI, MACD), Quantitative Stock Screener, 55/45 split, 45d candlestick, and right-hand scrollable news feed hub.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def compute_technical_indicators(df_hist):
    """Compute 20-day Bollinger Bands, 14-day RSI, and 12/26 MACD for quantitative analysis."""
    df = df_hist.copy()
    closes = df["close"]

    # 20-day Moving Average & Bollinger Bands
    df["MA20"] = closes.rolling(window=20, min_periods=1).mean()
    df["STD20"] = closes.rolling(window=20, min_periods=1).std().fillna(0)
    df["Upper_Band"] = df["MA20"] + (2 * df["STD20"])
    df["Lower_Band"] = df["MA20"] - (2 * df["STD20"])

    # 14-day Relative Strength Index (RSI)
    delta = closes.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss + 1e-6)
    df["RSI14"] = 100 - (100 / (1 + rs))

    # MACD (12-day EMA vs 26-day EMA) & 9-day Signal
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    return df

def render_market_intelligence(
    run_query, run_write, backend: dict,
    all_tickers: list, ticker_names: dict, get_ticker_label_func,
    safe_num_func, safe_str_func, fmt_date_func, sentiment_badge_func,
    dark_layout_func, simulate_history_func, default_tickers: list
):
    _client_ok = backend.get("client_ok", False)

    # ── High-density KPI Metric Bar
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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Selector & Quick Watchlist Action Row
    sel_col, action_col = st.columns([3, 1])

    with sel_col:
        selected = st.selectbox(
            "Select Stock / Asset",
            all_tickers,
            format_func=get_ticker_label_func,
            index=0, key="tab1_ticker",
            help="Select a ticker symbol to inspect price action, fundamentals, and news"
        )

    quote = {}
    if _client_ok:
        try: quote = backend["client"].get_ticker_quote(selected)
        except: pass

    close  = safe_num_func(quote.get("close_price",0))
    _open  = safe_num_func(quote.get("open_price",0))
    high   = safe_num_func(quote.get("high_price",0))
    low    = safe_num_func(quote.get("low_price",0))
    volume = int(safe_num_func(quote.get("volume",0)))
    chg    = close - _open
    chg_pct= (chg / _open * 100) if _open else 0

    with action_col:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        in_wl = run_query("SELECT 1 FROM watchlist_tickers WHERE watchlist_id='default_watchlist' AND ticker=%s;", (selected,))
        if in_wl:
            st.button(f"✅ In Watchlist ({selected})", disabled=True, use_container_width=True)
        else:
            with st.popover(f"⭐ Add {selected} to Watchlist", use_container_width=True):
                st.markdown(f"**Add {get_ticker_label_func(selected)}**")
                pop_buy = st.number_input("Target Buy Price ($)", value=round(close*0.95, 2) if close else 100.0, step=1.0)
                pop_sell = st.number_input("Target Sell Price ($)", value=round(close*1.15, 2) if close else 150.0, step=1.0)
                pop_notes = st.text_input("Thesis Note", value=f"Tracked via Market Intelligence main screen.")
                if st.button("Save to Portfolio", type="primary", use_container_width=True):
                    run_write("INSERT INTO companies(ticker,name) VALUES(%s,%s) ON CONFLICT DO NOTHING;", (selected, ticker_names.get(selected, f"{selected} Corp")))
                    run_write("""
                        INSERT INTO watchlist_tickers(watchlist_id,ticker,target_buy_price,target_sell_price,notes)
                        VALUES('default_watchlist',%s,%s,%s,%s)
                        ON CONFLICT(watchlist_id,ticker) DO UPDATE SET
                            target_buy_price=EXCLUDED.target_buy_price,
                            target_sell_price=EXCLUDED.target_sell_price,
                            notes=EXCLUDED.notes;
                    """, (selected, pop_buy, pop_sell, pop_notes))
                    st.toast(f"✅ Added {selected} to Watchlist!")
                    st.rerun()

    # ── COMPACT HIGH-DENSITY PRICE METRIC CARDS
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Close Price", f"${close:.2f}", f"{chg:+.2f} ({chg_pct:+.2f}%)")
    m2.metric("Open Price",  f"${_open:.2f}")
    m3.metric("Day High",    f"${high:.2f}")
    m4.metric("Day Low",     f"${low:.2f}")
    m5.metric("Volume",      f"{volume/1e6:.1f}M")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── REBALANCED TWO-COLUMN LAYOUT: Left = Charts (55%), Right = Profile + Scrollable News Hub (45%)
    cleft, cright = st.columns([55, 45])

    with cleft:
        # Technical Indicator Selector Toggle
        tech_mode = st.radio(
            "Chart Overlay",
            ["Candlestick + Volume", "Bollinger Bands", "RSI (14-day)", "MACD Indicator"],
            horizontal=True, key="tech_indicator_mode"
        )

        if close > 0:
            raw_hist = simulate_history_func(close, high, low, _open, days=45, seed=hash(selected)%9999)
            df_hist = pd.DataFrame(raw_hist)
            df_tech = compute_technical_indicators(df_hist)

            dates_h  = df_tech["date"]
            opens_h  = df_tech["open"]
            highs_h  = df_tech["high"]
            lows_h   = df_tech["low"]
            closes_h = df_tech["close"]
            vols_h   = df_tech["volume"]
            vc = ["#10B981" if c>=o else "#EF4444" for o,c in zip(opens_h,closes_h)]

            if tech_mode == "Bollinger Bands":
                fig_c = go.Figure()
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["Upper_Band"], name="Upper Band", line=dict(color="rgba(165,180,252,0.5)", dash="dash")))
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["MA20"], name="20d SMA", line=dict(color="#F59E0B", width=1.5)))
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["Lower_Band"], name="Lower Band", line=dict(color="rgba(165,180,252,0.5)", dash="dash"), fill="tonexty", fillcolor="rgba(99,102,241,0.06)"))
                fig_c.add_trace(go.Scatter(x=dates_h, y=closes_h, name="Close Price", line=dict(color="#10B981", width=2)))
                dark_layout_func(fig_c, height=350, title=f"{get_ticker_label_func(selected)} — Bollinger Bands (20, 2σ)")
                st.plotly_chart(fig_c, use_container_width=True)

            elif tech_mode == "RSI (14-day)":
                fig_c = go.Figure()
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["RSI14"], name="RSI (14)", line=dict(color="#A5B4FC", width=2)))
                fig_c.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="Overbought (70)")
                fig_c.add_hline(y=30, line_dash="dash", line_color="#10B981", annotation_text="Oversold (30)")
                dark_layout_func(fig_c, height=350, title=f"{get_ticker_label_func(selected)} — Relative Strength Index (RSI 14)")
                fig_c.update_yaxes(range=[0, 100])
                st.plotly_chart(fig_c, use_container_width=True)

            elif tech_mode == "MACD Indicator":
                fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.03)
                fig_c.add_trace(go.Scatter(x=dates_h, y=closes_h, name="Close Price", line=dict(color="#6366F1", width=1.5)), row=1, col=1)
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["MACD"], name="MACD", line=dict(color="#38BDF8", width=1.5)), row=2, col=1)
                fig_c.add_trace(go.Scatter(x=dates_h, y=df_tech["MACD_Signal"], name="Signal Line", line=dict(color="#F59E0B", width=1.5, dash="dot")), row=2, col=1)
                fig_c.add_trace(go.Bar(x=dates_h, y=df_tech["MACD_Hist"], name="Histogram", marker_color=["#10B981" if v>=0 else "#EF4444" for v in df_tech["MACD_Hist"]]), row=2, col=1)
                dark_layout_func(fig_c, height=350, title=f"{get_ticker_label_func(selected)} — Moving Average Convergence Divergence (MACD)")
                st.plotly_chart(fig_c, use_container_width=True)

            else:
                # Default Candlestick + Volume
                fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72,0.28], vertical_spacing=0.02)
                fig_c.add_trace(go.Candlestick(
                    x=dates_h, open=opens_h, high=highs_h, low=lows_h, close=closes_h,
                    name=selected,
                    increasing=dict(line=dict(color="#10B981"), fillcolor="rgba(16,185,129,0.7)"),
                    decreasing=dict(line=dict(color="#EF4444"), fillcolor="rgba(239,68,68,0.7)"),
                ), row=1, col=1)

                fig_c.add_trace(go.Scatter(
                    x=dates_h, y=df_tech["MA20"], name="20d MA",
                    line=dict(color="#F59E0B", width=1.5, dash="dot")
                ), row=1, col=1)

                fig_c.add_trace(go.Bar(
                    x=dates_h, y=vols_h, name="Volume",
                    marker_color=vc, opacity=0.55
                ), row=2, col=1)

                fig_c.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#E8EDFF", size=10),
                    title=dict(text=f"{get_ticker_label_func(selected)} — Price Action & Volume",
                               font=dict(size=12, color="#A5B4FC"), x=0),
                    margin=dict(l=6,r=6,t=30,b=6), height=350,
                    xaxis_rangeslider_visible=False,
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
                )
                fig_c.update_xaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="#4B5568", tickfont=dict(color="#4B5568",size=9))
                fig_c.update_yaxes(gridcolor="rgba(255,255,255,0.05)", linecolor="#4B5568", tickfont=dict(color="#4B5568",size=9))
                st.plotly_chart(fig_c, use_container_width=True)

        # STANDOUT FEATURE: QUANTITATIVE STOCK SCREENER MATRIX
        with st.expander("🔍 Quantitative Market Screener Matrix", expanded=False):
            st.markdown("Rank and filter all tracked stocks based on fundamental metrics and NLP sentiment:")
            screener_data = []
            for t in default_tickers:
                try:
                    q = backend["client"].get_ticker_quote(t)
                    c_rows = run_query("SELECT pe_ratio, market_cap, sector FROM companies WHERE ticker=%s;", (t,))
                    pe_v = safe_num_func(c_rows[0]["pe_ratio"]) if c_rows else 25.0
                    mcap_v = safe_num_func(c_rows[0]["market_cap"]) if c_rows else 1e11
                    sec_v = c_rows[0]["sector"] if c_rows else "Tech"
                    c_p = safe_num_func(q.get("close_price",0))
                    o_p = safe_num_func(q.get("open_price",0))
                    chg_v = ((c_p - o_p)/o_p*100) if o_p else 0
                    screener_data.append({
                        "Ticker": t,
                        "Company": ticker_names.get(t, t),
                        "Sector": sec_v,
                        "Close ($)": c_p,
                        "Change (%)": round(chg_v, 2),
                        "P/E Ratio": pe_v,
                        "Market Cap ($B)": round(mcap_v/1e9, 1),
                        "AI Rating": "BUY" if chg_v > 0 and pe_v < 45 else ("HOLD" if chg_v >= -1.0 else "SELL")
                    })
                except: pass

            if screener_data:
                df_scr = pd.DataFrame(screener_data)
                st.dataframe(df_scr, use_container_width=True, hide_index=True)

    with cright:
        # Company Profile Card
        st.markdown(f"#### {selected} — Company Profile")
        comp = run_query("SELECT * FROM companies WHERE ticker=%s;", (selected,))
        if comp:
            c = comp[0]
            mcap = safe_num_func(c.get("market_cap",0))
            pe   = safe_num_func(c.get("pe_ratio",0))
            st.markdown(f"**{safe_str_func(c.get('name', ticker_names.get(selected, selected)))}**")
            st.markdown(f"`{safe_str_func(c.get('sector'))}` · `{safe_str_func(c.get('industry'))}`")
            fa, fb = st.columns(2)
            fa.metric("Market Cap", f"${mcap/1e12:.2f}T" if mcap>1e11 else (f"${mcap/1e9:.1f}B" if mcap>0 else "N/A"))
            fb.metric("P/E Ratio",  f"{pe:.1f}x" if pe>0 else "N/A")
            desc = safe_str_func(c.get("description"), "")
            if desc:
                st.markdown(
                    f"<div style='font-size:0.78rem;color:#A0AEC0;background:rgba(255,255,255,0.03);"
                    f"border-radius:8px;padding:8px 10px;border:1px solid rgba(255,255,255,0.06);margin-top:6px;margin-bottom:12px'>"
                    f"{desc[:180]}{'...' if len(desc)>180 else ''}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("Company fundamentals loading…")

        # 📰 DEDICATED SCROLLABLE NEWS WINDOW
        st.markdown("#### 📰 Financial News Feed Hub")
        news_tab_selected, news_tab_wl, news_tab_global = st.tabs([
            f"🎯 {selected}", "⭐ Watchlist", "🌐 All Market"
        ])

        with news_tab_selected:
            news_box = st.container(height=360)
            with news_box:
                news_rows = run_query(
                    "SELECT ticker,title,publisher,published_utc,sentiment,article_url "
                    "FROM news_articles WHERE ticker=%s ORDER BY published_utc DESC LIMIT 15;",
                    (selected,)
                )
                if news_rows:
                    for n in news_rows:
                        badge = sentiment_badge_func(n.get("sentiment"))
                        date  = fmt_date_func(n.get("published_utc"))
                        url   = safe_str_func(n.get("article_url"), "#")
                        title = safe_str_func(n.get("title"), "Market Update")
                        pub   = safe_str_func(n.get("publisher"), "—")
                        link  = f'<a href="{url}" target="_blank" style="color:#6366F1">Read ↗</a>' if url != "#" else ""
                        st.markdown(
                            f"<div class='news-card'>"
                            f"<div class='news-title'>{badge}&nbsp; {title}</div>"
                            f"<div class='news-meta'>{pub} · {date} &nbsp; {link}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info(f"No news indexed for {selected}. Click **Refresh ETL** in sidebar.")

        with news_tab_wl:
            news_box_wl = st.container(height=360)
            with news_box_wl:
                wl_tickers_rows = run_query("SELECT ticker FROM watchlist_tickers WHERE watchlist_id='default_watchlist';")
                wl_ticks = [r["ticker"] for r in wl_tickers_rows] if wl_tickers_rows else []
                if wl_ticks:
                    format_placeholders = ",".join(["%s"] * len(wl_ticks))
                    news_wl_rows = run_query(
                        f"SELECT ticker,title,publisher,published_utc,sentiment,article_url "
                        f"FROM news_articles WHERE ticker IN ({format_placeholders}) ORDER BY published_utc DESC LIMIT 20;",
                        tuple(wl_ticks)
                    )
                    if news_wl_rows:
                        for n in news_wl_rows:
                            tick  = safe_str_func(n.get("ticker"))
                            badge = sentiment_badge_func(n.get("sentiment"))
                            date  = fmt_date_func(n.get("published_utc"))
                            url   = safe_str_func(n.get("article_url"), "#")
                            title = safe_str_func(n.get("title"), "Market Update")
                            pub   = safe_str_func(n.get("publisher"), "—")
                            link  = f'<a href="{url}" target="_blank" style="color:#6366F1">Read ↗</a>' if url != "#" else ""
                            st.markdown(
                                f"<div class='news-card'>"
                                f"<div class='news-title'><strong style='color:#A5B4FC'>[{tick}]</strong> {badge}&nbsp; {title}</div>"
                                f"<div class='news-meta'>{pub} · {date} &nbsp; {link}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No news found for watchlist tickers.")
                else:
                    st.info("Watchlist is currently empty.")

        with news_tab_global:
            news_box_g = st.container(height=360)
            with news_box_g:
                news_g_rows = run_query(
                    "SELECT ticker,title,publisher,published_utc,sentiment,article_url "
                    "FROM news_articles ORDER BY published_utc DESC LIMIT 25;"
                )
                if news_g_rows:
                    for n in news_g_rows:
                        tick  = safe_str_func(n.get("ticker"))
                        badge = sentiment_badge_func(n.get("sentiment"))
                        date  = fmt_date_func(n.get("published_utc"))
                        url   = safe_str_func(n.get("article_url"), "#")
                        title = safe_str_func(n.get("title"), "Market Update")
                        pub   = safe_str_func(n.get("publisher"), "—")
                        link  = f'<a href="{url}" target="_blank" style="color:#6366F1">Read ↗</a>' if url != "#" else ""
                        st.markdown(
                            f"<div class='news-card'>"
                            f"<div class='news-title'><strong style='color:#A5B4FC'>[{tick}]</strong> {badge}&nbsp; {title}</div>"
                            f"<div class='news-meta'>{pub} · {date} &nbsp; {link}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No global news articles available.")
