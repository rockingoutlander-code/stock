# 📈 India Daily Invest Dashboard

AI-powered algorithmic equity research dashboard for NSE/BSE stocks.
Auto-updates every 5 minutes with fresh technical + fundamental analysis.

---

## 🚀 DEPLOY IN 5 MINUTES — Get a Shareable Live Link

### Option A — Streamlit Cloud (FREE, easiest, shareable URL)

1. **Fork / upload to GitHub**
   ```
   git init
   git add .
   git commit -m "India Invest Dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/india-dashboard.git
   git push -u origin main
   ```

2. **Go to** https://share.streamlit.io

3. **Click** → "New app" → connect your GitHub repo → select `app.py`

4. **Click Deploy** → You get a live URL like:
   ```
   https://YOUR_USERNAME-india-dashboard-app-xxxx.streamlit.app
   ```

5. **Share that link** — anyone can open it, it auto-refreshes every 5 min!

---

### Option B — Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run app.py

# 3. Opens at http://localhost:8501
```

---

### Option C — Deploy on Render (Free hosting, always-on)

1. Create account at https://render.com
2. New → Web Service → connect GitHub repo
3. Build command:  `pip install -r requirements.txt`
4. Start command:  `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. You get a permanent URL like `https://india-dashboard.onrender.com`

---

## 🔌 Enable Live NSE/BSE Data

The dashboard works in **demo mode** by default (curated research data).
To get real-time prices, pick one:

### Option 1 — Yahoo Finance (FREE, no signup, 15-min delay)
Already configured! Just set in `utils/data_fetcher.py`:
```python
PROVIDER = "yahoo"
```

### Option 2 — Zerodha Kite API (Real-time, free for Zerodha customers)
```python
PROVIDER = "zerodha"
```
Steps:
1. Open Zerodha Kite account at https://zerodha.com
2. Create API app at https://kite.trade (₹2,000/year)
3. Set environment variables:
   ```
   ZERODHA_API_KEY=your_key
   ZERODHA_ACCESS_TOKEN=your_token
   ```
4. On Streamlit Cloud: Settings → Secrets → paste your keys

### Option 3 — Upstox API (Real-time, free for Upstox customers)
```python
PROVIDER = "upstox"
```
Steps:
1. Open Upstox account at https://upstox.com
2. Create app at https://developer.upstox.com
3. Set:
   ```
   UPSTOX_API_KEY=your_key
   ```

### Option 4 — Alpha Vantage (Free key, 15-min delay)
```python
PROVIDER = "alphavantage"
```
Free API key at https://www.alphavantage.co/support/#api-key
```
ALPHAVANTAGE_KEY=your_key
```

---

## 📁 Project Structure

```
india_dashboard/
├── app.py                    ← Main Streamlit dashboard (run this)
├── requirements.txt          ← Python dependencies
├── .streamlit/
│   └── config.toml           ← Dark theme + server settings
└── utils/
    ├── data_fetcher.py       ← Live NSE/BSE data (Yahoo/Zerodha/Upstox)
    └── screener.py           ← Algorithmic stock screener engine
```

---

## 🔄 How Auto-Update Works

- `st.cache_data(ttl=300)` — all data functions cache for 5 minutes
- After 5 min, next visitor triggers a fresh fetch from the API
- The auto-refresh checkbox in sidebar triggers `st.rerun()` every 5 min
- For true server-side scheduling, add APScheduler or a cron job

---

## ⚙️ Customise the Algorithm

Edit `utils/screener.py` to change thresholds:

```python
THRESHOLDS = {
    "rev_growth_min":    10.0,   # minimum revenue growth %
    "profit_growth_min": 10.0,   # minimum profit growth %
    "roe_min":           12.0,   # minimum ROE %
    "rsi_min":           35,     # RSI lower bound
    "rsi_max":           75,     # RSI upper bound
}
```

Add your own universe of stocks in `FUNDAMENTAL_DB` inside `screener.py`.

---

## ⚠️ Disclaimer

This dashboard is for **educational and research purposes only**.
It is **NOT** SEBI-registered investment advice.
Consult a SEBI-registered financial advisor before investing.
Equity investments are subject to market risks.
Stop losses are mandatory.
