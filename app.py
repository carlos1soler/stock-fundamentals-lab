import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fundamentals.config import GROUPS, POORLY_SUITED_SECTORS, SCORECARD, SECTOR_OVERRIDES
from fundamentals.data import compute_ttm, extract_all, load_facts, load_market_data, load_tickers
from fundamentals.explanations import (EXPLANATIONS, QUESTIONS, QUIZ, STATEMENTS_LESSON,
                                       VALUATION_EXPLANATIONS)
from fundamentals.metrics import (build_df, cagr, fmt_value, generate_insights, latest_fy, scale,
                                  unit_label)
from fundamentals.scoring import (icon_from_points, overall, peer_points, threshold_scores,
                                  thresholds_for)

st.set_page_config(page_title="Stock Fundamentals Lab", page_icon="📊", layout="wide")

st.markdown("""
<style>
.hero {background: linear-gradient(120deg,#4F46E5 0%,#7C3AED 55%,#EC4899 100%); padding: 1.6rem 1.8rem;
       border-radius: 16px; color: #fff; margin-bottom: 1rem;}
.hero h1 {color:#fff; margin:0; font-size:2rem;} .hero p {margin:.3rem 0 0 0; opacity:.92;}
.card {border:1px solid rgba(128,128,128,.25); border-radius:12px; padding:.8rem 1rem; margin-bottom:.5rem;
       background: rgba(128,128,128,.06);}
.pill {display:inline-block; padding:.1rem .6rem; border-radius:999px; font-size:.8rem;
       background:rgba(79,70,229,.15); margin-right:.3rem;}
</style>
<div class="hero"><h1>📊 Stock Fundamentals Lab</h1>
<p>Compare companies with SEC filings and market prices, then <b>learn</b> what every number means and
<b>experiment</b> with DuPont and DCF tools.</p></div>
""", unsafe_allow_html=True)


# ---------- helpers ----------
def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except Exception:
        st.dataframe(df, use_container_width=True, **kw)


def show_chart(fig):
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), legend_title_text="")
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def show_explanation(metric, source=EXPLANATIONS):
    info = source.get(metric)
    if not info:
        return
    with st.expander(f"ℹ️ What does {info['title']} mean?"):
        st.write(info["what"])
        if info["formula"]:
            st.markdown(f"**Formula:** `{info['formula']}`")
        if info["read"]:
            st.info(f"**How to read it:** {info['read']}")
        if info["watch"]:
            st.warning(f"**Watch out:** {info['watch']}")
        st.caption("Always interpret alongside industry, business model, accounting policies and multi-year trend.")


def safe_div(n, d):
    if pd.isna(n) or pd.isna(d) or d <= 0:
        return np.nan
    return n / d


def fetch_all(tickers, user_agent):
    raw, errors, market = {}, [], {}
    try:
        ticker_map = load_tickers(user_agent)
    except Exception as exc:
        return raw, [f"Could not download the SEC ticker list: {exc}"], market
    progress = st.progress(0.0, text="Downloading SEC financials...")
    for n, ticker in enumerate(tickers, 1):
        progress.progress((n - 1) / len(tickers), text=f"Downloading {ticker}...")
        try:
            if ticker not in ticker_map:
                errors.append(f"{ticker}: ticker not found at SEC")
            else:
                facts = load_facts(ticker_map[ticker], user_agent)
                series = extract_all(facts)
                if build_df(series).empty:
                    errors.append(f"{ticker}: no annual income statement data found")
                else:
                    raw[ticker] = {"series": series, "ttm": compute_ttm(facts, series)}
        except Exception as exc:
            errors.append(f"{ticker}: SEC data error: {exc}")
        try:
            market[ticker] = load_market_data(ticker)
        except Exception as exc:
            market[ticker] = {"price": np.nan, "price_time": "Unavailable", "market_cap": np.nan,
                              "shares_outstanding": np.nan, "enterprise_value": np.nan, "long_name": ticker,
                              "sector": "Unknown", "industry": "Unknown", "yahoo_trailing_pe": np.nan}
            errors.append(f"{ticker}: Yahoo Finance data unavailable ({exc})")
    progress.empty()
    return raw, errors, market


