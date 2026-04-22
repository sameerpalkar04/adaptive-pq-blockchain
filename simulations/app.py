import streamlit as st
import sys
import os
import glob  
import pandas as pd

# --- 1. STRICT PATH INJECTION ---
# Ensures the middleware and blockchain modules are discoverable
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports from your project structure
from simulations.runner import ResearchSimulator
from blockchain_core.onchain_logger import OnChainLogger
from blockchain_core.runtime import BlockchainRuntime

# App Configuration
st.set_page_config(page_title="PQC Adaptive Dashboard", layout="wide")

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Parameters")
# Single slider for all logic (100 to 5000 range)
total_tx = st.sidebar.slider("Research Scale (Transactions)", 100, 5000, 2000, step=100)

st.sidebar.divider()
run_all = st.sidebar.button("🚀 Run Full Simulation", use_container_width=True)

# --- 3. EXECUTION ENGINE ---
st.title("Post-Quantum Adaptive Middleware Dashboard")
st.markdown("### Research Framework for Post-Quantum Blockchain Security")

if run_all:
    with st.status(f"Simulating {total_tx} Transactions...", expanded=True) as status:
        # 1. Initialize the Blockchain Runtime (The "Logging" part)
        st.write(f"🔗 Connecting to PQRegistry & Logging {total_tx} Transactions...")
        runtime = BlockchainRuntime()
        
        # This will now print the "Logged to Block" messages in your terminal/IDE
        runtime.run(total_tx) 
        
        # 2. Proceed with Simulations
        sim = ResearchSimulator()
        
        st.write("Phase 1: Theoretical Analysis...")
        sim.run_simulation_1()
        
        st.write(f"Phase 2: Behavioral Logic (N={total_tx})...")
        logic_logs = sim.run_simulation_2(num_tx=total_tx)
        st.session_state['logic_logs'] = logic_logs 
        
        st.write(f"Phase 3: Economic Impact (N={total_tx})...")
        sim.run_simulation_3(num_tx=total_tx)
        
        status.update(label="All Tasks & Logging Complete!", state="complete")
    st.balloons()

# --- 4. PRESENTATION LAYER ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Quantum Analysis", 
    "Behavioral Logic", 
    "Economic Impact",
    "On-Chain Audit"
])

def render_sim_plots(sim_folder):
    """Helper to render generated plots from the evaluation folder."""
    path = os.path.join(project_root, "evaluation", "plots", sim_folder, "*.png")
    files = glob.glob(path)
    if not files:
        st.info(f"No plots found for {sim_folder}. Run the simulation to generate research data.")
        return
    cols = st.columns(2)
    for idx, f_path in enumerate(sorted(files)):
        with cols[idx % 2]:
            st.image(f_path, use_container_width=True, caption=os.path.basename(f_path))

with tab1:
    st.header("Sim 1: Quantum Vulnerability Analysis")
    st.write("Evaluation of Shor's Algorithm impact on traditional ECC vs. PQC Algorithms.")
    render_sim_plots("sim1")

with tab2:
    st.header("Sim 2: Behavioral Adaptability")
    st.subheader("Adaptive Decision Audit")
    
    if 'logic_logs' in st.session_state:
        st.write("Real-time breakdown of ML-driven lane selection based on network telemetry:")
        audit_df = pd.DataFrame(st.session_state['logic_logs'])
        
        st.dataframe(
            audit_df,
            use_container_width=True,
            column_config={
                "ML Threat Score": st.column_config.ProgressColumn(
                    "Threat Intensity", min_value=0, max_value=1, format="%.4f"
                ),
                "Value": st.column_config.NumberColumn("TX Value ($)"),
                "Final Lane": st.column_config.TextColumn("Selected Algorithm")
            }
        )
    
    st.divider()
    st.subheader(f"Statistical Performance Visualizations")
    render_sim_plots("sim2")

with tab3:
    st.header("Sim 3: Gas & Energy Economics")
    st.write(f"Comparative analysis of PQC signature overhead and resource consumption.")
    render_sim_plots("sim3")
    
with tab4:
    st.header("🔗 PQRegistry On-Chain Audit")
    
    # Check connection to the blockchain node
    logger = OnChainLogger()
    if logger.w3.is_connected():
        st.success(f"Connected to Hardhat Node | Registry: `{logger.contract_address}`")
    else:
        st.error("Hardhat Node Offline. Run 'npx hardhat node' to visualize live ledger data.")

    if st.button("🔄 Sync with Blockchain", use_container_width=True):
        with st.spinner("Fetching cryptographic proofs from ledger..."):
            raw_logs = logger.get_all_logs()
            
            if raw_logs:
                df = pd.DataFrame(raw_logs)
                
                # Ensure columns match the keys in your extracted_data list
                display_cols = ["txHash", "scheme", "threatScore", "latency", "verified", "block"]
                
                st.dataframe(
                    df[display_cols], 
                    use_container_width=True,
                    column_config={
                        "txHash": "TX ID",
                        "scheme": "Algorithm",
                        "threatScore": "Threat Level",
                        "latency": "Latency (ms)",
                        "verified": st.column_config.CheckboxColumn("Integrity")
                    }
                )
                st.info(f"Verified {len(df)} transactions logged on the PQRegistry contract.")
            else:
                st.warning("Registry is empty. Run 'Sim 2' to log adaptive security events on-chain.")