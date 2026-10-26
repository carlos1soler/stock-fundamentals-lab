"""Educational content. Each metric: what it is, formula, how to read it, what to watch out for."""


def _e(title, what, formula="", read="", watch=""):
    return {"title": title, "what": what, "formula": formula, "read": read, "watch": watch}


EXPLANATIONS = {
    # ---------------- Income statement ----------------
    "Revenue": _e("Revenue (sales)", "Total money earned from selling products and services before any expense is deducted.",
        "Price × units sold, summed over all products", "Look at the trend and mix first: is growth steady, accelerating or fading?",
        "Revenue is not profit. Growth bought with heavy discounts or acquisitions can be low quality."),
    "Cost of revenue": _e("Cost of revenue (COGS)", "Direct costs of delivering what was sold: materials, manufacturing, cloud hosting, delivery.",
        "", "Compare it with revenue through gross margin; falling cost share usually means scale or pricing power.",
        "Companies classify costs differently (e.g. depreciation inside or outside COGS), which distorts peer comparisons."),
    "Gross profit": _e("Gross profit", "Revenue minus direct costs: what is left to pay for operations, interest, tax and profit.",
        "Revenue − Cost of revenue", "Software tends to be 70%+ of revenue, retailers 20-35%, so judge against the industry.",
        "Not available for every company; the dashboard derives it when the tag is missing."),
    "R&D expense": _e("Research & development (R&D)", "Spending on new products and technology.",
        "", "R&D as a % of revenue shows how much a company reinvests in its future.",
        "Accounting rules expense most R&D immediately, which depresses current profit while building future value."),
    "SG&A expense": _e("Selling, general & administrative (SG&A)", "Overhead: marketing, sales staff, offices, management.",
        "", "Falling SG&A as a share of revenue signals operating leverage (revenue growing faster than overhead).",
        "Cutting SG&A can boost profit short-term while hurting growth."),
    "Operating income": _e("Operating income (EBIT)", "Profit from core operations after operating costs, before interest and tax.",
        "Gross profit − Operating expenses", "The cleanest view of how profitable the business itself is.",
        "One-off charges (restructuring, impairments) can distort a single year; look at several years."),
    "EBITDA": _e("EBITDA", "Operating income with depreciation & amortization added back: a rough proxy for operating cash earnings.",
        "Operating income + D&A", "Used in leverage and valuation ratios because it ignores differences in asset age and financing.",
        "Not cash flow: it ignores capital spending, working capital, interest and tax. Capital-heavy firms look better than they are."),
    "D&A": _e("Depreciation & amortization", "Non-cash accounting charge spreading the cost of long-lived assets over their useful life.",
        "", "Compare with CapEx: CapEx persistently above D&A means the asset base is growing.", ""),
    "Interest expense": _e("Interest expense", "Cost of borrowing: interest on loans and bonds.", "", "Rising interest expense with flat profit reduces safety margin.", ""),
    "Pretax income": _e("Pretax income", "Profit after interest but before income tax.", "Operating income − Interest ± other items", "", ""),
    "Income tax": _e("Income tax expense", "Tax expense recorded for the period.", "", "Effective tax rate = Income tax ÷ Pretax income.",
        "Tax credits and one-off items can make the rate jump around."),
    "Net income": _e("Net income (bottom line)", "Profit after every reported expense, interest and tax.",
        "Revenue − All expenses − Interest − Tax", "Compare with operating cash flow to see whether profit is backed by cash.",
        "Includes non-cash and one-off gains/losses such as investment revaluations."),
    "Diluted EPS": _e("Diluted earnings per share", "Net income per share, counting potential shares from options and convertibles.",
        "Net income ÷ Diluted weighted-average shares", "Growing EPS is what ultimately drives stock returns over time.",
        "Buybacks lift EPS even when net income is flat; stock splits change history (SEC data is as originally reported)."),
    "Diluted shares": _e("Weighted-average diluted shares", "Average share count over the year used to compute EPS.", "",
        "A shrinking count means buybacks outpace issuance; a growing one means dilution.", "Not the current share count."),
    # ---------------- Balance sheet ----------------
    "Cash & investments": _e("Cash & short-term investments", "Cash and liquid investments on the balance sheet.", "Cash + Short-term investments",
        "Compare with total debt and annual cash burn.", "Long-term investments are excluded, so cash-rich firms can look poorer here."),
    "Accounts receivable": _e("Accounts receivable", "Money customers owe for goods or services already delivered.", "",
        "Receivables growing faster than revenue can signal looser credit terms or collection problems.", ""),
    "Inventory": _e("Inventory", "Goods and materials held for sale or production.", "",
        "Inventory growing faster than sales may mean weak demand or obsolescence risk.", ""),
    "Current assets": _e("Current assets", "Assets expected to turn into cash within about a year.", "", "", ""),
    "Total assets": _e("Total assets", "Everything the company owns or is owed: cash, equipment, receivables, goodwill.", "Liabilities + Equity", "", ""),
    "Accounts payable": _e("Accounts payable", "Amounts owed to suppliers for goods and services already received.", "", "", ""),
    "Current liabilities": _e("Current liabilities", "Obligations due within about a year.", "", "", ""),
    "Total liabilities": _e("Total liabilities", "All reported obligations: debt, supplier bills, deferred revenue, leases and more.", "Total assets − Equity", "", ""),
    "Total debt": _e("Total debt (estimated)", "Interest-bearing borrowing identified from SEC tags; optionally includes operating leases (sidebar toggle).",
        "Long-term debt + Current debt + Commercial paper (+ Leases)", "",
        "Companies tag debt differently, so this can understate borrowing. Treat as an estimate."),
    "Lease liabilities": _e("Operating lease liabilities", "Present value of rent commitments (stores, offices, aircraft) recognized on the balance sheet since 2019.", "",
        "Retailers and airlines can carry far more lease obligations than bank debt.", "Included in debt only if you switch the sidebar option on."),
    "Net debt": _e("Net debt", "Debt minus cash and short-term investments: what would remain owed if cash repaid debt.", "Total debt − Cash & investments",
        "Negative means a net-cash position.", "Cash held abroad or needed for operations may not be freely available."),
    "Equity": _e("Shareholders' equity (book value)", "Accounting value of assets minus liabilities.", "Total assets − Total liabilities",
        "", "Not market value. Big buybacks or losses can push it negative, making ROE and debt/equity meaningless."),
    # ---------------- Cash flow ----------------
    "Operating cash flow": _e("Operating cash flow (OCF)", "Cash produced by day-to-day operations.", "Net income + non-cash items ± working capital changes",
        "Persistently below net income is a classic earnings-quality red flag.", "Timing of payments can swing a single year."),
    "CapEx": _e("Capital expenditures (CapEx)", "Cash spent on equipment, buildings, data centers and other long-term assets.", "", "CapEx ÷ Revenue shows capital intensity.",
        "Maintenance versus growth CapEx is not split out."),
    "Free cash flow": _e("Free cash flow (FCF)", "Cash left after running and reinvesting in the business: what can fund dividends, buybacks, debt paydown.",
        "Operating cash flow − CapEx", "Compare FCF with net income and over several years.", "Lumpy when CapEx is cyclical; excludes acquisitions."),
    "Dividends paid": _e("Dividends paid", "Cash distributed to shareholders.", "", "", ""),
    "Share buybacks": _e("Share repurchases", "Cash spent buying back the company's own shares.", "",
        "Good when done below intrinsic value with spare cash.", "Buying at high prices or with borrowed money destroys value; buybacks often only offset stock compensation."),
    # ---------------- Profitability ----------------
    "Gross margin %": _e("Gross margin", "Share of each sales dollar left after direct costs.", "Gross profit ÷ Revenue × 100",
        "Higher and stable = pricing power or efficient production.", "Industry differences are huge; compare peers only."),
    "Operating margin %": _e("Operating margin", "Operating profit per sales dollar.", "Operating income ÷ Revenue × 100",
        "A 15% margin means $15 operating profit per $100 of sales.", "Sensitive to one-off charges."),
    "EBITDA margin %": _e("EBITDA margin", "EBITDA relative to sales.", "EBITDA ÷ Revenue × 100", "", "Flatters capital-heavy businesses."),
    "Net margin %": _e("Net profit margin", "Final profit per sales dollar.", "Net income ÷ Revenue × 100", "Compare with operating margin to see the burden of interest and tax.",
        "Includes non-operating gains, which can inflate a year."),
    "ROE %": _e("Return on equity (ROE)", "Profit earned for each dollar of shareholders' book equity.", "Net income ÷ Average equity × 100",
        "15%+ sustained is generally strong. Use the DuPont lab to see whether margin, efficiency or leverage drives it.",
        "High leverage or buyback-shrunken equity can fake a high ROE."),
    "ROA %": _e("Return on assets (ROA)", "How much profit the asset base generates.", "Net income ÷ Average total assets × 100", "Best for comparing similar business models.", "Misleading for banks and other heavily levered firms."),
    "ROIC %": _e("Return on invested capital (ROIC)", "After-tax operating profit generated per dollar of debt and equity capital.", "NOPAT ÷ Average (Debt + Equity) × 100",
        "ROIC above the cost of capital (~8-10%) means growth creates value.", "Simplified here; analysts define invested capital differently."),
    # ---------------- Liquidity ----------------
    "Current ratio": _e("Current ratio", "Short-term assets available to cover short-term obligations.", "Current assets ÷ Current liabilities",
        "1.5 means $1.50 of current assets for each $1 owed within a year.", "Too high can mean idle cash or bloated inventory."),
    "Quick ratio": _e("Quick ratio", "Stricter liquidity test excluding inventory.", "(Cash + ST investments + Receivables) ÷ Current liabilities", "Above 1 is comfortable.", ""),
    # ---------------- Leverage ----------------
    "Debt / Equity": _e("Debt-to-equity", "Borrowing relative to book equity.", "Total debt ÷ Equity", "Below ~1 is conservative for most industries.",
        "Not meaningful when equity is negative or tiny (shown as —)."),
    "Debt / Assets": _e("Debt-to-assets", "Share of assets financed by debt.", "Total debt ÷ Total assets", "", ""),
    "Net debt / EBITDA": _e("Net debt to EBITDA", "Roughly how many years of EBITDA it would take to repay net debt.", "Net debt ÷ EBITDA",
        "Below 2x is comfortable, above 4x often stretched.", "Not meaningful when EBITDA is zero or negative (shown as —)."),
    "Interest coverage": _e("Interest coverage", "How many times operating profit covers interest costs.", "Operating income ÷ Interest expense",
        "Below 3x is thin; above 8x is comfortable.", "Companies with almost no interest cost give huge, uninformative values."),
    "Equity multiplier": _e("Equity multiplier (financial leverage)", "How many dollars of assets each dollar of equity supports.", "Average assets ÷ Average equity",
        "2.0 means half of assets are funded by equity, half by liabilities.", "Third leg of the DuPont identity."),
    # ---------------- Efficiency ----------------
    "Asset turnover": _e("Asset turnover", "Sales generated per dollar of assets.", "Revenue ÷ Average total assets", "Retail is high, utilities and telecom low.", ""),
    "Inventory turnover": _e("Inventory turnover", "How many times inventory is sold and replaced per year.", "Cost of revenue ÷ Average inventory", "Higher = leaner inventory.", "Too high can mean stock-outs."),
    "DSO (days)": _e("Days sales outstanding", "Average days to collect payment from customers.", "Receivables ÷ Revenue × 365", "Lower is faster collection.", "Business terms differ by industry."),
    "DIO (days)": _e("Days inventory outstanding", "Average days inventory sits before sale.", "Inventory ÷ Cost of revenue × 365", "", ""),
    "DPO (days)": _e("Days payable outstanding", "Average days taken to pay suppliers.", "Payables ÷ Cost of revenue × 365", "Higher funds the company with supplier credit.", "Very high may signal payment stress."),
    "Cash conversion cycle (days)": _e("Cash conversion cycle", "Days between paying suppliers and collecting from customers.", "DSO + DIO − DPO",
        "Negative means customers fund the business (typical for some retailers and subscription models).", "Companies without inventory have no DIO term."),
    # ---------------- Cash-flow quality ----------------
    "FCF margin %": _e("Free cash flow margin", "Free cash flow per sales dollar.", "FCF ÷ Revenue × 100", "10%+ is strong for many industries.", "Volatile in heavy-investment years."),
    "OCF / Net income": _e("Cash conversion (OCF ÷ net income)", "Whether reported profit turns into cash.", "Operating cash flow ÷ Net income",
        "Around or above 1.0 is healthy.", "Only computed when net income is positive."),
    "CapEx / Revenue %": _e("Capital intensity", "Share of revenue reinvested in long-term assets.", "CapEx ÷ Revenue × 100", "Software is low; utilities and semiconductors high.", ""),
    "Dividend payout %": _e("Dividend payout ratio", "Share of profit paid out as dividends.", "Dividends ÷ Net income × 100", "40-60% is typical for mature payers.", "Not computed when net income is negative."),
    "Shareholder payout % of FCF": _e("Shareholder payout of FCF", "Dividends plus buybacks as a share of free cash flow.", "(Dividends + Buybacks) ÷ FCF × 100",
        "Over 100% means payouts exceeded FCF, funded by cash or borrowing.", "Only computed when FCF is positive."),
    # ---------------- Growth ----------------
    "Revenue growth %": _e("Revenue growth", "Year-over-year change in sales.", "(Revenue − Prior revenue) ÷ Prior revenue × 100", "Check consistency across years.", "Acquisitions inflate growth."),
    "EBITDA growth %": _e("EBITDA growth", "Year-over-year change in EBITDA.", "", "", "Unavailable when the prior year is zero or negative."),
    "Net income growth %": _e("Net income growth", "Year-over-year change in profit.", "", "", "Unavailable when the prior year is zero or negative."),
    "EPS growth %": _e("EPS growth", "Year-over-year change in earnings per share.", "", "", "Stock splits and buybacks affect it."),
    "FCF growth %": _e("Free cash flow growth", "Year-over-year change in free cash flow.", "", "", "Volatile when FCF is small."),
}

