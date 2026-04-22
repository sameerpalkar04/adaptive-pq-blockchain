import streamlit as st
import sys
import os
import glob  
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from simulations.runner import ResearchSimulator
from blockchain_core.onchain_logger import OnChainLogger
from blockchain_core.runtime import BlockchainRuntime

st.set_page_config(page_title="PQC Adaptive Dashboard", layout="wide")

st.sidebar.header("Simulation Settings")

sim_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Simulated Data", "Live Blockchain Data"],
    help="Simulated generates mock transactions. Live fetches real-time metadata from the Ethereum mainnet/testnet via RPC."
)
is_live = sim_mode == "Live Blockchain Data"

total_tx = st.sidebar.slider("Research Scale (Transactions)", 50, 500, 2000, step=150)

st.sidebar.divider()
run_all = st.sidebar.button("Run Full Simulation", use_container_width=True)

st.title("Post-Quantum Adaptive Middleware Dashboard")
st.markdown(f"### Research Framework | Mode: **{sim_mode}**")

if run_all:
    with st.status(f"Processing {total_tx} Transactions...", expanded=True) as status:
        rpc = "https://eth.llamarpc.com" if is_live else "http://127.0.0.1:8545"
        
        # Pass the RPC to the logger so it looks in the right place!
        logger = OnChainLogger(provider_url=rpc) 
        runtime = BlockchainRuntime(rpc_url=rpc)
        
        st.write(f"Executing Adaptive Middleware (Live={is_live})...")
        runtime.run(num_tx=total_tx, live_mode=is_live) 
        
        sim = ResearchSimulator()
        
        st.write("Phase 1: Generating Quantum Vulnerability Baselines")
        sim.run_simulation_1()
        
        st.write("Phase 2: Syncing Behavioral Logic Plots")
        sim.run_simulation_2() 
        
        st.write("Phase 3: Calculating Economic Impact")
        sim.run_simulation_3() 
        
        status.update(label=f"{sim_mode} Simulation Complete!", state="complete")

tab1, tab2, tab3, tab4 = st.tabs([
    "Quantum Analysis", 
    "Behavioral Logic", 
    "Economic Impact",
    "On-Chain Audit"
])

def render_sim_plots(sim_folder):
    path = os.path.join(project_root, "evaluation", "plots", sim_folder, "*.png")
    files = glob.glob(path)
    if not files:
        st.info(f"No plots found for {sim_folder}. Run simulation to generate data.")
        return
    cols = st.columns(2)
    for idx, f_path in enumerate(sorted(files)):
        with cols[idx % 2]:
            st.image(f_path, use_container_width=True, caption=os.path.basename(f_path))

with tab1:
    st.header("Sim 1: Quantum Vulnerability Analysis")
    render_sim_plots("sim1")

with tab2:
    st.header("Sim 2: Behavioral Adaptability")
    metrics_path = os.path.join(project_root, "logs", "metrics.csv")
    if os.path.exists(metrics_path):
        st.subheader("Latest Transaction Audit")
        df_metrics = pd.read_csv(metrics_path)
        st.dataframe(
            df_metrics,
            use_container_width=True,
            column_config={
                "threat": st.column_config.ProgressColumn(
                    "Threat Score", min_value=0, max_value=1, format="%.4f"
                ),
                "lane": "Selected Algorithm",
                "threat_level": "Category"
            }
        )
    st.divider()
    render_sim_plots("sim2")

with tab3:
    st.header("Sim 3: Gas & Energy Economics")
    render_sim_plots("sim3")
    
with tab4:
    st.header("PQRegistry On-Chain Audit")
    
    current_rpc = "https://eth.llamarpc.com" if is_live else "http://127.0.0.1:8545"
    logger = OnChainLogger(provider_url=current_rpc)

    if logger.w3.is_connected():
        st.success(f"Connected to {sim_mode} | Registry: `{logger.contract_address}`")
    else:
        st.error(f"Cannot connect to {sim_mode}. Ensure your node/RPC is active.")

    if st.button("Sync with Blockchain", use_container_width=True):
        with st.spinner(f"Fetching logs from {sim_mode}..."):
            raw_logs = logger.get_all_logs(is_live=is_live)
            
            if raw_logs:
                st.dataframe(pd.DataFrame(raw_logs), use_container_width=True)
            else:
                st.warning(f"No on-chain logs found on {sim_mode}.")