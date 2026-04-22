import random
import time
import hashlib

# Middleware + PQC imports
from adaptive_middleware.controller import AdaptiveMiddleware
from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme
from pq_crypto_engine.signatures.sphincs_plus import SPHINCSScheme

# Utilities
from benchmarks.logger import MetricsLogger
from blockchain_core.onchain_logger import OnChainLogger

class BlockchainRuntime:
    def __init__(self):
        # 1. Initialize PQC Schemes
        falcon = FalconScheme()
        dilithium = DilithiumScheme("5")
        ov = OVScheme()
        sphincs = SPHINCSScheme()

        self.schemes_dict = {
            "FALCON": falcon,
            "DILITHIUM": dilithium,
            "OV": ov,
            "SPHINCS+": sphincs, 
        }

        # 2. Initialize Core Components
        # Pass the schemes to the middleware for decision logic
        self.middleware = AdaptiveMiddleware(schemes=self.schemes_dict)
        
        # CSV logger for local performance data
        self.logger = MetricsLogger()
        
        # Persistent blockchain helper for on-chain audit trails
        self.onchain_helper = OnChainLogger() 
        
        self.chain = []
        self.tx_pool_size = 0

    def generate_transaction(self, tx_id):
        """Generates mock transaction data with varying values to test adaptive logic."""
        return {
            "id": tx_id,
            "value": random.randint(100, 15000), 
            "urgency": random.choice(["LOW", "HIGH"]),
            "payloadData": f"tx_data_{tx_id}".encode()
        }

    def generate_tx_hash(self, tx):
        return hashlib.sha256(tx["payloadData"]).hexdigest()

    def run(self, num_tx=50):
        """Main simulation execution loop."""
        print(f"Starting Simulation for {num_tx} transactions...")
        start_runtime = time.time()
        last_verify_latency = 0.005 # Seed value for first TX

        for i in range(num_tx):
            tx = self.generate_transaction(i)
            self.tx_pool_size = i

            # Mock network conditions
            network_state = {
                "congestion": (1.0 if self.tx_pool_size > 40 else 0.0),
                "verify_latency": last_verify_latency
            }

            # 3. Adaptive Middleware Decision
            # ML Model predicts threat and selects the best PQC algorithm
            result = self.middleware.process_transaction(tx, network_state)

            lane = result["selected_lane"]
            scheme_name = result["scheme_name"]
            
            # Extract telemetry and cryptographic material
            signature = result.get("signature") or result.get("signature_hex")
            threat_score = result["metrics"]["threat_score"]
            threat_conf = result["metrics"].get("threat_confidence", 0.0)
            sign_latency = result["metrics"]["sign_latency_ms"] / 1000 # Convert to seconds

            # 4. PQC Verification Logic
            scheme_obj = self.schemes_dict[lane]
            
            # Handle signature format (hex string vs bytes)
            sig_bytes = bytes.fromhex(signature) if isinstance(signature, str) else signature

            start_verify = time.time()
            is_valid = scheme_obj.verify(
                tx["payloadData"],
                sig_bytes,
                scheme_obj.get_public_key()
            )
            verify_latency = time.time() - start_verify
            last_verify_latency = verify_latency

            tx_hash = self.generate_tx_hash(tx)

            # 5. Local CSV Logging (for Sim 2/Sim 3 plots)
            self.logger.log(
                i, scheme_name, lane, threat_score,
                network_state["congestion"], sign_latency, verify_latency
            )

            # 6. Blockchain Logging (PQRegistry Audit)
            chain_tx_hash = None
            try:
                # Pass the sig_bytes we generated earlier in the loop
                receipt = self.onchain_helper.log_onchain(
                    tx_id=str(tx["id"]),    
                    scheme=lane,            
                    threat=round(threat_score, 2), # Passing as a float/str
                    latency=verify_latency, 
                    verified=is_valid,
                    signature=sig_bytes # Pass actual PQC signature bytes
                )
                
                if receipt:
                    chain_tx_hash = receipt.transactionHash.hex()
                    print(f"Logged to Block: {receipt.blockNumber}")
            except Exception as e:
                print(f"On-chain log failed: {e}")

            # 7. Console Telemetry
            print(
                f"TX {i:03d} | "
                f"Score={threat_score:.2f} (Conf:{threat_conf:.2f}) | "
                f"Lane={lane:10} | "
                f"Sign={sign_latency:.4f}s | "
                f"Valid={is_valid}"
            )

            self.chain.append({
                "header": tx,
                "signature": signature,
                "tx_hash": tx_hash,
                "onchain_tx": chain_tx_hash
            })

        # Finalize logs and cleanup
        self.logger.close()
        total_time = time.time() - start_runtime
        print(f"\nSimulation Complete. Total Time: {total_time:.2f}s")
        print(f"Data saved to benchmarks/ and PQRegistry contract.")