VALUATION_EXPLANATIONS = {
    "P/E (price / EPS)": _e("Price-to-earnings", "What investors pay per dollar of annual earnings.", "Share price ÷ Diluted EPS",
        "High P/E = high growth expectations (or an expensive stock); low P/E = low expectations (or a problem).",
        "Uses TTM EPS when available. Meaningless when EPS is negative."),
    "EV / EBITDA": _e("Enterprise value / EBITDA", "Price of the whole business (equity + net debt) relative to operating earnings.", "(Market cap + Net debt) ÷ EBITDA",
        "Capital-structure neutral, so useful across companies with different debt.", "Ignores CapEx; Yahoo's EV and SEC EBITDA may have different dates."),
    "EV / Revenue": _e("Enterprise value / revenue", "Value of the business per dollar of sales.", "EV ÷ Revenue", "Used for young or unprofitable companies.", "Says nothing about profitability."),
    "P/S": _e("Price-to-sales", "Market cap per dollar of sales.", "Market cap ÷ Revenue", "Interpret together with margins.", ""),
    "P/B": _e("Price-to-book", "Market cap relative to accounting equity.", "Market cap ÷ Equity", "Most useful for banks and insurers.", "Weak for asset-light, buyback-heavy companies."),
    "P/FCF": _e("Price-to-free-cash-flow", "Market cap per dollar of free cash flow.", "Market cap ÷ FCF", "Lower can mean cheaper, if FCF is sustainable.", "FCF must be positive."),
    "FCF yield %": _e("Free cash flow yield", "FCF as a percentage of market cap, the inverse of P/FCF.", "FCF ÷ Market cap × 100", "Compare with bond yields and your required return.", "Not a guaranteed return."),
    "Dividend yield %": _e("Dividend yield", "Annual dividends relative to market cap.", "Dividends ÷ Market cap × 100", "", "Based on reported dividends, not the announced current rate."),
}