# ---------- sidebar ----------
st.sidebar.header("🔑 SEC API identification")
user_name = st.sidebar.text_input("Your name or organization", placeholder="e.g. Jane Smith")
user_email = st.sidebar.text_input("Your email", placeholder="e.g. jane@example.com")
st.sidebar.caption("The SEC requires a descriptive User-Agent with contact information.")
st.sidebar.header("🏢 Companies")
tickers_raw = st.sidebar.text_input("Tickers, comma separated", "AAPL, MSFT")
tickers = list(dict.fromkeys(t.strip().upper() for t in tickers_raw.split(",") if t.strip()))
years = st.sidebar.slider("Fiscal years to show", 3, 15, 10)
include_leases = st.sidebar.checkbox("Include operating leases in debt", value=False,
    help="Adds lease liabilities to total debt. Matters for retailers, airlines and restaurants.")

if st.sidebar.button("📥 Download / refresh data", type="primary"):
    if not user_name.strip() or not user_email.strip():
        st.sidebar.error("Please enter your name and email for the SEC User-Agent.")
    elif not tickers:
        st.sidebar.error("Enter at least one ticker.")
    else:
        with st.spinner("Loading..."):
            raw, errors, market = fetch_all(tickers, f"{user_name.strip()} {user_email.strip().lower()}")
        st.session_state.update(raw=raw, errors=errors, market=market, loaded=tickers)

