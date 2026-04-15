import os
import time
import pandas as pd
from blockchain_core.runtime import BlockchainRuntime

def run_large_scale_simulation(iterations=1000):
    print(f"🚀 Running Large-Scale Simulation: {iterations} Transactions")
    
    # Initialize your actual BlockchainRuntime from runtime.py
    runtime = BlockchainRuntime()
    
    # 1. Execute the Adaptive Simulation
    # This calls your adaptive_middleware.controller to select schemes
    runtime.run(iterations) 
    
    print("✅ Simulation complete. Running Quantum Evaluation Suite...")
    
    # 2. Automatically launch the evaluation scripts we will define below
    os.system("python3 -m evaluation.quantum_analysis")

if __name__ == "__main__":
    # Ensure logs folder exists for metrics.csv
    if not os.path.exists('logs'): os.makedirs('logs')
    
    run_large_scale_simulation(1000)