import os
import sys
from blockchain_core.runtime import BlockchainRuntime
from simulations.runner import ResearchSimulator

def run_research_suite(iterations=2000):
    print(f"--- Starting Adaptive PQC Research Suite ---")
    
    sim_suite = ResearchSimulator()
    sim_suite.run_simulation_1()
    
    print(f"Initializing Blockchain Runtime: {iterations} Transactions...")
    
    if not os.path.exists('logs'): 
        os.makedirs('logs')
        
    runtime = BlockchainRuntime()
    runtime.run(iterations) 
    
    print("Generating Adaptive Switching Visualization...")
    sim_suite.run_simulation_2(num_tx=iterations)

    print("Generating Gas Cost and Energy Simulations")
    sim_suite.run_simulation_3(num_tx=5000)
    
    print(f"\nAll Research Tasks Complete.")
    print(f"Plots: evaluation/plots/sim1/ and evaluation/plots/sim2/")

if __name__ == "__main__":
    try:
        run_research_suite(iterations=2000)
    except KeyboardInterrupt:
        print("\nSimulation interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)