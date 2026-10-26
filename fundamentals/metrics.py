"""Metric calculations. Pure pandas/numpy so they can be unit-tested without Streamlit or network access."""
import numpy as np
import pandas as pd

from .config import FMT, SOURCE


def to_fiscal_year(series):
    """Label a period-end date with a fiscal year: shift back 25 days, take the year.
    This keeps 52/53-week years that end in the first days of January (e.g. Jan 3, 2025) in fiscal 2024, while
    year-ends such as Dec 31 or Jan 26 keep the calendar year in which they fall (NVIDIA's Jan 26, 2025 = FY2025)."""
    if series.empty:
        return pd.Series(dtype=float, index=pd.Index([], dtype="int64"))
    series = series.sort_index()
    years = (series.index - pd.Timedelta(days=25)).year
    out = pd.Series(series.values, index=years)
    return out[~out.index.duplicated(keep="last")]


def ratio(a, b, min_abs=1e6):
    """a / b, but 'not meaningful' (NaN) when the denominator is under min_abs (default $1M)."""
    return a / b.where(b.abs() >= min_abs)


def average(series):
    return series.rolling(2, min_periods=2).mean()


def growth(series):
    prev = series.shift(1)
    return (series - prev) / prev.where(prev > 0) * 100  # no growth % off a zero/negative base


def cagr(series):
    series = series.dropna()
    if len(series) < 2 or series.iloc[0] <= 0 or series.iloc[-1] <= 0:
        return None
    n = series.index[-1] - series.index[0]
    return ((series.iloc[-1] / series.iloc[0]) ** (1 / n) - 1) * 100 if n > 0 else None


def build_df(series, include_leases=False):
    """series: {SOURCE name: Series indexed by period-end date}. Returns a fiscal-year DataFrame of all metrics."""
    anchors = [series[k].index for k in ("Net income", "Revenue", "Operating income") if not series[k].empty]
    if not anchors:
        return pd.DataFrame()
    fiscal_ends = pd.DatetimeIndex([])
    for anchor in anchors:
        fiscal_ends = fiscal_ends.union(anchor)

    cols = {}
    for name, (kind, _, _, _) in SOURCE.items():
        s = series[name]
        if kind == "instant":
            s = s[s.index.isin(fiscal_ends)]
        cols[name] = to_fiscal_year(s)
    d = pd.DataFrame(cols).sort_index()
    d = d.reindex(range(int(d.index.min()), int(d.index.max()) + 1))
    d.insert(0, "Period end", to_fiscal_year(pd.Series(fiscal_ends, index=fiscal_ends)).reindex(d.index))

    d["Gross profit"] = d["Gross profit"].fillna(d["Revenue"] - d["Cost of revenue"])
    d["EBITDA"] = d["Operating income"] + d["D&A"]
    d["Cash & investments"] = d[["Cash", "Short-term investments"]].sum(axis=1, min_count=1)

    # Debt: non-current + current if reported, else the all-in "LongTermDebt" tag; plus commercial paper.
    core = d["Long-term debt"].add(d["Current debt"], fill_value=0)
    core = core.where(d["Long-term debt"].notna() | d["Current debt"].notna()).fillna(d["Long-term debt (total)"])
    debt = core.add(d["Commercial paper"], fill_value=0).where(core.notna() | d["Commercial paper"].notna())
    d["Lease liabilities"] = d[["Operating lease (current)", "Operating lease (non-current)"]].sum(axis=1, min_count=1)
    if include_leases:
        debt = debt.add(d["Lease liabilities"], fill_value=0).where(debt.notna() | d["Lease liabilities"].notna())
    d["Total debt"] = debt  # missing stays unknown (NaN), never silently zero
    d["Net debt"] = d["Total debt"] - d["Cash & investments"]
    d["Total liabilities"] = d["Total liabilities"].fillna(d["Total assets"] - d["Equity"])
    capex = d["CapEx"].abs()
    d["Free cash flow"] = d["Operating cash flow"] - capex

    d["Gross margin %"] = ratio(d["Gross profit"], d["Revenue"]) * 100
    d["Operating margin %"] = ratio(d["Operating income"], d["Revenue"]) * 100
    d["EBITDA margin %"] = ratio(d["EBITDA"], d["Revenue"]) * 100
    d["Net margin %"] = ratio(d["Net income"], d["Revenue"]) * 100
    d["ROE %"] = ratio(d["Net income"], average(d["Equity"])) * 100
    d["ROA %"] = ratio(d["Net income"], average(d["Total assets"])) * 100
    tax_rate = ratio(d["Income tax"], d["Pretax income"]).clip(0, 0.4).fillna(0.21)
    nopat = d["Operating income"] * (1 - tax_rate)
    d["ROIC %"] = ratio(nopat, average(d["Total debt"] + d["Equity"])) * 100

    d["Current ratio"] = ratio(d["Current assets"], d["Current liabilities"])
    quick_assets = d[["Cash", "Short-term investments", "Accounts receivable"]].sum(axis=1, min_count=1)
    d["Quick ratio"] = ratio(quick_assets, d["Current liabilities"])
    d["Debt / Equity"] = ratio(d["Total debt"], d["Equity"].where(d["Equity"] > 0))
    d["Debt / Assets"] = ratio(d["Total debt"], d["Total assets"])
    d["Net debt / EBITDA"] = ratio(d["Net debt"], d["EBITDA"].where(d["EBITDA"] > 0))
    d["Interest coverage"] = ratio(d["Operating income"], d["Interest expense"].abs())
    d["Equity multiplier"] = ratio(average(d["Total assets"]), average(d["Equity"]).where(average(d["Equity"]) > 0))
    d["Asset turnover"] = ratio(d["Revenue"], average(d["Total assets"]))
    d["Inventory turnover"] = ratio(d["Cost of revenue"], average(d["Inventory"]))
    d["DSO (days)"] = ratio(d["Accounts receivable"], d["Revenue"]) * 365
    d["DIO (days)"] = ratio(d["Inventory"], d["Cost of revenue"]) * 365
    d["DPO (days)"] = ratio(d["Accounts payable"], d["Cost of revenue"]) * 365
    d["Cash conversion cycle (days)"] = d["DSO (days)"] + d["DIO (days)"].fillna(0) - d["DPO (days)"]
    d["FCF margin %"] = ratio(d["Free cash flow"], d["Revenue"]) * 100
    d["OCF / Net income"] = ratio(d["Operating cash flow"], d["Net income"].where(d["Net income"] > 0))
    d["CapEx / Revenue %"] = ratio(capex, d["Revenue"]) * 100
    d["Dividend payout %"] = ratio(d["Dividends paid"].abs(), d["Net income"].where(d["Net income"] > 0)) * 100
    returned = pd.concat([d["Dividends paid"], d["Share buybacks"]], axis=1).abs().sum(axis=1, min_count=1)
    d["Shareholder payout % of FCF"] = ratio(returned, d["Free cash flow"].where(d["Free cash flow"] > 0)) * 100
    for metric, source in [("Revenue growth %", "Revenue"), ("EBITDA growth %", "EBITDA"),
                           ("Net income growth %", "Net income"), ("EPS growth %", "Diluted EPS"),
                           ("FCF growth %", "Free cash flow")]:
        d[metric] = growth(d[source])
    numeric = d.select_dtypes("number")
    d[numeric.columns] = numeric.replace([np.inf, -np.inf], np.nan)
    return d