if "raw" not in st.session_state:
    st.info("👈 Enter your SEC contact details and tickers in the sidebar, then click **Download / refresh data**.")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="card"><b>📈 Compare</b><br>Interactive charts for 60+ metrics across companies.</div>', unsafe_allow_html=True)
    c2.markdown('<div class="card"><b>🧪 Lab</b><br>DuPont ROE explorer and a DCF playground with sliders.</div>', unsafe_allow_html=True)
    c3.markdown('<div class="card"><b>🎓 Learn</b><br>Plain-English guide, formulas, pitfalls and a quiz.</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state.get("loaded") != tickers:
    st.sidebar.warning("Ticker list changed. Click **Download / refresh data** to load it.")

raw, market_data = st.session_state["raw"], st.session_state.get("market", {})
for error in st.session_state.get("errors", []):
    st.warning(error)
if not raw:
    st.error("No company data was loaded. Check the tickers and try again.")
    st.stop()
data = {t: build_df(v["series"], include_leases) for t, v in raw.items()}

# ---------- market snapshot ----------
cols = st.columns(min(4, len(data)))
for i, ticker in enumerate(data):
    m = market_data.get(ticker, {})
    with cols[i % len(cols)]:
        price = m.get("price", np.nan)
        st.metric(m.get("long_name", ticker), f"${price:,.2f}" if pd.notna(price) else "Unavailable",
                  help=f"Quote date/source: {m.get('price_time', 'Unavailable')}")
        st.caption(f"{ticker} · {m.get('sector', '?')} · {m.get('price_time', '')}")

tabs = st.tabs(["📈 Compare", "🏁 Scorecard", "💰 Valuation", "🔍 Company detail", "🧪 Lab", "🎓 Learn", "💾 Export", "🧭 Methodology"])

# ---------- Compare ----------
with tabs[0]:
    c1, c2, c3 = st.columns([2, 1, 1])
    group = c1.selectbox("Metric category", list(GROUPS), index=list(GROUPS).index("Profitability"))
    chart_type = c2.radio("Chart type", ["Line", "Bar"], horizontal=True)
    base100 = c3.checkbox("Normalize to 100", help="Amount metrics only: first shared positive year = 100, to compare relative change instead of size.")
    selected = st.multiselect("Choose metrics", GROUPS[group], default=GROUPS[group][:3], key=f"metrics_{group}")
    if not selected:
        st.info("Choose at least one metric.")
    for metric in selected:
        st.subheader(f"{metric} · {unit_label(metric)}")
        show_explanation(metric)
        chart_df = pd.DataFrame({t: f[metric] for t, f in data.items()}).sort_index().tail(years)
        if chart_df.dropna(how="all").empty:
            st.warning("No company has data for this metric under the SEC tags searched.")
            continue
        plot_df = scale(chart_df, metric)
        if base100 and metric in ("Revenue", "Net income", "Diluted EPS", "Free cash flow", "EBITDA", "Operating income"):
            ok = plot_df.dropna()
            years_ok = ok.index[(ok > 0).all(axis=1)] if not ok.empty else []
            if len(years_ok):
                plot_df = plot_df / plot_df.loc[years_ok[0]] * 100
                st.caption(f"Indexed to 100 in fiscal year {years_ok[0]}.")
            else:
                st.info("Normalization needs a shared year with positive values for every company.")
        plot_df.index.name = "Fiscal year"
        long = plot_df.reset_index().melt(id_vars="Fiscal year", var_name="Company", value_name="Value")
        long["Fiscal year"] = long["Fiscal year"].astype(str)
        fig = (px.line(long, x="Fiscal year", y="Value", color="Company", markers=True) if chart_type == "Line"
               else px.bar(long, x="Fiscal year", y="Value", color="Company", barmode="group"))
        fig.update_layout(height=340, yaxis_title=unit_label(metric))
        show_chart(fig)
        show_df(chart_df.style.format(lambda v, m=metric: fmt_value(m, v)))

# ---------- Scorecard ----------
with tabs[1]:
    st.markdown("A quick **screening** tool, not a recommendation. Pick how companies are judged:")
    mode = st.radio("Scoring mode", ["Sector-aware thresholds", "Generic thresholds", "Peer ranking"], horizontal=True,
                    help="Sector-aware adjusts thresholds using the Yahoo sector. Peer ranking compares only the companies you loaded.")
    latest = pd.DataFrame({t: f.loc[latest_fy(f), list(SCORECARD)] for t, f in data.items()}).T
    peer_pts = peer_points(latest) if mode == "Peer ranking" else None
    if mode == "Peer ranking" and len(data) < 2:
        st.info("Peer ranking needs at least two companies.")
    results, rows = {}, []
    for t, f in data.items():
        sector = market_data.get(t, {}).get("sector", "Unknown")
        if mode == "Peer ranking":
            res = {m: (latest.loc[t, m], icon_from_points(peer_pts.loc[t, m]), peer_pts.loc[t, m]) for m in SCORECARD}
        else:
            res = threshold_scores(f.loc[latest_fy(f)], sector, mode.startswith("Sector"))
        results[t] = res
        row = {"Company": t, "Sector": sector, "Fiscal year": int(latest_fy(f))}
        for m, (v, icon, _) in res.items():
            row[m] = f"{icon} {fmt_value(m, v)}" if icon else "—"
        score = overall([p for _, _, p in res.values()])
        row["Screening score"] = f"{score:.0f}/100" if pd.notna(score) else "—"
        rows.append(row)
        if sector in POORLY_SUITED_SECTORS:
            st.warning(f"{t} is in **{sector}**: margins, liquidity and leverage ratios are not comparable to industrial companies.")
    show_df(pd.DataFrame(rows).set_index("Company"))
    radar = go.Figure()
    for t, res in results.items():
        r = [0 if pd.isna(p) else p for _, _, p in res.values()]
        radar.add_trace(go.Scatterpolar(r=r + r[:1], theta=list(res) + [list(res)[0]], fill="toself", name=t, opacity=.55))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=520, title="Strengths radar (100 = green, missing = 0)")
    show_chart(radar)
    with st.expander("See the thresholds used"):
        t_pick = st.selectbox("Company", list(data), key="th_company")
        th = thresholds_for(market_data.get(t_pick, {}).get("sector"), mode.startswith("Sector"))
        show_df(pd.DataFrame([{"Metric": m, "Better when": "higher" if h else "lower", "🟢 green at": g, "🟡 yellow at": o}
                              for m, (h, g, o) in th.items()]).set_index("Metric"))
        st.caption("Sectors with custom thresholds: " + ", ".join(SECTOR_OVERRIDES) + ". Others use generic values.")
    st.subheader(f"Growth over the last {years} years (CAGR)")
    crow = []
    for t, f in data.items():
        w = f.tail(years)
        crow.append({"Company": t, **{f"{m} CAGR": (f"{cagr(w[m]):.1f}%" if cagr(w[m]) is not None else "—")
                                      for m in ("Revenue", "EBITDA", "Net income", "Diluted EPS", "Free cash flow")}})
    show_df(pd.DataFrame(crow).set_index("Company"))
    st.caption("CAGR (compound annual growth rate) is shown only when first and last values are positive.")

