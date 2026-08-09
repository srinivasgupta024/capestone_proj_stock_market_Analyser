"""
View Module: Market Intelligence (Tab 1).
Renders high-density metric bar, 55/45 split layout, 45-day candlestick chart, intraday change bar chart, company profile card, and right-hand scrollable news feed hub.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # ── REBALANCED TWO-COLUMN LAYOUT: Left = Charts (55%), Right = Company Profile + SCROLLABLE NEWS HUB (45%)
    cleft, cright = st.columns([55, 45])

    with cleft:
        # Candlestick & Volume Chart
        if close > 0:
            hist = simulate_history_func(close, high, low, _open, days=45, seed=hash(selected)%9999)
            fig_c = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   row_heights=[0.72,0.28], vertical_spacing=0.02)
            dates_h  = [h["date"]   for h in hist]
            opens_h  = [h["open"]   for h in hist]
            highs_h  = [h["high"]   for h in hist]
            lows_h   = [h["low"]    for h in hist]
            closes_h = [h["close"]  for h in hist]
            vols_h   = [h["volume"] for h in hist]
            vc = ["#10B981" if c>=o else "#EF4444" for o,c in zip(opens_h,closes_h)]

            fig_c.add_trace(go.Candlestick(
                x=dates_h, open=opens_h, high=highs_h, low=lows_h, close=closes_h,
                name=selected,
                increasing=dict(line=dict(color="#10B981"), fillcolor="rgba(16,185,129,0.7)"),
                decreasing=dict(line=dict(color="#EF4444"), fillcolor="rgba(239,68,68,0.7)"),
            ), row=1, col=1)

            w = 10
            ma = [sum(closes_h[max(0,i-w+1):i+1])/len(closes_h[max(0,i-w+1):i+1]) for i in range(len(closes_h))]
            fig_c.add_trace(go.Scatter(
                x=dates_h, y=ma, name="10d MA",
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

        # Intraday Change Market Overview Bar Chart
        if _client_ok:
            all_q = []
            for t in default_tickers:
                try:
                    q = backend["client"].get_ticker_quote(t)
                    all_q.append({
                        "Ticker": t,
                        "Close":  safe_num_func(q.get("close_price",0)),
                        "Open":   safe_num_func(q.get("open_price",0)),
                    })
                except: pass

            if all_q:
                df_all = pd.DataFrame(all_q)
                df_all["Δ%"]    = ((df_all["Close"]-df_all["Open"])/df_all["Open"]*100).round(2)
                df_all["Color"] = df_all["Δ%"].apply(lambda x: "#10B981" if x>=0 else "#EF4444")

                fig_d = go.Figure(go.Bar(
                    x=df_all["Ticker"], y=df_all["Δ%"],
                    marker_color=df_all["Color"].tolist(), opacity=0.88,
                    text=[f"{v:+.2f}%" for v in df_all["Δ%"]],
                    textposition="outside",
                    textfont=dict(color="#E8EDFF", size=10),
                ))
                dark_layout_func(fig_d, height=220, title="Market Overview — Intraday % Change", show_legend=False)
                fig_d.update_layout(yaxis_title="% Change")
                fig_d.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)")
                st.plotly_chart(fig_d, use_container_width=True)

    with cright:
        # Company Profile Card
        st.markdown(f"#### {selected} — Company Profile")
        comp = run_query("SELECT * FROM companies WHERE ticker=%s;", (selected,))
        if comp:
            c = comp[0]
            mcap = safe_num_func(c.get("market_cap",0))
            pe   = safe_num_func(c.get("pe_ratio",0))
            divy = safe_num_func(c.get("dividend_yield",0))
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
