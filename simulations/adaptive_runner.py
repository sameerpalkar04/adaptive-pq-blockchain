import os
import sys
import numpy as np
import time

# Ensure the root directory is in the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from adaptive_middleware.controller import AdaptiveMiddleware

# --- MOCK SCHEMES ---
# These simulate the PQC algorithms you've implemented or plan to use.
class MockScheme:
    def __init__(self, name, base_latency):
        self._name = name
        self.base_latency = base_latency # simulates compute overhead

    def sign(self, data):
        # Simulate computational delay for research benchmarks
        time.sleep(self.base_latency / 1000) 
        return f"sig_{self._name}_{os.urandom(4).hex()}".encode()

    def name(self):
        return self._name

    def get_public_key(self):
        return f"pk_{self._name}".encode()

def run_research_simulation():
    # Initialize Mock Schemes with realistic relative latencies
    schemes = {
        "FALCON":    MockScheme("FALCON", 0.5),    # Fast
        "OV":        MockScheme("OV", 0.2),        # Extremely Fast
        "DILITHIUM": MockScheme("DILITHIUM", 1.2), # Moderate
        "HYBRID":    MockScheme("HYBRID", 2.5)     # Slow (Dual Signature)
    }

    # Initialize the Middleware
    mw = AdaptiveMiddleware(schemes)

    print(f"{'TX ID':<8} | {'VAL ($)':<8} | {'CONGEST':<8} | {'THREAT':<8} | {'SELECTED LANE':<15} | {'COST':<8}")
    print("-" * 75)

    for i in range(1001):
        # --- STOCHASTIC ENVIRONMENT GENERATION ---
        # We simulate "Network Entropy" using noise. 
        # In the 500-800 range, we simulate an 'Anomaly Period'.
        noise = np.random.normal(0, 0.05)
        
        if 500 <= i <= 800:
            # Simulate high-risk environment features
            congestion = min(0.95, 0.75 + noise)
            v_latency = 0.09 + abs(noise) 
            tx_value = 5000 + np.random.randint(0, 2000)
        else:
            # Simulate stable network features
            congestion = max(0.05, 0.15 + noise)
            v_latency = 0.005 + abs(noise/10)
            tx_value = 100 + np.random.randint(0, 500)

        # Prepare payload
        network_state = {
            "congestion": congestion, 
            "verify_latency": v_latency
        }
        tx_metadata = {
            "id": i, 
            "value": tx_value, 
            "urgency": "NORMAL", 
            "payloadData": b"blockchain_transaction_data"
        }

        # --- MIDDLEWARE EXECUTION ---
        # The decision_engine calculates utility based on the features above
        result = mw.process_transaction(tx_metadata, network_state)
        
        # Display logs at specific intervals to observe the 'Pivot'
        if i % 100 == 0 or i == 500 or i == 801:
            m = result["metrics"]
            print(f"{i:<8} | {tx_value:<8} | {congestion:<8.2f} | {m['threat_score']:<8.3f} | {result['selected_lane']:<15} | {m['optimization_cost']:<8.3f}")

if __name__ == "__main__":
    run_dynamic_simulation = run_research_simulation()