STATEMENTS_LESSON = """
**The three statements tell one connected story**

| Statement | Question it answers | Time view | Key lines |
|---|---|---|---|
| **Income statement** | Did the company make a profit? | A period (year) | Revenue → Gross profit → Operating income → Net income |
| **Balance sheet** | What does it own and owe? | A moment (year-end) | Assets = Liabilities + Equity |
| **Cash-flow statement** | Where did the cash actually go? | A period (year) | Operating, investing, financing cash flows |

**How they connect:** net income flows into equity (balance sheet) and is the starting point of operating cash flow;
CapEx on the cash-flow statement becomes assets on the balance sheet; borrowing and dividends change liabilities and equity.
A healthy company shows consistent stories across all three: profits that turn into cash and a balance sheet that stays solid.
"""

QUESTIONS = [
    ("Is the business growing?", "Revenue growth %, EPS growth %", "Compare tab → Growth"),
    ("Is it profitable, and is that improving?", "Gross / operating / net margin", "Compare tab → Profitability"),
    ("Does it earn good returns on capital?", "ROE %, ROIC %, DuPont", "Compare tab → Profitability, Lab tab"),
    ("Is profit backed by real cash?", "OCF / Net income, FCF margin %", "Compare tab → Cash Flow Quality"),
    ("Can it survive a downturn?", "Current ratio, Net debt / EBITDA, Interest coverage", "Scorecard, Compare → Leverage"),
    ("Is management allocating capital well?", "CapEx / Revenue, payouts, ROIC", "Compare → Cash Flow Quality"),
    ("Is the price reasonable?", "P/E, EV/EBITDA, FCF yield, DCF playground", "Valuation and Lab tabs"),
]

