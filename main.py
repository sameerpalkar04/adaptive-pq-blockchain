import os
import sys
from blockchain_core.runtime import BlockchainRuntime
from simulations.runner import ResearchSimulator

def run_research_suite(iterations):
    """
    Executes the research suite based on the specific count 
    provided by the user via the Dashboard slider.
    """
    print(f"--- Starting Adaptive PQC Research Suite ---")
    print(f"Targeting {iterations} Transactions for Simulation and Logging...")
    
    sim_suite = ResearchSimulator()
    sim_suite.run_simulation_1() # Theory remains constant
    
    # Ensure logs directory exists for CSV/Text backups
    if not os.path.exists('logs'): 
        os.makedirs('logs')
        
    # --- BLOCKCHAIN LOGGING ---
    # This initializes the actual Hardhat/EVM transactions
    print(f"Initializing Blockchain Runtime: Processing {iterations} TXs...")
    runtime = BlockchainRuntime()
    runtime.run(iterations) 
    
    # --- SIMULATION 2: BEHAVIORAL ---
    print(f"Generating Adaptive Switching Visualization for {iterations} TXs...")
    sim_suite.run_simulation_2(num_tx=iterations)

    # --- SIMULATION 3: ECONOMICS ---
    print(f"Generating Gas and Energy Simulations for {iterations} TXs...")
    sim_suite.run_simulation_3(num_tx=iterations)
    
    print(f"\nAll Research Tasks Complete.")

if __name__ == "__main__":
    # Allows main.py to be run standalone with a custom number: python main.py 3500
    try:
        user_input = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
        run_research_suite(iterations=user_input)
    except Exception as e:
        print(f"Error: {e}")