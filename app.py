# app.py - Karm Tiger v0.3 — Beast Mode (No SDK)
import streamlit as st
import numpy as np
import yfinance as yf
import requests
import pandas as pd
from web3 import Web3
import ccxt

# === CONFIG ===
st.set_page_config(page_title="Karm Tiger v0.3", page_icon="🐅", layout="wide")
st.title("🐅 Karm Tiger Deep Tech Investment Dashboard v0.3")
st.markdown("**Beast Mode**: Live Perplexity • Grok X Sentiment • Multi-Ticker • Blockchain • Futures Prep")

# === SIDEBAR ===
with st.sidebar:
    st.header("🔑 API Keys")
    perplexity_key = st.text_input("Perplexity API Key", type="password")
    xai_key = st.text_input("xAI Grok API Key", type="password", help="https://x.ai/api")
    eth_rpc = st.text_input("Ethereum RPC", value="https://sepolia.infura.io/v3/YOUR_INFURA_KEY")
    eth_private_key = st.text_input("ETH Private Key", type="password")

    st.header("🛠️ Mode")
    use_mock = st.checkbox("Mock Mode (No APIs)", value=True)
    enable_blockchain = st.checkbox("Enable Blockchain Log", value=False)

# === MULTI-TICKER WATCHLIST ===
st.subheader("📊 Multi-Ticker Watchlist")
watchlist = st.multiselect("Add Tickers", ["MP", "NVDA", "IONQ", "QUBT"], default=["MP"])
period = st.selectbox("Price History", ["1mo", "3mo", "6mo", "1y"], index=0)

if st.button("Run Inference + Crunch", type="primary"):
    with st.spinner("Fetching data + running analysis..."):
        try:
            # === REAL PRICE DATA ===
            data = {}
            for ticker in watchlist:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
                if not hist.empty:
                    prices = hist['Close'].values
                    returns = np.diff(np.log(prices))
                    vol = np.std(returns) * np.sqrt(252) * 100 if len(returns) > 1 else 0
                    momentum = (prices[-1] / prices[0] - 1) * 100
                    data[ticker] = {'prices': prices, 'hist': hist, 'vol': vol, 'momentum': momentum, 'current': prices[-1]}

            # Metrics Table
            metrics_df = pd.DataFrame({
                'Ticker': list(data.keys()),
                'Price': [f"${d['current']:.2f}" for d in data.values()],
                'Vol': [f"{d['vol']:.1f}%" for d in data.values()],
                f"{period.upper()} Return": [f"{d['momentum']:+.1f}%" for d in data.values()]
            })
            st.dataframe(metrics_df, use_container_width=True)

            # Charts
            for ticker, d in data.items():
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(ticker, f"${d['current']:.2f}", f"{d['momentum']:+.1f}%")
                with col2:
                    st.line_chart(d['hist']['Close'], use_container_width=True)

            # === PERPLEXITY LIVE (raw requests) ===
            if not use_mock and perplexity_key:
                st.subheader("🔮 Perplexity AI Insights")
                for ticker in watchlist:
                    try:
                        url = "https://api.perplexity.ai/chat/completions"
                        payload = {
                            "model": "llama-3.1-sonar-small-128k-online",
                            "messages": [{"role": "user", "content": f"Analyze {ticker}: earnings, valuation, risks, 6-month outlook. Be concise."}],
                            "temperature": 0.3
                        }
                        headers = {"Authorization": f"Bearer {perplexity_key}", "Content-Type": "application/json"}
                        r = requests.post(url, json=payload, headers=headers, timeout=30)
                        if r.status_code == 200:
                            st.write(f"**{ticker}**: {r.json()['choices'][0]['message']['content']}")
                        else:
                            st.error(f"Perplexity Error for {ticker}: {r.status_code}")
                    except Exception as e:
                        st.error(f"Perplexity Error for {ticker}: {str(e)}")
            else:
                st.subheader("🔮 Mock AI")
                for t in watchlist:
                    st.info(f"**{t}**: Strong buy — DoD deal + AI demand. (Mock)")

            # === GROK X SENTIMENT (raw requests) ===
            if not use_mock and xai_key:
                st.subheader("🚀 Grok X Sentiment")
                for ticker in watchlist:
                    try:
                        url = "https://api.x.ai/v1/chat/completions"
                        payload = {"model": "grok-beta", "messages": [{"role": "user", "content": f"X sentiment on {ticker}: score 1-10, key themes."}]}
                        headers = {"Authorization": f"Bearer {xai_key}", "Content-Type": "application/json"}
                        r = requests.post(url, json=payload, headers=headers)
                        if r.status_code == 200:
                            st.write(f"**{ticker}**: {r.json()['choices'][0]['message']['content']}")
                    except Exception as e:
                        st.warning(f"Grok Error for {ticker}: {str(e)}")
            else:
                st.subheader("🚀 Mock X Sentiment")
                for t in watchlist:
                    st.info(f"**{t}**: 8/10 bullish — X buzzing. (Mock)")

            # === BLOCKCHAIN LOG ===
            if enable_blockchain and eth_rpc and eth_private_key:
                st.subheader("🔗 Blockchain Trade Log")
                w3 = Web3(Web3.HTTPProvider(eth_rpc))
                if w3.is_connected():
                    acc = w3.eth.account.from_key(eth_private_key)
                    st.write(f"Wallet: {acc.address[:8]}...")
                    if st.button("Log Test Trade"):
                        tx = {'to': acc.address, 'value': w3.to_wei(0.001, 'ether'), 'gas': 21000, 'gasPrice': w3.to_wei('50', 'gwei'), 'nonce': w3.eth.get_transaction_count(acc.address)}
                        signed = w3.eth.account.sign_transaction(tx, eth_private_key)
                        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                        st.success(f"Logged! TX: {tx_hash.hex()}")
                else:
                    st.error("RPC failed")
            else:
                st.subheader("🔗 Mock Blockchain")
                st.info("Trade logged: 0xmock123...")

            # === FUTURES & SAMURIA STUB ===
            st.subheader("📈 Futures & Samuria Scan")
            futures = st.selectbox("Futures", ["ES=F", "NQ=F"])
            try:
                ex = ccxt.binance()
                price = ex.fetch_ticker(futures)['last']
                st.metric("Futures", f"${price:.2f}")
                st.info("Samuria: Bull Call if vol < 25% (v0.5)")
            except:
                st.info("Futures loading...")

            # === EXPORT ===
            for t in watchlist:
                if t in data:
                    csv = data[t]['hist'][['Close']].reset_index().to_csv(index=False)
                    st.download_button(f"Export {t}", csv, f"{t}_{period}.csv")

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Add tickers → Click **Run Inference + Crunch**")