QUIZ = [
    {"q": "A company reports net income of $100M but operating cash flow of only $20M for several years. What is the most sensible reaction?",
     "options": ["Great, profits are high", "Investigate earnings quality: receivables, inventory, accruals", "Ignore cash flow; only net income matters", "Conclude the stock is cheap"],
     "answer": 1, "why": "Persistent gaps between profit and operating cash flow are a classic warning sign that earnings are not converting into cash."},
    {"q": "A firm has ROE of 45% but negative shareholders' equity after huge buybacks. What does the ROE tell you?",
     "options": ["Excellent returns", "Very little; a tiny or negative denominator distorts it", "The firm has no debt", "Margins must be high"],
     "answer": 1, "why": "ROE divides by book equity. When equity is small or negative, the ratio loses meaning, so check ROIC and the DuPont breakdown."},
    {"q": "Net debt / EBITDA is −0.5x. What does that mean?",
     "options": ["The company is bankrupt", "Cash exceeds debt (net cash position)", "EBITDA is negative", "Debt is half of EBITDA"],
     "answer": 1, "why": "Net debt = Debt − Cash. A negative value means cash and short-term investments exceed the debt counted."},
    {"q": "Why is EV/EBITDA often preferred to P/E when comparing companies with different debt levels?",
     "options": ["It ignores profit", "EV includes debt, so capital structure matters less", "EBITDA is always higher", "P/E cannot be calculated"],
     "answer": 1, "why": "Enterprise value adds net debt to market cap, and EBITDA sits before interest, so the ratio compares the whole business regardless of financing."},
    {"q": "Which statement about EBITDA is TRUE?",
     "options": ["It equals free cash flow", "It ignores capital spending", "It includes taxes", "It is audited as a cash figure"],
     "answer": 1, "why": "EBITDA adds back D&A and ignores CapEx, working capital, interest and tax, so it is not cash flow."},
    {"q": "Why can't you judge a bank with the same margin and current-ratio thresholds as a software company?",
     "options": ["Banks don't report income", "Their business model and balance sheet work differently (deposits are liabilities, interest is revenue)", "Banks have no equity", "Software firms are always bigger"],
     "answer": 1, "why": "For banks, debt is the raw material of the business, so leverage and liquidity ratios built for industrial companies are misleading."},
]
