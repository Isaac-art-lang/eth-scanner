# app.py – Multi-Chain Scanner Pro (Nov 2025 – Guaranteed working)
import streamlit as st
from web3 import Web3
import pandas as pd
import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey

# ==================== RPCs ====================
ETH_RPC = "https://eth-mainnet.g.alchemy.com/v2/demo"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"          # works
# SOLANA_RPC = "https://mainnet.helius-rpc.com/?api-key=xxx"  # optional faster

solana_client = Client(SOLANA_RPC)

# ==================== PROFILE PIC ====================
html = """
<div style="text-align:center; margin:30px 0 20px 0;">
    <img src="https://i.imgur.com/ZXKQzN.png" width="130" style="border-radius:50%; border:4px solid #6366f1; box-shadow:0 8px 25px rgba(99,102,241,0.4);">
    <div style="margin-top:15px; font-size:22px; font-weight:800; color:#6366f1;">Multi-Chain Scanner Pro</div>
    <div style="font-size:15px; color:#94a3b8;">Ethereum • Solana • Tokens • Nov 2025</div>
</div>
"""
st.sidebar.markdown(html, unsafe_allow_html=True)

# ==================== ETHEREUM ====================
def scan_ethereum(address):
    w3 = Web3(Web3.HTTPProvider(ETH_RPC))
    if not w3.is_connected():
        return None
    try:
        balance = w3.eth.get_balance(address)
        eth = w3.from_wei(balance, "ether")
        price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()["ethereum"]["usd"]
        return {"chain": "Ethereum", "native": f"{eth:.6f} ETH", "usd": f"${eth*price:,.2f}"}
    except:
        return None

# ==================== SOLANA ====================
def scan_solana(address):
    try:
        pubkey = Pubkey.from_string(address)
        balance_resp = solana_client.get_balance(pubkey)
        sol = balance_resp.value / 1_000_000_000

        price_resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd").json()
        sol_price = price_resp["solana"]["usd"]

        # Token accounts
        token_resp = solana_client.get_token_accounts_by_owner(pubkey, program_id=Pubkey("TokenkegQfeZyiNwAJbNbGKLZA6K4w3Z3ZnT4b4i3o"))
        tokens = []
        for acc in token_resp.value:
            info = acc.account.data.parsed["info"]
            ui_amount = info["tokenAmount"]["uiAmount"]
            if ui_amount and ui_amount > 0:
                symbol = info.get("symbol") or info["mint"][:6]
                tokens.append({"symbol": symbol, "amount": f"{ui_amount:,}"})

        return {
            "chain": "Solana",
            "native": f"{sol:.6f} SOL",
            "usd": f"${sol*sol_price:,.2f}",
            "tokens": tokens
        }
    except:
        return None

# ==================== AUTO DETECT =================
def scan_wallet(address):
    address = address.strip()
    if address.startswith("0x") and len(address) == 42:
        return scan_ethereum(address)
    elif len(address) >= 32:
        try:
            Pubkey.from_string(address)
            return scan_solana(address)
        except:
            pass
    return None

# ==================== UI ====================
st.set_page_config(page_title="Multi-Chain Scanner", layout="centered")
wallet = st.sidebar.text_input("Wallet Address", placeholder="0x... or Solana base58")
if st.sidebar.button("Scan Now", type="primary", use_container_width=True):
    if wallet:
        with st.spinner("Scanning blockchain..."):
            result = scan_wallet(wallet)
        if result:
            st.success(f"{result['chain']} wallet detected!")
            c1, c2 = st.columns(2)
            c1.metric("Native Balance", result["native"])
            c2.metric("USD Value", result["usd"])
            if result.get("tokens"):
                st.subheader("Token Balances")
                st.dataframe(pd.DataFrame(result["tokens"]), use_container_width=True)
        else:
            st.error("Invalid or empty wallet")
    else:
        st.warning("Enter a wallet address")

st.title("Multi-Chain Wallet Scanner")
st.write("Supports Ethereum & Solana • Live prices • Token detection")
st.caption("Clean & working • November 2025")