# ---------- Valuation ----------
with tabs[2]:
    basis_choice = st.radio("Financial basis", ["TTM (latest 10-Qs)", "Last fiscal year"], horizontal=True,
                            help="TTM = last fiscal year + latest year-to-date − same period a year ago.")
    st.warning("Multiples are estimates, not recommendations. Price, market cap and SEC data can have different dates.")
    rows = []
    for t, f in data.items():
        m, fy = market_data.get(t, {}), latest_fy(data[t])
        x = f.loc[fy]
        ttm = raw[t]["ttm"]
        use_ttm = basis_choice.startswith("TTM")
        val = lambda k: ttm["values"].get(k, x.get(k, np.nan)) if use_ttm else x.get(k, np.nan)
        price, shares = m.get("price", np.nan), m.get("shares_outstanding", np.nan)
        cap = m.get("market_cap", np.nan)
        if pd.isna(cap) and pd.notna(price) and pd.notna(shares):
            cap = price * shares
        ev = m.get("enterprise_value", np.nan)
        if pd.isna(ev) and pd.notna(cap) and pd.notna(x.get("Net debt")):
            ev = cap + x["Net debt"]
        fcf, div = val("Free cash flow"), val("Dividends paid")
        rows.append({
            "Company": t, "Basis": ttm["basis"] if use_ttm else f"FY{fy}", "Price": price,
            "Market cap ($B)": cap / 1e9 if pd.notna(cap) else np.nan, "EV ($B)": ev / 1e9 if pd.notna(ev) else np.nan,
            "P/E (price / EPS)": safe_div(price, val("Diluted EPS")), "P/E (Yahoo trailing)": m.get("yahoo_trailing_pe", np.nan),
            "EV / EBITDA": safe_div(ev, val("EBITDA")), "EV / Revenue": safe_div(ev, val("Revenue")),
            "P/S": safe_div(cap, val("Revenue")), "P/B": safe_div(cap, x.get("Equity")), "P/FCF": safe_div(cap, fcf),
            "FCF yield %": fcf / cap * 100 if pd.notna(cap) and pd.notna(fcf) and cap > 0 else np.nan,
            "Dividend yield %": abs(div) / cap * 100 if pd.notna(cap) and pd.notna(div) and cap > 0 else np.nan,
        })
    vdf = pd.DataFrame(rows).set_index("Company")
    fmt = {c: "{:,.2f}x" for c in ["P/E (price / EPS)", "P/E (Yahoo trailing)", "EV / EBITDA", "EV / Revenue", "P/S", "P/B", "P/FCF"]}
    fmt.update({"Price": "${:,.2f}", "Market cap ($B)": "{:,.1f}", "EV ($B)": "{:,.1f}", "FCF yield %": "{:,.2f}%", "Dividend yield %": "{:,.2f}%"})
    show_df(vdf.style.format(fmt, na_rep="—"))
    st.caption("The 'Yahoo trailing' P/E is shown as a cross-check; differences usually come from timing or one-off items.")
    vm = st.selectbox("Explain and chart a multiple", list(VALUATION_EXPLANATIONS))
    show_explanation(vm, VALUATION_EXPLANATIONS)
    if vm in vdf and vdf[vm].notna().any():
        show_chart(px.bar(vdf.reset_index(), x="Company", y=vm, color="Company", text_auto=".2f"))

