# app.py - Karm Tiger Deep Tech Dashboard v0.2
# → Real MP prices | Toggle Mock/Real | Deploy-Ready
import streamlit as st
import numpy as np
import yfinance as yf
import requests
import json
from datetime import datetime

# === CONFIG ===
st.set_page_config(page_title="Karm Tiger v0.2", page_icon="Tiger", layout="wide")
st.title("Tiger Karm Tiger Deep Tech Investment Dashboard")
st.markdown("**v0.2** — Real prices • NumPy alpha • Perplexity toggle • Deploy-ready")

# === SIDEBAR ===
with st.sidebar:
    st.header("Mode")
    use_mock = st.checkbox("Mock Mode (No API Key)", value=True)
    
    if not use_mock:
        perplexity_key = st.text_input("Perplexity API Key", type="password")
        model = st.selectbox("Model", ["llama-3.1-sonar-small-128k-online", "sonar-small-online"])
    else:
        perplexity_key = None
        model = "llama-3.1-sonar-small-128k-online"
        st.success("Mock Mode Active — No API Key Needed")

    st.divider()
    st.caption("Built with Grok • Perplexity • yfinance • Streamlit")

# === INPUT ===
ticker = st.text_input("Deep Tech Ticker", value="MP", help="e.g., MP, NVDA, IONQ")
period = st.selectbox("Price History", ["1mo", "3mo", "6mo", "1y"], index=0)

if st.button("Run Inference + Crunch", type="primary"):
    with st.spinner("Fetching real data + running inference..."):
        try:
            # === REAL PRICE DATA (yfinance) ===
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                st.error(f"No data for {ticker}. Check ticker.")
            else:
                prices = hist['Close'].values
                dates = hist.index.strftime('%Y-%m-%d')

                # === NUMPY RISK ENGINE ===
                returns = np.diff(np.log(prices))
                vol = np.std(returns) * np.sqrt(252) * 100 if len(returns) > 1 else 0
                momentum = (prices[-1] / prices[0] - 1) * 100

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"${prices[-1]:.2f}")
                col2.metric("Volatility (Ann.)", f"{vol:.1f}%")
                col3.metric(f"{period.upper()} Return", f"{momentum:+.1f}%")
                col4.metric("Days", len(prices))

                st.line_chart(hist['Close'], use_container_width=True)

                # === INFERENCE: MOCK OR REAL ===
                if use_mock:
                    st.subheader("Inferred Deep Tech Insights (Mock)")
                    mock_insight = f"""
                    **{ticker.upper()} Analysis (Simulated)**  
                    • Latest: Q2 revenue up 84% YoY  
                    • NdPr production: +119%  
                    • DoD 10-year deal: $110/kg locked  
                    • Valuation: Trading at ${prices[-1]:.2f} vs target $68.73  
                    • Outlook: Geopolitical tailwinds strong  
                    _Source: Karm Tiger AI (mock mode)_
                    """
                    st.write(mock_insight)
                else:
                    if not perplexity_key:
                        st.error("API key required in real mode.")
                    else:
                        try:
                            url = "https://api.perplexity.ai/chat/completions"
                            payload = {
                                "model": model,
                                "messages": [
                                    {"role": "user", "content": f"Analyze {ticker}: latest earnings, valuation, macro risks, AI/blockchain relevance, 6-month outlook. Be concise, cite sources."}
                                ],
                                "temperature": 0.3
                            }
                            headers = {
                                "Authorization": f"Bearer {perplexity_key}",
                                "Content-Type": "application/json"
                            }
                            response = requests.post(url, json=payload, headers=headers, timeout=30)
                            response.raise_for_status()
                            data = response.json()
                            insights = data['choices'][0]['message']['content']
                            st.subheader("Inferred Deep Tech Insights (Live)")
                            st.write(insights)
                        except Exception as e:
                            st.error(f"Perplexity API Error: {str(e)}")
                            st.info("Switch to Mock Mode to continue.")

                # === EXPORT ===
                export_df = hist[['Close']].reset_index()
                export_df.columns = ['Date', 'Price']
                csv = export_df.to_csv(index=False)
                st.download_button("Export Price Data", csv, f"{ticker}_{period}_karmtiger.csv", "text/csv")

                # === xAI SENTIMENT PLACEHOLDER ===
                st.subheader("xAI / Grok Sentiment Pulse")
                st.info(f"Grok detects **high conviction** in {ticker} — structural tailwinds intact. [Live API coming soon]")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

else:
    st.info("Enter ticker → Select period → Click **Run Inference + Crunch**")
    st.caption("Mock Mode = instant results. Real Mode = live AI insights.")