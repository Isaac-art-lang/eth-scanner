# app.py → Galaxy Scanner – Official Final Version (2025)
import streamlit as st
from web3 import Web3
import requests
import time

# ==================== CONFIG ====================
st.set_page_config(page_title="Galaxy Scanner", layout="wide", initial_sidebar_state="expanded")

# Reliable RPCs with fallback
RPCS = [
    "https://eth-mainnet.g.alchemy.com/v2/demo",
    "https://ethereum.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://eth.llamarpc.com"
]
w3 = None
for rpc in RPCS:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
        if w3.is_connected():
            break
    except:
        continue
if not w3 or not w3.is_connected():
    st.error("No Ethereum node connection – try again later")
    st.stop()

# ==================== PRICE CACHE ====================
@st.cache_data(ttl=5)
def get_eth_price():
    try:
        return requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()["ethereum"]["usd"]
    except:
        return 3050.0

eth_price = get_eth_price()

# ==================== GALAXY HEADER ====================
st.markdown("""
<style>
    .title-font {font-size: 4.5rem; font-weight: 900; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {font-size: 1.5rem; color: #94a3b8; text-align: center; margin-top: -20px;}
</style>

<div style="text-align:center; padding: 30px 0;">
    <img src="https://raw.githubusercontent.com/""" + st.secrets.get("GITHUB_REPO", "YOUR-USERNAME/YOUR-REPO") + """/main/logo.png" width="180">
    <h1 class="title-font">Galaxy Scanner</h1>
    <p class="subtitle">Ethereum Wallet Explorer • ENS • Balance • TXs • Live Data</p>
</div>
""", unsafe_allow_html=True)

# ==================== SCAN FUNCTION ====================
def scan_wallet(address):
    try:
        addr = w3.to_checksum_address(address)
    except:
        return None

    start = time.time()
    balance_wei = w3.eth.get_balance(addr)
    tx_count = w3.eth.get_transaction_count(addr)
    balance_eth = w3.from_wei(balance_wei, "ether")
    usd_value = balance_eth * eth_price
    gas = w3.from_wei(w3.eth.gas_price, "gwei")

    ens = None
    try:
        ens = w3.ens.name(addr)
    except:
        pass

    return {
        "address": addr,
        "ens": ens or "—",
        "balance_eth": balance_eth,
        "usd": usd_value,
        "txs": tx_count,
        "gas": gas,
        "time": round(time.time() - start, 2),
        "price": eth_price
    }

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("logo.png", width=120)
    st.markdown("<h2 style='text-align:center; color:#8b5cf6;'>Galaxy Scanner</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    address = st.text_input(
        "Enter Address or ENS",
        placeholder="vitalik.eth",
        help="Supports 0x... and .eth names"
    ).strip()

    if st.button("SCAN GALAXY", type="primary", use_container_width=True):
        st.session_state.address = address

# ==================== MAIN DISPLAY ====================
if "address" in st.session_state and st.session_state.address:
    input_addr = st.session_state.address

    # Resolve ENS if needed
    if not input_addr.startswith("0x"):
        try:
            resolved = w3.ens.address(input_addr)
            if resolved:
                input_addr = resolved
                st.info(f"Resolved ENS → {resolved}")
        except:
            pass

    with st.spinner("Exploring the galaxy..."):
        result = scan_wallet(input_addr)

    if result:
        st.success(f"Star System Located • Scanned in {result['time']}s")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ETH Balance", f"{result['balance_eth']:,.6f}")
        c2.metric("USD Value", f"${result['usd']:,.2f}")
        c3.metric("Transactions", f"{result['txs']:,}")
        c4.metric("Gas Price", f"{result['gas']:.1f} Gwei")

        st.markdown("---")
        col1, col2 = st.columns([3,1])
        col1.code(result["address"])
        col2.markdown(f"*ENS Name*<br>{result['ens']}", unsafe_allow_html=True)

        st.caption(f"Live ETH Price: ${result['price']:,.2f} • Connected via {w3.client_version.split('/')[0]}")

    else:
        st.error("Invalid address – no life detected")

else:
    st.info("Enter an Ethereum address or ENS name to begin exploration")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Galaxy Scanner • 2025 • Made with cosmic energy</p>", unsafe_allow_html=True)