# ---------- formatting helpers ----------
def fmt_value(metric, value):
    if pd.isna(value) or not np.isfinite(value):
        return "—"
    kind = FMT.get(metric, "x")
    if kind in ("usd", "shares"):
        return f"{value / 1e6:,.1f}"
    if kind == "eps":
        return f"${value:,.2f}"
    if kind == "pct":
        return f"{value:,.1f}%"
    if kind == "x":
        return f"{value:,.2f}x"
    return f"{value:,.0f}"


def scale(df, metric):
    return df / 1e6 if FMT.get(metric) in ("usd", "shares") else df


def unit_label(metric):
    return {"usd": "USD millions", "shares": "millions of shares", "eps": "USD per share",
            "pct": "%", "x": "times (x)", "days": "days"}.get(FMT.get(metric), "")


def latest_fy(df):
    for col in ("Net income", "Revenue", "Operating income"):
        series = df[col].dropna()
        if not series.empty:
            return series.index.max()
    return df.index.max()


# ---------- plain-English insights ----------
def generate_insights(row):
    """Return [(icon, headline, explanation)] describing strengths and watch-points of one fiscal year."""
    def g(key):
        v = row.get(key, np.nan)
        return None if pd.isna(v) or not np.isfinite(v) else float(v)

    out = []
    nm, om, gr = g("Net margin %"), g("Operating margin %"), g("Revenue growth %")
    if nm is not None:
        if nm < 0:
            out.append(("🔴", "Loss-making", f"Net margin is {nm:.1f}%: expenses exceeded revenue this year."))
        elif nm >= 20:
            out.append(("🟢", "High profitability", f"Net margin of {nm:.1f}% means about ${nm / 100:.2f} of profit per $1 of sales."))
    if om is not None and om >= 25:
        out.append(("🟢", "Strong operating profitability", f"Operating margin is {om:.1f}%, a sign of pricing power or a scalable cost base."))
    if gr is not None:
        if gr >= 15:
            out.append(("🟢", "Fast growth", f"Revenue grew {gr:.1f}% versus the prior year."))
        elif gr < 0:
            out.append(("🔴", "Shrinking sales", f"Revenue fell {abs(gr):.1f}% versus the prior year."))
    nd, ic = g("Net debt"), g("Interest coverage")
    if nd is not None and nd < 0:
        out.append(("🟢", "Net cash position", "Cash and short-term investments exceed the debt counted here."))
    if ic is not None and ic < 3:
        out.append(("🔴", "Thin interest cover", f"Operating income covers interest only {ic:.1f}x; a profit dip could strain debt service."))
    nde = g("Net debt / EBITDA")
    if nde is not None and nde > 3.5:
        out.append(("🔴", "High leverage", f"Net debt is {nde:.1f}x EBITDA; many lenders treat above ~3-4x as stretched."))
    q = g("OCF / Net income")
    if q is not None and q < 0.8:
        out.append(("🟡", "Earnings not fully backed by cash", f"Operating cash flow is only {q:.2f}x net income; check receivables, inventory and one-offs."))
    elif q is not None and q >= 1.1:
        out.append(("🟢", "High-quality earnings", f"Operating cash flow is {q:.2f}x net income."))
    fcf, po = g("Free cash flow"), g("Shareholder payout % of FCF")
    if fcf is not None and fcf < 0:
        out.append(("🔴", "Negative free cash flow", "The business spent more cash than it generated after capital spending."))
    if po is not None and po > 100:
        out.append(("🟡", "Payouts exceed free cash flow", f"Dividends + buybacks were {po:.0f}% of FCF, funded from cash reserves or borrowing."))
    cr = g("Current ratio")
    if cr is not None and cr < 1:
        out.append(("🟡", "Current ratio below 1", "Short-term liabilities exceed short-term assets; normal for some models, risky for others."))
    eq = g("Equity")
    if eq is not None and eq <= 0:
        out.append(("🟡", "Negative book equity", "ROE and debt/equity are not meaningful, often caused by large buybacks."))
    return out
