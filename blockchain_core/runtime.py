import random
import time

# New Imports for Initialization
from adaptive_middleware.controller import AdaptiveMiddleware
from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme
from adaptive_middleware.hybrid import HybridSignature 

# Existing Imports
from threat_engine.quantum_risk import QuantumThreatEngine # Note: Consider using this to feed 'threat_prob' later
from benchmarks.logger import MetricsLogger

class BlockchainRuntime:
    def __init__(self):
        # 1. Initialize PQC Scheme Instances
        falcon = FalconScheme()
        dilithium = DilithiumScheme("5")
        ov = OVScheme()
        hybrid = HybridSignature(falcon, dilithium)

        # 2. Map them for the Controller
        self.schemes_dict = {
            "FALCON": falcon,
            "DILITHIUM": dilithium,
            "OV": ov,
            "HYBRID": hybrid
        }

        # 3. Inject into Middleware
        self.middleware = AdaptiveMiddleware(schemes=self.schemes_dict)
        self.logger = MetricsLogger()

        self.chain = []
        self.tx_pool_size = 0

    def generate_transaction(self, tx_id):
        return {
            "id": tx_id,
            "value": random.randint(100, 3000), # Increased range for better ML variance
            "urgency": random.choice(["LOW", "HIGH"]),
            "payloadData": f"tx_data_{tx_id}".encode()
        }

    def run(self, num_tx=50):
        start_runtime = time.time()
        last_verify_latency = 0.005

        for i in range(num_tx):
            tx = self.generate_transaction(i)
            self.tx_pool_size = i # Simulating growing pool

            # Prepare network state for the optimizer
            network_state = {
                "congestion": 1.0 if self.tx_pool_size > 40 else 0.0,
                "verify_latency": last_verify_latency
            }

            # ⭐ Execute optimized PQC selection and signing
            result = self.middleware.process_transaction(tx, network_state)

            # Extract results based on our new Controller output format
            lane = result["selected_lane"]
            scheme_name = result["scheme_name"]
            signature = result["signature"]
            public_key = result["public_key"]
            threat_score = result["metrics"]["threat_score"]
            sign_latency = result["metrics"]["sign_latency_ms"] / 1000 # Convert back to seconds for logger

            # ⭐ Verification Step
            # We use the actual scheme object to verify
            scheme_obj = self.schemes_dict[lane]
            
            start_verify = time.time()
            is_valid = scheme_obj.verify(tx["payloadData"], signature, public_key)
            verify_latency = time.time() - start_verify
            
            last_verify_latency = verify_latency

            # ⭐ Log metrics for your Research Report
            self.logger.log(
                i,
                scheme_name,
                lane,
                threat_score,
                network_state["congestion"],
                sign_latency,
                verify_latency
            )

            print(
                f"TX {i:02d} | "
                f"Score={threat_score:.2f} | "
                f"Lane={lane:10} | "
                f"Sign={sign_latency:.5f}s | "
                f"Verify={verify_latency:.5f}s | "
                f"Valid={is_valid}"
            )

            self.chain.append({"header": tx, "signature": signature})

        self.logger.close()
        print(f"\nSimulation Complete. Total Time: {time.time() - start_runtime:.2f}s")