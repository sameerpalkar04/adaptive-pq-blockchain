import random
import time
import hashlib

# Middleware + PQC imports
from adaptive_middleware.controller import AdaptiveMiddleware
from adaptive_middleware.hybrid import HybridSignature

from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme

# Utilities
from threat_engine.quantum_risk import QuantumThreatEngine
from benchmarks.logger import MetricsLogger

# Blockchain logger
from blockchain_core.onchain_logger import log_onchain


class BlockchainRuntime:
    def __init__(self):
        # Initialize PQC Schemes
        falcon = FalconScheme()
        dilithium = DilithiumScheme("5")
        ov = OVScheme()
        hybrid = HybridSignature(falcon, dilithium)

        self.schemes_dict = {
            "FALCON": falcon,
            "DILITHIUM": dilithium,
            "OV": ov,
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
        return {
            "id": tx_id,
            "value": random.randint(100, 3000),
            "urgency": random.choice(
                ["LOW", "HIGH"]
            ),
            "payloadData": f"tx_data_{tx_id}".encode()
        }

    def generate_tx_hash(self, tx):
        return hashlib.sha256(
            tx["payloadData"]
        ).hexdigest()

    def run(self, num_tx=50):
        start_runtime = time.time()
        last_verify_latency = 0.005

        for i in range(num_tx):
            tx = self.generate_transaction(i)

            self.tx_pool_size = i

            network_state = {
                "congestion": (
                    1.0 if self.tx_pool_size > 40
                    else 0.0
                ),
                "verify_latency":
                    last_verify_latency
            }

            # Adaptive middleware processing
            result = (
                self.middleware
                .process_transaction(
                    tx,
                    network_state
                )
            )

            lane = result["selected_lane"]
            scheme_name = result["scheme_name"]
            signature = result["signature"]
            public_key = result["public_key"]

            threat_score = (
                result["metrics"]
                ["threat_score"]
            )

            sign_latency = (
                result["metrics"]
                ["sign_latency_ms"] / 1000
            )

            # Verification
            scheme_obj = self.schemes_dict[
                lane
            ]

            start_verify = time.time()

            is_valid = scheme_obj.verify(
                tx["payloadData"],
                signature,
                public_key
            )

            verify_latency = (
                time.time() - start_verify
            )

            last_verify_latency = (
                verify_latency
            )

            # Generate transaction hash
            tx_hash = self.generate_tx_hash(tx)

            # CSV logging
            self.logger.log(
                i,
                scheme_name,
                lane,
                threat_score,
                network_state["congestion"],
                sign_latency,
                verify_latency
            )

            # ⭐ On-chain logging
            try:
                receipt = log_onchain(
                    tx_hash,
                    scheme_name,
                    lane,
                    int(
                        verify_latency * 1000
                    ),
                    is_valid
                )

                chain_tx_hash = (
                    receipt.transactionHash
                    .hex()
                )

            except Exception as e:
                print(
                    f"On-chain log failed "
                    f"for TX {i}: {e}"
                )

                chain_tx_hash = None

            print(
                f"TX {i:02d} | "
                f"Score={threat_score:.2f} | "
                f"Lane={lane:10} | "
                f"Sign={sign_latency:.5f}s | "
                f"Verify={verify_latency:.5f}s | "
                f"Valid={is_valid}"
            )

            self.chain.append({
                "header": tx,
                "signature": signature,
                "tx_hash": tx_hash,
                "onchain_tx":
                    chain_tx_hash
            })

        self.logger.close()

        print(
            f"\nSimulation Complete. "
            f"Total Time: "
            f"{time.time() - start_runtime:.2f}s"
        )