# app.py → ETH Scanner PRO – Upgraded 2025
import streamlit as st
from web3 import Web3
import requests
import time

# ==================== CONFIG ====================
st.set_page_config(page_title="ETH Scanner PRO", layout="wide", initial_sidebar_state="expanded")

# Fast & reliable RPCs (rotates if one fails)
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
    st.error("All RPCs down – try again later")
    st.stop()

# ==================== CACHE PRICE (5 sec) ====================
@st.cache_data(ttl=5)
def get_eth_price():
    try:
        return requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        ).json()["ethereum"]["usd"]
    except:
        return 3034.0  # fallback

eth_price = get_eth_price()

# ==================== AWESOME HEADER ====================
st.markdown("""
<style>
    .big-title {font-size: 4rem; font-weight: 900; background: linear-gradient(90deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {font-size: 1.4rem; color: #94a3b8; text-align: center;}
    .address-box {background: #1e1b4b; padding: 1.5rem; border-radius: 16px; border: 2px solid #6366f1;}
</style>
<div style="text-align:center; padding: 2rem 0;">
    <h1 class="big-title">ETH Scanner PRO</h1>
    <p class="subtitle">Live Balance • USD Value • TX Count • ENS • Gas Price • Nov 2025</p>
</div>
""", unsafe_allow_html=True)

# ==================== SCAN FUNCTION (BEAST MODE) ====================
def scan_wallet(address):
    try:
        checksum = w3.to_checksum_address(address)
    except:
        return None

    start = time.time()
    balance_wei = w3.eth.get_balance(checksum)
    tx_count = w3.eth.get_transaction_count(checksum)
    balance_eth = w3.from_wei(balance_wei, "ether")
    usd_value = balance_eth * eth_price
    gas_price = w3.from_wei(w3.eth.gas_price, "gwei")

    # ENS lookup (optional fun)
    ens_name = None
    try:
        ens_name = w3.ens.name(checksum)
    except:
        pass

    return {
        "address": checksum,
        "ens": ens_name or "—",
        "balance_eth": balance_eth,
        "balance_usd": usd_value,
        "tx_count": tx_count,
        "gas_gwei": gas_price,
        "scan_time": round(time.time() - start, 2),
        "price": eth_price
    }

# ==================== SIDEBAR INPUT ====================
with st.sidebar:
    st.image("https://i.imgur.com/ZXKQzN.png", width=100)
    st.markdown("<h2 style='color:#6366f1;'>ETH Scanner PRO</h2>", unsafe_allow_html=True)
    
    address = st.text_input(
        "Wallet Address",
        placeholder="vitalik.eth or 0xAb58...d5f6",
        help="Supports ENS names too!"
    ).strip()

    if st.button("SCAN WALLET", type="primary", use_container_width=True):
        st.session_state.address = address

# ==================== MAIN SCAN ====================
if "address" in st.session_state and st.session_state.address:
    addr = st.session_state.address

    # ENS resolve if needed
    if not addr.startswith("0x"):
        try:
            resolved = w3.ens.address(addr)
            if resolved:
                addr = resolved
                st.info(f"ENS Resolved → {resolved}")
        except:
            pass

    with st.spinner("Scanning Ethereum mainnet..."):
        result = scan_wallet(addr)

    if result:
        st.success(f"Wallet Found • Scanned in {result['scan_time']}s")

        # Big beautiful cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Balance", f"{result['balance_eth']:,.6f} ETH")
        c2.metric("USD Value", f"${result['balance_usd']:,.2f}")
        c3.metric("Transactions", f"{result['tx_count']:,}")
        c4.metric("Current Gas", f"{result['gas_gwei']:.1f} Gwei")

        st.markdown("---")
        col_a, col_b = st.columns([3,1])
        with col_a:
            st.code(result["address"], language=None)
        with col_b:
            st.markdown(f"*ENS:* {result['ens']}")

        # Fun stats
        st.caption(f"Live ETH Price: ${result['price']:,.2f} • RPC: {w3.client_version}")

    else:
        st.error("Invalid address or RPC timeout")

else:
    st.info("Enter an Ethereum address or ENS name in the sidebar →")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Upgraded Nov 2025 • 4 RPC fallback • ENS • Gas • Lightning fast</p>", unsafe_allow_html=True)