# ---------- Company detail ----------
with tabs[3]:
    t = st.selectbox("Choose a company", list(data), key="detail_ticker")
    frame, fy, m = data[t].tail(years), latest_fy(data[t]), market_data.get(t, {})
    st.subheader(m.get("long_name", t))
    st.markdown(f'<span class="pill">{m.get("sector", "?")}</span><span class="pill">{m.get("industry", "?")}</span>', unsafe_allow_html=True)
    k = st.columns(4)
    k[0].metric("Share price", f"${m['price']:,.2f}" if pd.notna(m.get("price", np.nan)) else "Unavailable")
    k[1].metric("Latest fiscal year", str(fy), help=f"Period ended {data[t].loc[fy, 'Period end']:%Y-%m-%d}" if pd.notna(data[t].loc[fy, "Period end"]) else None)
    k[2].metric("Revenue ($M)", fmt_value("Revenue", data[t].loc[fy, "Revenue"]))
    k[3].metric("Net income ($M)", fmt_value("Net income", data[t].loc[fy, "Net income"]))
    st.subheader("💡 Auto-generated insights")
    insights = generate_insights(data[t].loc[fy])
    if insights:
        for icon, head, text in insights:
            st.markdown(f"{icon} **{head}**: {text}")
    else:
        st.write("Not enough data to generate insights.")
    st.caption("Rule-based descriptions of historical results, not a forecast or recommendation.")
    trend = scale(frame[["Revenue", "Net income", "Free cash flow"]], "Revenue").rename_axis("Fiscal year").reset_index()
    show_chart(px.line(trend.melt(id_vars="Fiscal year", var_name="Metric", value_name="USD millions"),
                       x="Fiscal year", y="USD millions", color="Metric", markers=True, title="Revenue, net income and FCF"))
    dg = st.selectbox("Financial category", list(GROUPS), key="detail_group")
    for metric in GROUPS[dg]:
        show_explanation(metric)
    table = pd.DataFrame({mt: frame[mt].map(lambda v, mm=mt: fmt_value(mm, v)) for mt in GROUPS[dg]}).T
    table.columns = [str(c) for c in table.columns]
    show_df(table)

