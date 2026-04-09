import streamlit as st
import pandas as pd
import json
from web3 import Web3

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Adaptive PQ Blockchain Dashboard",
    layout="wide"
)

st.title("Adaptive Post-Quantum Blockchain Dashboard")
st.caption(
    "Real-time monitoring of transaction processing, "
    "PQC scheme usage, verification latency, and on-chain logs."
)

# ----------------------------
# LOAD METRICS CSV
# ----------------------------
df = pd.read_csv("logs/metrics.csv")

# ----------------------------
# CONNECT TO BLOCKCHAIN
# ----------------------------
w3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:8545")
)

with open(
    "artifacts/contracts/PQRegistry.sol/PQRegistry.json",
    "r"
) as f:
    contract_json = json.load(f)

abi = contract_json["abi"]

contract = w3.eth.contract(
    address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
    abi=abi
)

onchain_count = contract.functions.getCount().call()

# ----------------------------
# TOP METRICS
# ----------------------------
st.subheader("System Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Transactions",
    len(df)
)

col2.metric(
    "On-chain Logs",
    onchain_count
)

col3.metric(
    "Avg Verify Latency",
    f"{df['verify_latency'].mean():.5f}s"
)

st.markdown("---")

# ----------------------------
# SCHEME USAGE
# ----------------------------
st.subheader("PQC Scheme Usage")

st.write(
    "This graph shows how frequently each post-quantum "
    "signature scheme was selected by the adaptive middleware. "
    "It helps explain the system's decision-making behavior "
    "under different threat and network conditions."
)

scheme_counts = df["scheme"].value_counts()

st.bar_chart(scheme_counts)

st.markdown("---")

# ----------------------------
# LATENCY TREND
# ----------------------------
st.subheader("Verification Latency Trend")

st.write(
    "This line graph shows how signature verification latency "
    "changes across transactions. Lower latency indicates "
    "faster verification performance."
)

st.line_chart(df["verify_latency"])

st.markdown("---")

# ----------------------------
# RECENT TRANSACTIONS
# ----------------------------
st.subheader("Recent Transactions")

st.write(
    "The table below displays the latest processed transactions "
    "along with their selected scheme, threat score, "
    "and latency metrics."
)

st.dataframe(
    df.tail(10),
    use_container_width=True
)

st.markdown("---")

# ----------------------------
# FOOTER SUMMARY
# ----------------------------
st.info(
    "The adaptive middleware dynamically selects the most "
    "suitable PQC scheme based on transaction urgency, "
    "threat score, and network state. "
    "All verified transactions are logged on-chain."
)