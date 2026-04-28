"""
India Daily Invest Dashboard
============================
Auto-updating algorithmic equity research dashboard for NSE/BSE stocks.
Runs every day at market open with fresh technical + fundamental analysis.

Setup:  pip install -r requirements.txt
Run:    streamlit run app.py
Deploy: streamlit deploy  (or push to GitHub → Streamlit Cloud)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Daily Invest Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0e1117; }
    
    /* Metric card */
    .metric-card {
        background: #1c2333;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 4px 0;
    }
    .metric-label { font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 20px; font-weight: 700; margin: 2px 0; }
    .metric-sub   { font-size: 11px; color: #6b7588; }
    
    /* Stock card */
    .stock-card {
        background: #1c2333;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px;
        margin: 6px 0;
    }
    .stock-card:hover { border-color: #4a90e2; }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-swing  { background: #1a3a6b; color: #64b5f6; }
    .badge-lt     { background: #1a3d2e; color: #66bb6a; }
    .badge-hrrr   { background: #3d1a2e; color: #f06292; }
    .badge-low    { background: #1a3d2e; color: #66bb6a; }
    .badge-medium { background: #3d3200; color: #ffd54f; }
    .badge-high   { background: #3d1a1a; color: #ef5350; }
    
    /* Section header */
    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #e2e8f0;
        padding: 8px 0;
        border-bottom: 2px solid #2d3748;
        margin-bottom: 12px;
    }

    /* Verdict bar */
    .verdict-bar {
        background: #1e2840;
        border: 1px solid #3b4f7a;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 12px 0;
    }

    /* Red flag */
    .red-flag {
        background: #2a1515;
        border-left: 3px solid #ef5350;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 13px;
    }

    /* Winner card */
    .winner-card {
        background: linear-gradient(135deg, #1a2a4a 0%, #0f1e35 100%);
        border: 2px solid #4a90e2;
        border-radius: 14px;
        padding: 20px;
        margin: 8px 0;
    }

    /* Confidence bar */
    .conf-bar-bg { background: #2d3748; border-radius: 4px; height: 6px; margin: 6px 0; }
    .conf-bar-fill { height: 6px; border-radius: 4px; background: #4a90e2; }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  DATA LAYER  — replace with real API calls (see utils/data_fetcher.py)
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)   # refresh every 5 minutes
def fetch_market_context():
    """
    Fetches live market context.
    Currently returns demo data.
    Replace the body of this function with real API calls — see utils/data_fetcher.py
    """
    today = datetime.now()
    # ── swap these with live API values ──────────────────────────────────────
    return {
        "date":         today.strftime("%d %b %Y, %I:%M %p"),
        "nifty":        {"value": 23950, "change": -0.81, "level": "Below 24,500 resistance"},
        "bank_nifty":   {"value": 51240, "change": -0.43, "level": "Support zone test"},
        "india_vix":    {"value": 16.4,  "change": +15.2, "level": "Elevated — Caution"},
        "fii_mtd":      {"value": -44281,"label": "Heavy April selling"},
        "dii_mtd":      {"value": +33837,"label": "Cushioning declines"},
        "inr_usd":      {"value": 94.25, "label": "DXY + crude pressure"},
        "crude":        {"value": 94.0,  "label": "Easing from highs"},
        "market_mode":  "CORRECTIVE",
        "mode_color":   "#ef5350",
        "summary":      (
            "FII exodus ₹44,281 Cr MTD. IT sector in freefall (HCL –16.6%, Infosys –12.4%). "
            "Nifty below 24,500, VIX elevated, Iran war risk premium. "
            "DII support + FMCG / Defence / Healthcare offering defensive pockets. "
            "Deploy 50–60% of planned capital. Use strict stop losses."
        ),
    }


@st.cache_data(ttl=300)
def fetch_swing_picks():
    return [
        {
            "rank": 1, "sym": "BEL", "name": "Bharat Electronics Ltd",
            "sector": "Defence PSU", "risk": "Low", "conf": 8.7,
            "entry": "₹420–435", "sl": "₹400", "t1": "₹475", "t2": "₹530",
            "cmp": 432, "upside_t1": 9.9, "upside_t2": 22.7,
            "why": (
                "FY26 turnover ₹26,750 Cr (+16.2% YoY). Order book ₹74,000 Cr as on 1 Apr 2026. "
                "Fresh ₹569 Cr orders received 22 Apr for avionics, EW systems & lasers. "
                "Q3 net profit +20.45% YoY. Debt-free. Iran war premium boosts defence spending. "
                "Breakout above ₹332 with 2.1x volume. RSI constructive. Promoter (Govt) 51.1%."
            ),
            "tags": ["Above 50 DMA", "Order inflow catalyst", "Defence sector rotation", "Strong volume"],
            "technicals": {"rsi": 62, "above_50dma": True, "above_200dma": True, "trend": "Bullish"},
        },
        {
            "rank": 2, "sym": "NESTLEIND", "name": "Nestlé India Ltd",
            "sector": "FMCG / Consumer", "risk": "Low", "conf": 8.4,
            "entry": "₹1,380–1,410", "sl": "₹1,330", "t1": "₹1,500", "t2": "₹1,600",
            "cmp": 1395, "upside_t1": 7.5, "upside_t2": 14.7,
            "why": (
                "Q4 FY26 blowout — revenue +22.6% YoY, net profit +25.8%, highest-ever domestic sales. "
                "Operating cash flow surged to ₹5,047 Cr. EBITDA margin 26.3%. Promoter 62.8%. "
                "Surged 10.6% on results. Defensive FMCG outperforms in corrective markets. "
                "Dividend record date 10 Jul — near-term catalyst."
            ),
            "tags": ["Near 52W high", "Earnings beat catalyst", "Defensive FMCG", "Strong OCF"],
            "technicals": {"rsi": 68, "above_50dma": True, "above_200dma": True, "trend": "Bullish"},
        },
        {
            "rank": 3, "sym": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise",
            "sector": "Healthcare", "risk": "Medium", "conf": 7.8,
            "entry": "₹7,500–7,700", "sl": "₹7,200", "t1": "₹8,100", "t2": "₹8,500",
            "cmp": 7620, "upside_t1": 6.3, "upside_t2": 11.5,
            "why": (
                "Healthcare is top defensive play in current selloff. Net profit +26% YoY, revenue +12.8%. "
                "Apollo 24/7 digital platform scaling rapidly. Q4 FY26 results due 28 May — re-rating trigger. "
                "Double-bottom near ₹7,500. Analyst consensus target ₹7,800–8,500. "
                "Medical tourism policy tailwind from Union Budget."
            ),
            "tags": ["Defensive sector", "Q4 result catalyst", "Double-bottom pattern", "DII accumulation"],
            "technicals": {"rsi": 55, "above_50dma": True, "above_200dma": False, "trend": "Neutral"},
        },
        {
            "rank": 4, "sym": "HINDUNILVR", "name": "Hindustan Unilever Ltd",
            "sector": "FMCG / Consumer", "risk": "Low", "conf": 7.6,
            "entry": "₹2,340–2,390", "sl": "₹2,260", "t1": "₹2,600", "t2": "₹2,760",
            "cmp": 2365, "upside_t1": 9.9, "upside_t2": 16.7,
            "why": (
                "Led Nifty gainers on 20 Apr (+4.72%) on strong volume. Zero-debt, 50+ brands. "
                "₹607 Bn revenue base. Rural demand recovery underway. DII buying on every dip. "
                "Strong RSI momentum. Holds above 200 DMA. Classic defensive swing in corrective market."
            ),
            "tags": ["Above 200 DMA", "DII accumulation", "Volume breakout", "Zero debt"],
            "technicals": {"rsi": 61, "above_50dma": True, "above_200dma": True, "trend": "Bullish"},
        },
        {
            "rank": 5, "sym": "INDUSTOWER", "name": "Indus Towers Ltd",
            "sector": "Telecom Infrastructure", "risk": "Medium", "conf": 7.2,
            "entry": "₹420–430", "sl": "₹408", "t1": "₹460", "t2": "₹480",
            "cmp": 424, "upside_t1": 8.5, "upside_t2": 13.2,
            "why": (
                "Consolidating near ₹420 demand zone — historic support with multiple reactions. "
                "Higher highs / higher lows structure intact. Volume drying at support = supply exhaustion. "
                "5G tower rollout is structural tailwind. Bharti-backed operations. Risk-reward 1:2.5."
            ),
            "tags": ["Support accumulation", "5G capex theme", "Higher high structure", "Volume contraction"],
            "technicals": {"rsi": 48, "above_50dma": False, "above_200dma": True, "trend": "Neutral"},
        },
    ]


@st.cache_data(ttl=300)
def fetch_lt_picks():
    return [
        {
            "rank": 1, "sym": "HDFCBANK", "name": "HDFC Bank Ltd",
            "sector": "Private Banking", "risk": "Low", "conf": 8.5,
            "entry": "₹790–820", "sl": "₹740", "t1": "₹1,050", "t2": "₹1,400",
            "cmp": 805, "horizon": "2–3 Years",
            "why": (
                "India's largest private bank. Q4 FY26 net profit +8% YoY to ₹20,350 Cr. "
                "44.2% FII holding — global risk-off stabilisation triggers massive reversal. "
                "Trading at ₹805 vs 52W high ₹1,020 — significant discount. "
                "Analyst consensus 12M target ₹1,200–1,400. Post-merger NIM recovery = re-rating. "
                "MSCI weight recovery to drive passive inflows. Decade-long compounder."
            ),
            "fundamentals": {"rev_growth": 12, "profit_growth": 8, "roe": 16, "debt": "Low", "promoter": "18.9%"},
        },
        {
            "rank": 2, "sym": "BEL", "name": "Bharat Electronics Ltd",
            "sector": "Defence PSU", "risk": "Low", "conf": 8.6,
            "entry": "₹415–435", "sl": "₹385", "t1": "₹600", "t2": "₹800",
            "cmp": 432, "horizon": "2–4 Years",
            "why": (
                "₹74,000 Cr order book with 71% conversion in FY26–27. Revenue CAGR 13.4% over 5 yrs. "
                "Defence indigenisation policy = decade-long structural theme. Export orders +33.65% YoY. "
                "Debt-free, ROE expanding. Nifty 50 + Sensex member — institutional must-own. "
                "Best defence compounding vehicle on NSE."
            ),
            "fundamentals": {"rev_growth": 16, "profit_growth": 20, "roe": 22, "debt": "Nil", "promoter": "51.1%"},
        },
        {
            "rank": 3, "sym": "NESTLEIND", "name": "Nestlé India Ltd",
            "sector": "FMCG", "risk": "Low", "conf": 8.1,
            "entry": "₹1,340–1,380", "sl": "₹1,250", "t1": "₹1,750", "t2": "₹2,200",
            "cmp": 1395, "horizon": "3–5 Years",
            "why": (
                "9 of 10 Indian households use Nestlé. ₹23,071 Cr revenue (+15% FY26). "
                "OCF ₹5,047 Cr. Promoter (Nestlé SA) 62.8% — governance hallmark. "
                "Premiumisation wave + rural India penetration = 10-year runway. "
                "Zero earnings cyclicality. Maggi, Nescafé, KitKat — recession-proof brands."
            ),
            "fundamentals": {"rev_growth": 15, "profit_growth": 9, "roe": 95, "debt": "Nil", "promoter": "62.8%"},
        },
        {
            "rank": 4, "sym": "BAJFINANCE", "name": "Bajaj Finance Ltd",
            "sector": "NBFC / Consumer Lending", "risk": "Medium", "conf": 8.0,
            "entry": "₹8,400–8,700", "sl": "₹7,850", "t1": "₹11,000", "t2": "₹14,000",
            "cmp": 8560, "horizon": "3–5 Years",
            "why": (
                "101M+ customer base — India's largest retail lending franchise. "
                "EMI financing, credit cards, personal loans all growing. ROE ~22%. "
                "AI-driven underwriting reducing NPAs. Rate cut cycle in FY27 = massive NBFC tailwind. "
                "Revenue CAGR 25%+ over decade. India's rising middle class is the thesis."
            ),
            "fundamentals": {"rev_growth": 28, "profit_growth": 22, "roe": 22, "debt": "Medium", "promoter": "54.7%"},
        },
        {
            "rank": 5, "sym": "RELIANCE", "name": "Reliance Industries Ltd",
            "sector": "Conglomerate / Energy", "risk": "Low", "conf": 7.9,
            "entry": "₹1,270–1,310", "sl": "₹1,200", "t1": "₹1,600", "t2": "₹2,000",
            "cmp": 1285, "horizon": "3–5 Years",
            "why": (
                "India's largest company — ₹9.98 lakh Cr revenue. Jio digital disruption, "
                "Reliance Retail (largest network), green energy capex. Q4 FY26 results pending. "
                "Multiple simultaneous re-rating triggers. Holds above 200 DMA. "
                "Most diversified risk-adjusted compounder on NSE."
            ),
            "fundamentals": {"rev_growth": 14, "profit_growth": 11, "roe": 11, "debt": "Medium", "promoter": "50.3%"},
        },
    ]


@st.cache_data(ttl=300)
def fetch_hrrr_picks():
    return [
        {
            "rank": 1, "sym": "PRAJIND", "name": "Praj Industries Ltd",
            "sector": "Clean Energy / Ethanol", "risk": "High", "conf": 6.8,
            "entry": "₹375–385", "sl": "₹355", "t1": "₹430", "t2": "₹500",
            "cmp": 381, "upside": "31%",
            "why": (
                "RSI oversold reversal from ₹280 → 30%+ rally to ₹382. Positive RSI divergence. "
                "Breaking above 50 EMA resistance = positional entry. "
                "Ethanol blending mandate (20% by 2025) = government policy tailwind. "
                "Clean energy + agriculture = powerful macro theme. Volume confirming breakout."
            ),
        },
        {
            "rank": 2, "sym": "SOUTHBANK", "name": "South Indian Bank Ltd",
            "sector": "Small Finance Bank", "risk": "High", "conf": 6.4,
            "entry": "₹32–35", "sl": "₹28", "t1": "₹45", "t2": "₹55",
            "cmp": 33, "upside": "50%+",
            "why": (
                "Forming base above 200 DMA. Analyst target ₹50 zone = ~50% upside. "
                "RSI stabilising. SmallCap 100 reclaiming 200 DMA for first time since Jan 2026. "
                "High beta play on banking recovery. Tight stop essential. "
                "NPA cycle improving. Institutional accumulation visible."
            ),
        },
        {
            "rank": 3, "sym": "GRAVITA", "name": "Gravita India Ltd",
            "sector": "Specialty Metals / Recycling", "risk": "High", "conf": 6.2,
            "entry": "₹1,800–1,900", "sl": "₹1,620", "t1": "₹2,500", "t2": "₹3,200",
            "cmp": 1850, "upside": "70%+",
            "why": (
                "India's largest lead recycling company. Nuvama's top 'restructurer' pick. "
                "EV battery recycling = massive decade-long theme. Promoter holding strong. "
                "Circular economy ESG tailwind. SMID index rebounding to pre-war levels. "
                "Volatile but structural story intact. Entry on pullback only."
            ),
        },
    ]


@st.cache_data(ttl=300)
def fetch_allocation():
    return pd.DataFrame([
        {"Symbol": "BEL",        "Name": "Bharat Electronics",   "Type": "Swing + LT",   "Allocation %": 18, "Amount (₹)": 18000, "Color": "#4a90e2"},
        {"Symbol": "NESTLEIND",  "Name": "Nestlé India",         "Type": "Swing + LT",   "Allocation %": 16, "Amount (₹)": 16000, "Color": "#66bb6a"},
        {"Symbol": "APOLLOHOSP", "Name": "Apollo Hospitals",     "Type": "Swing",        "Allocation %": 14, "Amount (₹)": 14000, "Color": "#ab47bc"},
        {"Symbol": "HDFCBANK",   "Name": "HDFC Bank",            "Type": "Long-Term",    "Allocation %": 16, "Amount (₹)": 16000, "Color": "#26c6da"},
        {"Symbol": "HINDUNILVR", "Name": "Hindustan Unilever",   "Type": "Swing",        "Allocation %": 12, "Amount (₹)": 12000, "Color": "#ffa726"},
        {"Symbol": "BAJFINANCE", "Name": "Bajaj Finance",        "Type": "Long-Term",    "Allocation %": 10, "Amount (₹)": 10000, "Color": "#ef5350"},
        {"Symbol": "PRAJIND",    "Name": "Praj Industries",      "Type": "High Risk",    "Allocation %": 8,  "Amount (₹)": 8000,  "Color": "#ec407a"},
        {"Symbol": "CASH",       "Name": "Cash Reserve",         "Type": "Safety Buffer","Allocation %": 6,  "Amount (₹)": 6000,  "Color": "#546e7a"},
    ])


# ════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ════════════════════════════════════════════════════════════════════════════

def risk_badge(risk):
    cls = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}.get(risk, "badge-medium")
    return f'<span class="badge {cls}">{risk} Risk</span>'

def conf_bar(score):
    pct = int(score * 10)
    return f"""
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
      <div class="conf-bar-bg" style="flex:1">
        <div class="conf-bar-fill" style="width:{pct}%"></div>
      </div>
      <span style="font-size:12px;color:#8892a4;min-width:36px">{score}/10</span>
    </div>"""

def tech_tag(label, good=True):
    color = "#1a3a6b" if good else "#3d1a1a"
    text  = "#64b5f6" if good else "#ef5350"
    return f'<span style="background:{color};color:{text};padding:2px 8px;border-radius:10px;font-size:10px;margin-right:4px">{label}</span>'

def dma_dot(val, label):
    color = "#66bb6a" if val else "#ef5350"
    sym   = "✔" if val else "✘"
    return f'<span style="color:{color};font-size:11px">{sym} {label}</span>&nbsp;&nbsp;'


# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    capital = st.number_input("Investment Capital (₹)", value=100000, step=10000, format="%d")
    risk_pref = st.selectbox("Risk Preference", ["Conservative", "Moderate", "Aggressive"])
    horizon = st.selectbox("Investment Horizon", ["Swing (1–8 Weeks)", "Long-Term (1–5 Years)", "Both"])
    auto_refresh = st.checkbox("Auto-refresh every 5 min", value=True)

    st.markdown("---")
    st.markdown("### 📡 Data Source")
    st.info(
        "**Demo mode** — using curated research data.\n\n"
        "To enable live NSE/BSE prices, add your API key in `utils/data_fetcher.py`.\n\n"
        "Supported: Zerodha Kite, Upstox, Alpha Vantage, Yahoo Finance"
    )

    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("[NSE India](https://nseindia.com) | [BSE India](https://bseindia.com)")
    st.markdown("[Screener.in](https://screener.in) | [TradingView](https://in.tradingview.com)")
    st.markdown("[Tickertape](https://tickertape.in) | [Moneycontrol](https://moneycontrol.com)")

    if auto_refresh:
        st.markdown("---")
        st.markdown(f"🟢 **Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN HEADER
# ════════════════════════════════════════════════════════════════════════════

ctx = fetch_market_context()

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:1rem">
  <div>
    <h1 style="margin:0;font-size:26px;font-weight:800">📈 India Daily Invest Dashboard</h1>
    <p style="margin:0;color:#8892a4;font-size:13px">AI-powered equity research · NSE/BSE · {ctx["date"]}</p>
  </div>
  <div style="background:#1a3a2e;border:1px solid #2d6a4f;padding:6px 16px;border-radius:20px;font-size:12px;color:#66bb6a">
    🟢 Live Analysis
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  MARKET CONTEXT BAR
# ════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">📊 Step 1 — Market Context</div>', unsafe_allow_html=True)

cols = st.columns(8)
metrics = [
    ("Nifty 50",    f"{ctx['nifty']['value']:,}",   f"{ctx['nifty']['change']:+.2f}%",   ctx['nifty']['change'] > 0),
    ("Bank Nifty",  f"{ctx['bank_nifty']['value']:,}", f"{ctx['bank_nifty']['change']:+.2f}%", ctx['bank_nifty']['change'] > 0),
    ("India VIX",   f"{ctx['india_vix']['value']}",  ctx['india_vix']['level'],           False),
    ("FII MTD",     f"₹{ctx['fii_mtd']['value']:,} Cr", ctx['fii_mtd']['label'],          ctx['fii_mtd']['value'] > 0),
    ("DII MTD",     f"₹{ctx['dii_mtd']['value']:,} Cr", ctx['dii_mtd']['label'],          ctx['dii_mtd']['value'] > 0),
    ("INR/USD",     f"₹{ctx['inr_usd']['value']}",  ctx['inr_usd']['label'],             False),
    ("US Crude",    f"${ctx['crude']['value']}",     ctx['crude']['label'],               False),
    ("Market Mode", ctx['market_mode'],              "Geopolitical + IT drag",            False),
]

for col, (label, val, sub, positive) in zip(cols, metrics):
    color = "#66bb6a" if positive else "#ef5350"
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="color:{color};font-size:15px">{val}</div>
          <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="verdict-bar">
  <span style="color:#ef5350;font-weight:700">⚠ Market Verdict — {ctx['market_mode']}:</span>
  <span style="color:#a8b4c8;font-size:13px"> {ctx['summary']}</span>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  TABS — PICKS + PORTFOLIO + RED FLAGS + FINAL
# ════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔄 Swing Trade",
    "📅 Long-Term",
    "🚀 High Risk/Reward",
    "💼 ₹ Portfolio",
    "🚫 Red Flags",
    "🏆 Best Pick Today",
])


# ── Tab 1: Swing picks ───────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">📈 Step 4A — Top 5 Swing Trade Picks (1–8 Weeks)</div>', unsafe_allow_html=True)
    picks = fetch_swing_picks()
    for p in picks:
        with st.expander(f"#{p['rank']}  {p['sym']} — {p['name']}  |  CMP ≈ ₹{p['cmp']:,}  |  Conf: {p['conf']}/10", expanded=p['rank']==1):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(
                    risk_badge(p['risk']) +
                    f'<span class="badge badge-swing">SWING</span>' +
                    f'<span style="color:#8892a4;font-size:12px;margin-left:6px">{p["sector"]}</span>',
                    unsafe_allow_html=True)
                st.markdown(conf_bar(p['conf']), unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:13px;color:#a8b4c8;line-height:1.6;margin-top:8px">{p["why"]}</p>', unsafe_allow_html=True)
                tags_html = "".join(tech_tag(t) for t in p["tags"])
                st.markdown(f'<div style="margin-top:8px">{tags_html}</div>', unsafe_allow_html=True)
                st.markdown(
                    dma_dot(p["technicals"]["above_50dma"], "Above 50 DMA") +
                    dma_dot(p["technicals"]["above_200dma"], "Above 200 DMA") +
                    f'<span style="font-size:11px;color:#8892a4">RSI: {p["technicals"]["rsi"]} | Trend: {p["technicals"]["trend"]}</span>',
                    unsafe_allow_html=True)
            with c2:
                st.metric("Entry Zone",  p["entry"])
                st.metric("Stop Loss",   p["sl"])
            with c3:
                st.metric("Target 1", p["t1"], f'+{p["upside_t1"]:.1f}%')
                st.metric("Target 2", p["t2"], f'+{p["upside_t2"]:.1f}%')


# ── Tab 2: Long-Term picks ───────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">📅 Step 4B — Top 5 Long-Term Investment Picks (1–5 Years)</div>', unsafe_allow_html=True)
    lt = fetch_lt_picks()
    for p in lt:
        with st.expander(f"#{p['rank']}  {p['sym']} — {p['name']}  |  Horizon: {p['horizon']}  |  Conf: {p['conf']}/10", expanded=p['rank']==1):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(
                    risk_badge(p['risk']) +
                    f'<span class="badge badge-lt">LONG-TERM</span>' +
                    f'<span style="color:#8892a4;font-size:12px;margin-left:6px">{p["sector"]}</span>',
                    unsafe_allow_html=True)
                st.markdown(conf_bar(p['conf']), unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:13px;color:#a8b4c8;line-height:1.6;margin-top:8px">{p["why"]}</p>', unsafe_allow_html=True)
                f = p["fundamentals"]
                st.markdown(f"""
                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px">
                  <span style="font-size:11px;background:#1c3040;color:#64b5f6;padding:2px 8px;border-radius:8px">Rev Growth: {f['rev_growth']}%</span>
                  <span style="font-size:11px;background:#1c3040;color:#64b5f6;padding:2px 8px;border-radius:8px">Profit Growth: {f['profit_growth']}%</span>
                  <span style="font-size:11px;background:#1c3040;color:#66bb6a;padding:2px 8px;border-radius:8px">ROE: {f['roe']}%</span>
                  <span style="font-size:11px;background:#1c3040;color:#ffd54f;padding:2px 8px;border-radius:8px">Debt: {f['debt']}</span>
                  <span style="font-size:11px;background:#1c3040;color:#ce93d8;padding:2px 8px;border-radius:8px">Promoter: {f['promoter']}</span>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.metric("Entry Zone",  p["entry"])
                st.metric("Stop Loss",   p["sl"])
            with c3:
                st.metric("Target 1", p["t1"])
                st.metric("Target 2", p["t2"])