# ---------- Lab ----------
with tabs[4]:
    st.markdown("### 🧪 Experiments\nChange the assumptions and watch the outputs move. This is how analysts build intuition.")
    lab = st.radio("Tool", ["DuPont ROE explorer", "DCF playground"], horizontal=True)
    t = st.selectbox("Company", list(data), key="lab_company")
    f = data[t]
    if lab == "DuPont ROE explorer":
        st.markdown("**ROE = Net margin × Asset turnover × Equity multiplier.** It splits return on equity into *profitability*, *efficiency* and *leverage*.")
        d = f[["Net margin %", "Asset turnover", "Equity multiplier", "ROE %"]].dropna().tail(years)
        if d.empty:
            st.info("Not enough data for a DuPont breakdown.")
        else:
            show_df(d.style.format("{:,.2f}"))
            base = d.iloc[-1]
            st.markdown(f"**What-if** starting from {t}'s latest values (FY{d.index[-1]}):")
            c = st.columns(3)
            nm = c[0].slider("Net margin %", -5.0, 60.0, float(base["Net margin %"]), 0.5)
            at = c[1].slider("Asset turnover", 0.1, 3.0, float(base["Asset turnover"]), 0.05)
            em = c[2].slider("Equity multiplier", 1.0, 10.0, float(base["Equity multiplier"]), 0.1)
            roe = nm * at * em / 1.0
            st.metric("Resulting ROE %", f"{roe:,.1f}%", delta=f"{roe - base['ROE %']:+.1f} pts vs actual")
            st.info("Try doubling the equity multiplier: ROE jumps without any improvement in the business. That is why high ROE from leverage is riskier than high ROE from margins.")
    else:
        st.markdown("A 10-year, two-stage **discounted cash flow**. It values a company as the present value of its future free cash flow. "
                    "The output is only as good as the assumptions, so treat it as a thinking tool, not a price target.")
        fy = latest_fy(f)
        ttm_fcf = raw[t]["ttm"]["values"].get("Free cash flow", f.loc[fy, "Free cash flow"])
        m = market_data.get(t, {})
        shares0 = m.get("shares_outstanding", np.nan)
        if pd.isna(shares0):
            shares0 = f.loc[fy, "Diluted shares"]
        c = st.columns(3)
        fcf0 = c[0].number_input("Starting FCF ($M)", value=float(ttm_fcf / 1e6) if pd.notna(ttm_fcf) else 1000.0)
        nd0 = f.loc[fy, "Net debt"]
        net_debt = c[1].number_input("Net debt ($M, negative = net cash)", value=float(nd0 / 1e6) if pd.notna(nd0) else 0.0)
        shares = c[2].number_input("Shares (millions)", value=float(shares0 / 1e6) if pd.notna(shares0) else 1000.0, min_value=0.001)
        s = st.columns(4)
        g1 = s[0].slider("FCF growth yrs 1-5 (%)", -10.0, 40.0, 8.0, 0.5)
        g2 = s[1].slider("FCF growth yrs 6-10 (%)", -5.0, 25.0, 5.0, 0.5)
        tg = s[2].slider("Terminal growth (%)", 0.0, 4.0, 2.5, 0.1)
        r = s[3].slider("Discount rate (%)", 5.0, 15.0, 9.0, 0.5)

        def dcf(g1, g2, tg, r):
            if r <= tg:
                return np.nan, np.nan
            f_, pv = fcf0, 0.0
            for yr in range(1, 11):
                f_ *= 1 + (g1 if yr <= 5 else g2) / 100
                pv += f_ / (1 + r / 100) ** yr
            tv_pv = f_ * (1 + tg / 100) / ((r - tg) / 100) / (1 + r / 100) ** 10
            return (pv + tv_pv - net_debt) / shares, tv_pv / (pv + tv_pv)

        if fcf0 <= 0:
            st.warning("Starting FCF is zero or negative, so a simple DCF is not meaningful.")
        value, tv_share = dcf(g1, g2, tg, r)
        price = m.get("price", np.nan)
        k = st.columns(3)
        k[0].metric("Model value per share", f"${value:,.2f}" if pd.notna(value) else "n/a")
        k[1].metric("Market price", f"${price:,.2f}" if pd.notna(price) else "n/a",
                    delta=f"{(value / price - 1) * 100:+.0f}% model vs price" if pd.notna(value) and pd.notna(price) and price > 0 else None)
        k[2].metric("Share of value from terminal", f"{tv_share * 100:.0f}%" if pd.notna(tv_share) else "n/a",
                    help="High values mean the answer depends mostly on the far future.")
        grid = pd.DataFrame({f"g={tgv:.1f}%": [dcf(g1, g2, tgv, rv)[0] for rv in np.arange(r - 2, r + 2.1, 1.0)]
                             for tgv in np.arange(max(tg - 1, 0), tg + 1.1, 0.5)},
                            index=[f"r={rv:.1f}%" for rv in np.arange(r - 2, r + 2.1, 1.0)])
        st.markdown("**Sensitivity**: value per share for different discount rates (rows) and terminal growth (columns).")
        show_df(grid.style.format("${:,.2f}", na_rep="n/a"))
        st.info("Notice how a 1-point change in the discount rate moves the value far more than most operating improvements. "
                "Not financial advice.")

