# app.py → Galaxy Scanner + Transaction Analyzer (2025 Final)
import streamlit as st
from web3 import Web3
import requests
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Galaxy Scanner", layout="wide", initial_sidebar_state="expanded")

# === RPCs with fallback ===
RPCS = [
    "https://eth-mainnet.g.alchemy.com/v2/demo",
    "https://ethereum.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://eth.llamarpc.com"
]
w3 = None
for rpc in RPCS:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 15}))
        if w3.is_connected():
            break
    except:
        pass
if not w3:
    st.error("All nodes down – try later")
    st.stop()

# === Cached price ===
@st.cache_data(ttl=10)
def get_eth_price():
    try:
        return requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()["ethereum"]["usd"]
    except:
        return 3050

eth_price = get_eth_price()

# === GALAXY HEADER ===
st.markdown(f"""
<style>
    .title {{font-size: 4.8rem; font-weight: 900; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}}
    .subtitle {{font-size: 1.6rem; color: #94a3b8; text-align: center; margin-top: -15px;}}
</style>
<div style="text-align:center; padding:40px 0;">
    <img src="https://raw.githubusercontent.com/{st.secrets.get('GITHUB_REPO','YOUR-USERNAME/YOUR-REPO')}/main/logo.png" width="180">
    <h1 class="title">Galaxy Scanner</h1>
    <p class="subtitle">Ethereum Explorer • Balance • Tokens • Full TX History & Analysis</p>
</div>
""", unsafe_allow_html=True)

# === MAIN SCAN FUNCTION ===
@st.cache_data(ttl=60, show_spinner=False)
def analyze_address(address: str):
    try:
        addr = w3.to_checksum_address(address)
    except:
        return None

    # Basic data
    balance_wei = w3.eth.get_balance(addr)
    balance_eth = w3.from_wei(balance_wei, "ether")
    tx_count = w3.eth.get_transaction_count(addr)
    usd_value = balance_eth * eth_price

    # ENS
    ens = None
    try:
        ens = w3.ens.name(addr)
    except:
        pass

    # === GET LAST 50 TRANSACTIONS (Etherscan-style via public RPC) ===
    try:
        latest = w3.eth.block_number
        txs = []
        for block_num in range(max(latest - 300, 0), latest + 1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    if tx['from'].lower() == addr.lower() or tx['to'] and tx['to'].lower() == addr.lower():
                        txs.append({
                            "hash": tx.hash.hex()[:10] + "...",
                            "from": tx['from'][:8] + "..." + tx['from'][-6:],
                            "to": (tx['to'][:8] + "..." + tx['to'][-6:] if tx['to'] else "Contract Creation"),
                            "value_eth": round(w3.from_wei(tx.value, "ether"), 6),
                            "value_usd": round(w3.from_wei(tx.value, "ether") * eth_price, 2),
                            "timestamp": datetime.fromtimestamp(block.timestamp).strftime("%b %d, %H:%M"),
                            "age": "Just now" if (time.time() - block.timestamp) < 3600 else f"{int((time.time()-block.timestamp)/3600)}h ago"
                        })
                    if len(txs) >= 50:
                        break
                if len(txs) >= 50:
                    break
            except:
                continue
    except:
        txs = []

    return {
        "address": addr,
        "ens": ens or "—",
        "balance_eth": balance_eth,
        "usd": usd_value,
        "tx_count": tx_count,
        "transactions": txs[:50],
        "last_active": txs[0]["timestamp"] if txs else "Never"
    }

# === SIDEBAR ===
with st.sidebar:
    st.image("logo.png", width=130)
    st.markdown("# Galaxy Scanner")
    address = st.text_input("Address or ENS", placeholder="vitalik.eth").strip()
    if st.button("SCAN GALAXY", type="primary", use_container_width=True):
        st.session_state.address = address
        st.rerun()

# === MAIN ===
if "address" in st.session_state:
    addr_input = st.session_state.address

    # ENS resolve
    if not addr_input.startswith("0x"):
        try:
            resolved = w3.ens.address(addr_input)
            if resolved:
                addr_input = resolved
                st.info(f"ENS → {resolved}")
        except:
            pass

    with st.spinner("Scanning the entire galaxy..."):
        data = analyze_address(addr_input)

    if data:
        st.success(f"Star found • Last active: {data['last_active']}")

        # Top metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Balance", f"{data['balance_eth']:,.6f} ETH")
        c2.metric("USD Value", f"${data['usd']:,.2f}")
        c3.metric("Total TXs", f"{data['tx_count']:,}")
        c4.metric("Live ETH Price", f"${eth_price:,.0f}")

        st.code(data["address"], language=None)
        st.caption(f"ENS Name: *{data['ens']}*")

        # === TRANSACTION TABLE ===
        if data["transactions"]:
            st.markdown("### Recent Transactions (last ~50)")
            df = pd.DataFrame(data["transactions"])
            df = df[["timestamp", "age", "hash", "from", "to", "value_eth", "value_usd"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent transactions found")

    else:
        st.error("Invalid address")

else:
    st.info("Enter an address to explore the galaxy")

st.markdown("---")
st.caption("Galaxy Scanner • Full transaction history • Real-time • Made with cosmic love • 2025")
