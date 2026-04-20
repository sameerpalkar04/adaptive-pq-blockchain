import streamlit as st
import sys
import os
import glob  
import pandas as pd

# --- 1. STRICT PATH INJECTION ---
# This ensures blockchain_core can be found even when running inside /simulations
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now these imports will work
from simulations.runner import ResearchSimulator
from blockchain_core.onchain_logger import OnChainLogger

# Fixed: Removed duplicate set_page_config
st.set_page_config(page_title="PQC Adaptive Dashboard", layout="wide")

# --- 2. Sidebar Controls ---
st.sidebar.header("Simulation Parameters")
tx_sim2 = st.sidebar.slider("Behavioral Transactions (Sim 2)", 100, 10000, 5000, step=100)
tx_sim3 = st.sidebar.slider("Economic Transactions (Sim 3)", 500, 10000, 5000, step=100)
run_all = st.sidebar.button("Run Simulation")

# --- 3. Execution Engine ---
st.title("Post-Quantum Adaptive Middleware Dashboard")

if run_all:
    with st.status("Executing Research Simulations...", expanded=True) as status:
        st.write("Initializing Simulator and Purging Workspace...")
        sim = ResearchSimulator()
        
        st.write("Running Sim 1: Quantum Vulnerability Analysis...")
        sim.run_simulation_1()
        
        st.write(f"Running Sim 2: Behavioral Adaptability ({tx_sim2} TX)...")
        # Capture the logic logs returned by the modified runner
        logic_logs = sim.run_simulation_2(num_tx=tx_sim2)
        st.session_state['logic_logs'] = logic_logs 
        
        st.write(f"Running Sim 3: Gas & Energy Economics ({tx_sim3} TX)...")
        sim.run_simulation_3(num_tx=tx_sim3)
        
        status.update(label="All Simulations Complete!", state="complete", expanded=False)
    st.balloons()

# --- 4. Presentation Layer ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Quantum Analysis", 
    "Behavioral Logic", 
    "Economic Impact",
    "On-Chain Logs"
])

def render_sim_plots(sim_folder):
    # Fixed: Uses project_root to build absolute paths for glob
    path = os.path.join(project_root, "evaluation", "plots", sim_folder, "*.png")
    files = glob.glob(path)
    if not files:
        st.info(f"No plots found for {sim_folder}. Run the simulation to generate data.")
        return
    cols = st.columns(2)
    for idx, f_path in enumerate(sorted(files)):
        with cols[idx % 2]:
            st.image(f_path, use_container_width=True, caption=os.path.basename(f_path))

with tab1:
    render_sim_plots("sim1")

with tab2:
    st.subheader("Adaptive Decision Audit")
    
    # Logic Calculation Table
    if 'logic_logs' in st.session_state:
        st.write("Step-by-step breakdown of how the middleware calculated the Threat Score and chose a lane:")
        audit_df = pd.DataFrame(st.session_state['logic_logs'])
        
        st.dataframe(
            audit_df,
            use_container_width=True,
            column_config={
                "ML Threat Score": st.column_config.ProgressColumn(
                    "Threat Intensity", min_value=0, max_value=1, format="%.4f"
                ),
                "Value": st.column_config.TextColumn("TX Value"),
                "Final Lane": st.column_config.TextColumn("Selected Algorithm")
            }
        )
    
    st.divider()
    st.subheader(f"Statistical Visualizations ({tx_sim2} TX)")
    render_sim_plots("sim2")

with tab3:
    st.subheader(f"Economic Efficiency Analysis ({tx_sim3} TX)")
    render_sim_plots("sim3")
    
with tab4:
    st.header("PQRegistry On-Chain Audit")
    # Initialize logger
    try:
        logger = OnChainLogger()
        if st.button("Sync with Blockchain"):
            events = logger.get_all_logs()
            if events:
                df = pd.DataFrame(events)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No logs found. Ensure Hardhat is running and Sim 2 has executed.")
    except Exception as e:
        st.error(f"Blockchain Connection Error: {e}")