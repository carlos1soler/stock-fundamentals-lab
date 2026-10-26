"""Data access: SEC EDGAR company facts, Yahoo Finance quotes, annual extraction and TTM construction."""
import time

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

from .config import FORMS, SOURCE, TTM_ITEMS

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def empty_series():
    return pd.Series(dtype=float, index=pd.DatetimeIndex([]))


@st.cache_data(ttl=86400, show_spinner=False)
def load_tickers(user_agent):
    response = requests.get(TICKERS_URL, headers={"User-Agent": user_agent}, timeout=30)
    response.raise_for_status()
    return {item["ticker"]: str(item["cik_str"]).zfill(10) for item in response.json().values()}


@st.cache_data(ttl=86400, show_spinner=False)
def load_facts(cik, user_agent):
    time.sleep(0.15)  # stay well below the SEC's 10 requests/second limit
    response = requests.get(FACTS_URL.format(cik=cik), headers={"User-Agent": user_agent}, timeout=60)
    response.raise_for_status()
    return response.json().get("facts", {}).get("us-gaap", {})


@st.cache_data(ttl=900, show_spinner=False)
def load_market_data(ticker):
    """Latest available daily close plus market metadata from Yahoo Finance (cached 15 minutes)."""
    obj = yf.Ticker(ticker)
    price, price_time = np.nan, "Not available"
    try:
        hist = obj.history(period="5d", interval="1d", auto_adjust=False)
        closes = hist["Close"].dropna() if not hist.empty else pd.Series(dtype=float)
        if not closes.empty:
            price = float(closes.iloc[-1])
            idx = closes.index[-1]
            price_time = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)
    except Exception:
        pass
    info = {}
    try:
        info = obj.get_info() or {}
    except Exception:
        pass
    if not np.isfinite(price):
        for key in ("currentPrice", "regularMarketPrice", "previousClose"):
            try:
                candidate = float(info.get(key))
                if candidate > 0:
                    price, price_time = candidate, "Yahoo Finance quote metadata (timestamp may vary)"
                    break
            except (TypeError, ValueError):
                continue
    return {
        "price": price, "price_time": price_time, "currency": info.get("currency", "USD"),
        "market_cap": info.get("marketCap", np.nan), "shares_outstanding": info.get("sharesOutstanding", np.nan),
        "enterprise_value": info.get("enterpriseValue", np.nan), "long_name": info.get("longName", ticker),
        "sector": info.get("sector", "Unknown"), "industry": info.get("industry", "Unknown"),
        "yahoo_trailing_pe": info.get("trailingPE", np.nan), "beta": info.get("beta", np.nan),
        "week52_high": info.get("fiftyTwoWeekHigh", np.nan), "week52_low": info.get("fiftyTwoWeekLow", np.nan),
    }


def extract_series(facts, tags, unit, flow):
    """Merge all XBRL tags for one concept into a single series indexed by period end date."""
    result = empty_series()
    for tag in tags:
        records = facts.get(tag, {}).get("units", {}).get(unit)
        if not records:
            continue
        df = pd.DataFrame(records)
        df["end"] = pd.to_datetime(df["end"])
        df = df[df["form"].isin(FORMS)]
        if flow:
            if "start" not in df.columns:
                continue
            duration = (df["end"] - pd.to_datetime(df["start"])).dt.days
            df = df[(duration >= 350) & (duration <= 380)].copy()  # keep true annual periods only
        if df.empty:
            continue
        df = df.sort_values("filed").drop_duplicates(subset="end", keep="last")  # latest restatement wins
        series = df.set_index("end")["val"].astype(float)
        result = series if result.empty else result.combine_first(series)
    return result


def extract_all(facts):
    return {name: extract_series(facts, tags, unit, flow=(kind == "flow"))
            for name, (kind, unit, tags, _) in SOURCE.items()}


def _ttm_one(facts, tags, unit, annual):
    """TTM = last fiscal year + current year-to-date - same year-to-date one year earlier (10-Q data)."""
    if annual.empty:
        return None
    last_end = annual.index.max()
    for tag in tags:
        records = facts.get(tag, {}).get("units", {}).get(unit)
        if not records:
            continue
        df = pd.DataFrame(records)
        if "start" not in df.columns:
            continue
        df = df[df["form"] == "10-Q"].copy()
        if df.empty:
            continue
        df["end"], df["start"] = pd.to_datetime(df["end"]), pd.to_datetime(df["start"])
        df["days"] = (df["end"] - df["start"]).dt.days
        newer = df[(df["end"] > last_end) & df["days"].between(80, 285)]
        if newer.empty:
            continue
        cur_end = newer["end"].max()
        cur = newer[newer["end"] == cur_end].sort_values(["days", "filed"]).iloc[-1]  # longest YTD window
        if abs((cur["start"] - last_end).days) > 10:  # YTD must start right after the last fiscal year
            continue
        target = cur_end - pd.Timedelta(days=365)
        prior = df[((df["end"] - target).abs().dt.days <= 10) & ((df["days"] - cur["days"]).abs() <= 10)]
        if prior.empty:
            continue
        prior_val = float(prior.sort_values("filed").iloc[-1]["val"])
        return float(annual.loc[last_end] + float(cur["val"]) - prior_val), cur_end
    return None


def compute_ttm(facts, series):
    """Return trailing-twelve-month values; items without usable 10-Q data fall back to the last fiscal year."""
    values, as_of = {}, None
    for name in TTM_ITEMS:
        _, unit, tags, _ = SOURCE[name]
        res = _ttm_one(facts, tags, unit, series[name])
        if res:
            values[name] = res[0]
            as_of = res[1] if as_of is None else max(as_of, res[1])
        elif not series[name].empty:
            values[name] = float(series[name].iloc[-1])
    if "Operating income" in values and "D&A" in values:
        values["EBITDA"] = values["Operating income"] + values["D&A"]
    if "Operating cash flow" in values and "CapEx" in values:
        values["Free cash flow"] = values["Operating cash flow"] - abs(values["CapEx"])
    basis = f"TTM through {as_of:%Y-%m-%d}" if as_of is not None else "Last fiscal year (no newer 10-Q found)"
    return {"values": values, "basis": basis, "as_of": as_of}