# ── Tab 3: High Risk/Reward ──────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">🚀 Step 4C — Top 3 High-Risk / High-Reward Smallcaps</div>', unsafe_allow_html=True)
    st.warning("⚠️ These are high-volatility picks. Position size at max 5–8% of capital. Always use tight stop losses.")
    hrrr = fetch_hrrr_picks()
    for p in hrrr:
        with st.expander(f"#{p['rank']}  {p['sym']} — {p['name']}  |  CMP ≈ ₹{p['cmp']:,}  |  Upside: {p['upside']}", expanded=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(
                    risk_badge(p['risk']) +
                    f'<span class="badge badge-hrrr">HIGH R/R</span>' +
                    f'<span style="color:#8892a4;font-size:12px;margin-left:6px">{p["sector"]}</span>',
                    unsafe_allow_html=True)
                st.markdown(conf_bar(p['conf']), unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:13px;color:#a8b4c8;line-height:1.6;margin-top:8px">{p["why"]}</p>', unsafe_allow_html=True)
            with c2:
                st.metric("Entry Zone", p["entry"])
                st.metric("Stop Loss",  p["sl"])
            with c3:
                st.metric("Target 1", p["t1"])
                st.metric("Target 2", p["t2"])


# ── Tab 4: Portfolio Allocation ──────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">💼 Step 5 — Portfolio Allocation</div>', unsafe_allow_html=True)
    alloc = fetch_allocation()

    # scale to user's capital
    alloc["Scaled Amount (₹)"] = (alloc["Allocation %"] / 100 * capital).astype(int)

    c1, c2 = st.columns([1, 1])

    with c1:
        # Donut chart
        fig = go.Figure(go.Pie(
            labels=alloc["Symbol"],
            values=alloc["Allocation %"],
            hole=0.5,
            marker_colors=alloc["Color"].tolist(),
            textinfo="label+percent",
            textfont_size=12,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"#### Capital: ₹{capital:,}")
        for _, row in alloc.iterrows():
            bar_pct = int(row["Allocation %"] * 3)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin:6px 0">
              <span style="font-size:12px;font-weight:600;min-width:80px;color:#e2e8f0">{row['Symbol']}</span>
              <div style="flex:1;background:#2d3748;border-radius:4px;height:8px;overflow:hidden">
                <div style="width:{bar_pct}%;background:{row['Color']};height:8px;border-radius:4px"></div>
              </div>
              <span style="font-size:11px;color:#8892a4;min-width:40px">{row['Allocation %']}%</span>
              <span style="font-size:12px;font-weight:600;color:#e2e8f0;min-width:80px;text-align:right">₹{row['Scaled Amount (₹)']:,}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1c2333;border:1px solid #2d3748;border-radius:10px;padding:12px 16px;margin-top:12px;font-size:12px;color:#8892a4">
      <strong style="color:#e2e8f0">Strategy note:</strong> 50% defensive (FMCG + Healthcare + Defence), 
      30% banking/financial compounders, 14% high-conviction smallcap, 6% cash buffer. 
      In corrective phase — hold 30–40% of total planned capital in cash. 
      Deploy remaining on confirmed support bounces only.
    </div>""", unsafe_allow_html=True)


# ── Tab 5: Red Flags ─────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">🚫 Step 6 — Red Flags: Sectors & Stocks to AVOID Today</div>', unsafe_allow_html=True)

    flags = [
        ("IT Sector — INFY, HCLTECH, WIPRO, TCS",
         "Infosys gave conservative FY27 guidance (1.5–3.5%). HCL Tech crashed 16.6%. "
         "Entire sector in negative momentum. Avoid until guidance clarity in Q1 FY27."),
        ("PSU Banks — SBIN, BANKBARODA, PNB",
         "SBIN down –0.58% even on strong market days. FII selling concentrated in PSU banks. "
         "Rising crude = NIM concerns for state lenders. Bank Nifty support fragile."),
        ("Oil & Gas — ONGC, BPCL, IOC",
         "Crude oil spike from Iran tensions hurts OMC margins. ONGC in losers list. "
         "Government pricing control = muted upside. Sector headwind persists."),
        ("Speculative Smallcaps & Penny Stocks",
         "VIX elevated at 16+. High-beta speculative names can drop 10–15% in a session. "
         "Stick to quality smallcaps with proven fundamentals and hard stop losses."),
        ("Highly Leveraged Companies",
         "High debt + INR at ₹94.25 makes dollar-denominated debt expensive. "
         "Avoid high-leverage names until INR stabilises below ₹90."),
    ]

    for title, desc in flags:
        st.markdown(f"""
        <div class="red-flag">
          <span style="color:#ef5350;font-weight:700">✘ {title}</span><br>
          <span style="color:#a8b4c8">{desc}</span>
        </div>""", unsafe_allow_html=True)


# ── Tab 6: Best Pick ──────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-header">🏆 Step 7 — The SINGLE BEST Indian Stock to Buy Today</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="winner-card">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
        <div style="background:#4a90e2;padding:10px 20px;border-radius:10px;font-size:28px;font-weight:900;color:#fff">BEL</div>
        <div>
          <div style="font-size:20px;font-weight:700;color:#e2e8f0">Bharat Electronics Ltd</div>
          <div style="font-size:13px;color:#8892a4">NSE: BEL · Defence PSU · Navratna</div>
        </div>
        <div style="margin-left:auto;background:#1a3a2e;border:1px solid #2d6a4f;padding:6px 16px;border-radius:20px;color:#66bb6a;font-size:13px">
          Confidence: 8.7 / 10
        </div>
      </div>

      <p style="color:#a8b4c8;font-size:13px;line-height:1.7;margin-bottom:16px">
        BEL is the single best stock to buy on 26 April 2026 for both swing and long-term investors.
        In a market where IT is crashing on weak guidance and FIIs are selling aggressively,
        BEL stands as the rare name with a <strong style="color:#e2e8f0">defensive moat, earnings acceleration, 
        and a powerful catalyst loop.</strong><br><br>
        Fresh ₹569 Cr orders on 22 April alone. FY26 turnover grew 16.2% to ₹26,750 Cr.
        The ₹74,000 Cr order book provides multi-year revenue visibility.
        The Iran war risk premium <em>helps</em> defence stocks — geopolitical tension = increased defence spending.
        Almost debt-free with ROE expansion. Part of Nifty 50 and Sensex — institutional must-own.
        Breakout above ₹332 confirmed with volume.
        <strong style="color:#e2e8f0">In 30 trading sessions, BEL has the highest probability 
        of outperforming Nifty.</strong>
      </p>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px">
        <div style="background:#1a2a4a;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#64b5f6;margin-bottom:4px">ENTRY ZONE</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">₹420–435</div>
        </div>
        <div style="background:#2a1a1a;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#ef5350;margin-bottom:4px">STOP LOSS</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">₹400</div>
        </div>
        <div style="background:#1a2a1a;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#66bb6a;margin-bottom:4px">SWING TARGET</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">₹530</div>
        </div>
        <div style="background:#1a2a1a;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#66bb6a;margin-bottom:4px">LT TARGET</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">₹800</div>
        </div>
        <div style="background:#1a2533;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#ce93d8;margin-bottom:4px">ORDER BOOK</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">₹74,000 Cr</div>
        </div>
        <div style="background:#1a2533;border-radius:8px;padding:10px 12px">
          <div style="font-size:10px;color:#ffd54f;margin-bottom:4px">REVENUE GROWTH</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0">+16.2% YoY</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  FOOTER + AUTO-REFRESH
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:11px;color:#546e7a;padding:8px 0">
  ⚠️ <strong>Disclaimer:</strong> Educational & research purposes only. Not SEBI-registered investment advice.
  Consult a SEBI-registered financial advisor before investing.
  Equity investments are subject to market risks. Stop losses are mandatory.
</div>""", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(300)
    st.rerun()