# ---------- Learn ----------
with tabs[5]:
    st.markdown("### 🎓 Learn financial statement analysis")
    l1, l2, l3, l4 = st.tabs(["Start here", "Metric encyclopedia", "Questions to ask", "Quiz"])
    with l1:
        st.markdown(STATEMENTS_LESSON)
        st.markdown("**A simple workflow:** growth → profitability → cash quality → balance-sheet safety → returns on capital → valuation. "
                    "Do this across several years and against peers in the same industry.")
    with l2:
        cat = st.selectbox("Category", list(GROUPS) + ["Valuation multiples"], key="enc_cat")
        names = list(VALUATION_EXPLANATIONS) if cat == "Valuation multiples" else GROUPS[cat]
        src = VALUATION_EXPLANATIONS if cat == "Valuation multiples" else EXPLANATIONS
        name = st.selectbox("Metric", names, key="enc_metric")
        info = src[name]
        st.header(info["title"])
        st.write(info["what"])
        if info["formula"]:
            st.code(info["formula"], language=None)
        if info["read"]:
            st.info(f"**How to read it:** {info['read']}")
        if info["watch"]:
            st.warning(f"**Watch out:** {info['watch']}")
    with l3:
        st.markdown("Good analysis starts with questions, not ratios.")
        show_df(pd.DataFrame(QUESTIONS, columns=["Question", "Metrics that help", "Where in this app"]).set_index("Question"))
    with l4:
        with st.form("quiz"):
            answers = [st.radio(f"**{i + 1}. {q['q']}**", q["options"], index=None, key=f"quiz_{i}") for i, q in enumerate(QUIZ)]
            submitted = st.form_submit_button("Check answers")
        if submitted:
            score = 0
            for i, (q, a) in enumerate(zip(QUIZ, answers)):
                ok = a == q["options"][q["answer"]]
                score += ok
                (st.success if ok else st.error)(f"Q{i + 1}: {'Correct' if ok else 'Not quite'}. {q['why']}")
            st.metric("Score", f"{score}/{len(QUIZ)}")

# ---------- Export ----------
with tabs[6]:
    long_df = pd.concat(data, names=["Ticker", "Fiscal year"]).reset_index()
    st.markdown("Full annual dataset in raw units (USD, not millions).")
    show_df(long_df, height=400)
    st.download_button("⬇️ Download fundamentals CSV", long_df.to_csv(index=False).encode("utf-8"), "fundamentals.csv", "text/csv")
    ttm_export = pd.DataFrame({t: {**v["ttm"]["values"], "basis": v["ttm"]["basis"]} for t, v in raw.items()}).T
    st.download_button("⬇️ Download TTM CSV", ttm_export.to_csv().encode("utf-8"), "ttm.csv", "text/csv")
    mk = pd.DataFrame([{"Ticker": t, **market_data.get(t, {})} for t in data])
    st.download_button("⬇️ Download market snapshot CSV", mk.to_csv(index=False).encode("utf-8"), "market_snapshot.csv", "text/csv")

# ---------- Methodology ----------
with tabs[7]:
    st.markdown("""
### Data sources
- **SEC EDGAR Company Facts:** annual figures from 10-K / 10-K/A, TTM from 10-Q filings. Cached 24 h.
- **Yahoo Finance (`yfinance`):** latest daily close and market metadata. Cached 15 min, not guaranteed real-time.

### Calculation notes
- **Fiscal year label:** period end minus 25 days, then the year. 52/53-week years ending in the first days of January stay in the prior fiscal year; other year-ends keep their calendar year (Jan 26, 2025 = FY2025). The "Period end" column shows the real date.
- **TTM** = last fiscal year + current year-to-date − same year-to-date a year earlier. Items without usable 10-Q data fall back to the last fiscal year.
- **Total debt** = non-current + current debt (or the all-in `LongTermDebt` tag) + commercial paper; operating leases are optional via the sidebar.
- **Materiality guard:** ratios with denominators under $1M, or negative equity / EBITDA where the ratio is meaningless, show "—".
- **ROIC** is simplified: NOPAT ÷ average (identified debt + equity), with a 21% tax fallback.
- **Scoring:** generic thresholds, sector-aware thresholds (Yahoo sector), or percentile rank among loaded companies.

### Limitations
- Balance-sheet items in valuation (net debt, equity) come from the last fiscal year-end, not the latest quarter.
- Market cap and share counts are current; EPS and cash flows are historical.
- Debt and revenue depend on the XBRL tags searched and may omit categories.
- Banks, insurers and REITs have different economics; most ratios here are not comparable for them.
- Educational tool, not investment advice.
""")