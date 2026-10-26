"""Static configuration: SEC XBRL tag map, metric groups, number formats and scoring thresholds."""

FORMS = ["10-K", "10-K/A"]

# name: (kind, unit, [XBRL tags tried in order and merged], display format)
SOURCE = {
    "Revenue": ("flow", "USD", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet"], "usd"),
    "Cost of revenue": ("flow", "USD", ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"], "usd"),
    "Gross profit": ("flow", "USD", ["GrossProfit"], "usd"),
    "R&D expense": ("flow", "USD", ["ResearchAndDevelopmentExpense"], "usd"),
    "SG&A expense": ("flow", "USD", ["SellingGeneralAndAdministrativeExpense"], "usd"),
    "Operating income": ("flow", "USD", ["OperatingIncomeLoss", "OperatingProfitLoss"], "usd"),
    "D&A": ("flow", "USD", ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet",
        "DepreciationAndAmortization", "Depreciation"], "usd"),
    "Interest expense": ("flow", "USD", ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"], "usd"),
    "Pretax income": ("flow", "USD", [
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"], "usd"),
    "Income tax": ("flow", "USD", ["IncomeTaxExpenseBenefit"], "usd"),
    "Net income": ("flow", "USD", ["NetIncomeLoss", "ProfitLoss"], "usd"),
    "Diluted EPS": ("flow", "USD/shares", ["EarningsPerShareDiluted"], "eps"),
    "Diluted shares": ("flow", "shares", ["WeightedAverageNumberOfDilutedSharesOutstanding"], "shares"),
    "Operating cash flow": ("flow", "USD", ["NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], "usd"),
    "CapEx": ("flow", "USD", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
        "PaymentsForCapitalImprovements"], "usd"),
    "Dividends paid": ("flow", "USD", ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"], "usd"),
    "Share buybacks": ("flow", "USD", ["PaymentsForRepurchaseOfCommonStock"], "usd"),
    "Cash": ("instant", "USD", ["CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"], "usd"),
    "Short-term investments": ("instant", "USD", ["MarketableSecuritiesCurrent", "ShortTermInvestments",
        "AvailableForSaleSecuritiesDebtSecuritiesCurrent"], "usd"),
    "Accounts receivable": ("instant", "USD", ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], "usd"),
    "Inventory": ("instant", "USD", ["InventoryNet"], "usd"),
    "Current assets": ("instant", "USD", ["AssetsCurrent"], "usd"),
    "Total assets": ("instant", "USD", ["Assets"], "usd"),
    "Accounts payable": ("instant", "USD", ["AccountsPayableCurrent", "AccountsPayableTradeCurrent"], "usd"),
    "Current liabilities": ("instant", "USD", ["LiabilitiesCurrent"], "usd"),
    "Total liabilities": ("instant", "USD", ["Liabilities"], "usd"),
    "Long-term debt": ("instant", "USD", ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations"], "usd"),
    "Long-term debt (total)": ("instant", "USD", ["LongTermDebt"], "usd"),
    "Current debt": ("instant", "USD", ["LongTermDebtCurrent", "DebtCurrent",
        "LongTermDebtAndCapitalLeaseObligationsCurrent"], "usd"),
    "Commercial paper": ("instant", "USD", ["CommercialPaper"], "usd"),
    "Operating lease (current)": ("instant", "USD", ["OperatingLeaseLiabilityCurrent"], "usd"),
    "Operating lease (non-current)": ("instant", "USD", ["OperatingLeaseLiabilityNoncurrent"], "usd"),
    "Equity": ("instant", "USD", ["StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "usd"),
}

# Flow items for which a trailing-twelve-month (TTM) value is built from 10-Q filings.
TTM_ITEMS = ["Revenue", "Operating income", "D&A", "Net income", "Diluted EPS",
             "Operating cash flow", "CapEx", "Dividends paid", "Share buybacks"]

GROUPS = {
    "Income Statement": ["Revenue", "Cost of revenue", "Gross profit", "R&D expense", "SG&A expense",
        "Operating income", "EBITDA", "D&A", "Interest expense", "Pretax income", "Income tax",
        "Net income", "Diluted EPS", "Diluted shares"],
    "Balance Sheet": ["Cash & investments", "Accounts receivable", "Inventory", "Current assets", "Total assets",
        "Accounts payable", "Current liabilities", "Total liabilities", "Total debt", "Lease liabilities",
        "Net debt", "Equity"],
    "Cash Flow": ["Operating cash flow", "CapEx", "Free cash flow", "Dividends paid", "Share buybacks"],
    "Profitability": ["Gross margin %", "Operating margin %", "EBITDA margin %", "Net margin %",
        "ROE %", "ROA %", "ROIC %"],
    "Liquidity": ["Current ratio", "Quick ratio"],
    "Leverage & Solvency": ["Debt / Equity", "Debt / Assets", "Net debt / EBITDA", "Interest coverage",
        "Equity multiplier"],
    "Efficiency": ["Asset turnover", "Inventory turnover", "DSO (days)", "DIO (days)", "DPO (days)",
        "Cash conversion cycle (days)"],
    "Cash Flow Quality & Payouts": ["FCF margin %", "OCF / Net income", "CapEx / Revenue %",
        "Dividend payout %", "Shareholder payout % of FCF"],
    "Growth": ["Revenue growth %", "EBITDA growth %", "Net income growth %", "EPS growth %", "FCF growth %"],
}

FMT = {name: cfg[3] for name, cfg in SOURCE.items()}
FMT.update({"EBITDA": "usd", "Cash & investments": "usd", "Total debt": "usd",
            "Lease liabilities": "usd", "Net debt": "usd", "Free cash flow": "usd"})
for _metric in sum(GROUPS.values(), []):
    if _metric not in FMT:
        FMT[_metric] = "pct" if _metric.endswith("%") else ("days" if "(days)" in _metric else "x")

# metric: (higher_is_better, green_threshold, yellow_threshold)
SCORECARD = {
    "Operating margin %": (True, 15, 8), "Net margin %": (True, 10, 5), "ROE %": (True, 15, 8),
    "ROIC %": (True, 12, 7), "Current ratio": (True, 1.5, 1.0), "Quick ratio": (True, 1.0, 0.7),
    "Debt / Equity": (False, 1.0, 2.0), "Net debt / EBITDA": (False, 2.0, 3.5),
    "Interest coverage": (True, 8, 3), "FCF margin %": (True, 10, 5),
    "OCF / Net income": (True, 1.0, 0.8), "Revenue growth %": (True, 8, 3),
}

# Sector-specific replacements for the generic thresholds (sector names follow Yahoo Finance).
SECTOR_OVERRIDES = {
    "Technology": {"Operating margin %": (True, 25, 12), "Net margin %": (True, 20, 10), "ROIC %": (True, 15, 8)},
    "Communication Services": {"Operating margin %": (True, 20, 10), "Net margin %": (True, 12, 6)},
    "Healthcare": {"Operating margin %": (True, 20, 10), "Net margin %": (True, 15, 7)},
    "Consumer Defensive": {"Operating margin %": (True, 8, 4), "Net margin %": (True, 5, 2.5),
        "Current ratio": (True, 1.0, 0.8), "Quick ratio": (True, 0.6, 0.4), "ROIC %": (True, 10, 6),
        "FCF margin %": (True, 5, 2)},
    "Consumer Cyclical": {"Operating margin %": (True, 10, 5), "Net margin %": (True, 7, 3),
        "Current ratio": (True, 1.2, 0.9), "Debt / Equity": (False, 1.5, 3.0), "ROIC %": (True, 10, 6),
        "FCF margin %": (True, 6, 2)},
    "Industrials": {"Operating margin %": (True, 12, 6), "Net margin %": (True, 8, 4),
        "Debt / Equity": (False, 1.2, 2.5), "ROIC %": (True, 10, 6)},
    "Energy": {"Operating margin %": (True, 12, 5), "Net margin %": (True, 8, 3),
        "Net debt / EBITDA": (False, 1.5, 3.0), "Revenue growth %": (True, 5, 0)},
    "Basic Materials": {"Operating margin %": (True, 15, 8), "Net margin %": (True, 10, 5),
        "Net debt / EBITDA": (False, 2.0, 3.5)},
    "Utilities": {"Operating margin %": (True, 18, 12), "Net margin %": (True, 10, 6), "ROE %": (True, 10, 7),
        "ROIC %": (True, 6, 4), "Current ratio": (True, 0.8, 0.6), "Quick ratio": (True, 0.5, 0.3),
        "Debt / Equity": (False, 1.5, 2.5), "Net debt / EBITDA": (False, 4.5, 6.0),
        "Interest coverage": (True, 3.5, 2.0), "FCF margin %": (True, 5, -5)},
}

POORLY_SUITED_SECTORS = {"Financial Services", "Real Estate"}
