import random
import time
import hashlib

# Middleware + PQC imports
from adaptive_middleware.controller import AdaptiveMiddleware
from adaptive_middleware.hybrid import HybridSignature

from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme
from pq_crypto_engine.signatures.sphincs_plus import SPHINCSScheme # Added

# Utilities
from benchmarks.logger import MetricsLogger

# Blockchain logger
from blockchain_core.onchain_logger import log_onchain

class BlockchainRuntime:
    def __init__(self):
        # Initialize PQC Schemes
        falcon = FalconScheme()
        dilithium = DilithiumScheme("5")
        ov = OVScheme()
        sphincs = SPHINCSScheme() # Added instantiation
        hybrid = HybridSignature(falcon, dilithium)

        # Added SPHINCS+ to the dictionary
        self.schemes_dict = {
            "FALCON": falcon,
            "DILITHIUM": dilithium,
            "OV": ov,
            "SPHINCS+": sphincs, 
            "HYBRID": hybrid
        }

        # Middleware
        self.middleware = AdaptiveMiddleware(
            schemes=self.schemes_dict
        )

        self.logger = MetricsLogger()
        self.chain = []
        self.tx_pool_size = 0

    def generate_transaction(self, tx_id):
        # Increased value range to trigger SPHINCS+ (since we set the threshold to 10000)
        return {
            "id": tx_id,
            "value": random.randint(100, 15000), 
            "urgency": random.choice(["LOW", "HIGH"]),
            "payloadData": f"tx_data_{tx_id}".encode()
        }

    def generate_tx_hash(self, tx):
        return hashlib.sha256(tx["payloadData"]).hexdigest()

    def run(self, num_tx=50):
        start_runtime = time.time()
        last_verify_latency = 0.005

        for i in range(num_tx):
            tx = self.generate_transaction(i)
            self.tx_pool_size = i

            network_state = {
                "congestion": (1.0 if self.tx_pool_size > 40 else 0.0),
                "verify_latency": last_verify_latency
            }

            # Adaptive middleware processing
            result = self.middleware.process_transaction(tx, network_state)

            lane = result["selected_lane"]
            scheme_name = result["scheme_name"]
            
            # Use .get() to handle potential key name differences in telemetry
            signature = result.get("signature") or result.get("signature_hex")
            public_key = result.get("public_key") or result.get("public_key_hex")

            threat_score = result["metrics"]["threat_score"]
            # Check if confidence exists in metrics (from our ML update)
            threat_conf = result["metrics"].get("threat_confidence", 0.0)

            sign_latency = result["metrics"]["sign_latency_ms"] / 1000

            # Verification logic
            scheme_obj = self.schemes_dict[lane]
            
            # Ensure signature is in bytes for the OQS verify method
            if isinstance(signature, str):
                sig_bytes = bytes.fromhex(signature)
            else:
                sig_bytes = signature

            start_verify = time.time()
            is_valid = scheme_obj.verify(
                tx["payloadData"],
                sig_bytes,
                scheme_obj.get_public_key() # Best to use object's key for internal consistency
            )
            verify_latency = time.time() - start_verify
            last_verify_latency = verify_latency

            tx_hash = self.generate_tx_hash(tx)

            # CSV logging
            self.logger.log(
                i, scheme_name, lane, threat_score,
                network_state["congestion"], sign_latency, verify_latency
            )

            # On-chain logging
            try:
                receipt = log_onchain(
                    tx_hash, scheme_name, lane,
                    int(verify_latency * 1000), is_valid
                )
                chain_tx_hash = receipt.transactionHash.hex() if receipt else None
            except Exception as e:
                # print(f"On-chain log failed for TX {i}: {e}")
                chain_tx_hash = None

            # Print stats including SPHINCS+ lanes
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

        self.logger.close()
        print(f"\nSimulation Complete. Total Time: {time.time() - start_runtime:.2f}s")