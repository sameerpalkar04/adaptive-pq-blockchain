import random
import time

from adaptive_middleware.controller import AdaptiveMiddleware
from threat_engine.quantum_risk import QuantumThreatEngine
from benchmarks.logger import MetricsLogger


class BlockchainRuntime:

    def __init__(self):

        self.middleware = AdaptiveMiddleware()
        self.threat_engine = QuantumThreatEngine()
        self.logger = MetricsLogger()

        self.chain = []
        self.tx_pool_size = 0

    def generate_transaction(self):

        return {
            "value": random.randint(100, 2000),
            "urgency": random.choice(["LOW", "HIGH"]),
            "payload": f"tx_{random.randint(1,10000)}".encode()
        }

    def get_network_state(self):

        return {
            "congestion": self.tx_pool_size > 40
        }

    def run(self, num_tx=50):

        start = time.time()

        last_verify_latency = 0.005

        for i in range(num_tx):

            tx = self.generate_transaction()

            self.tx_pool_size = i

            network_state = {
                "congestion": self.tx_pool_size > 40,
                "verify_latency": last_verify_latency
            }

            # ⭐ Middleware now does ML + decision making internally
            result = self.middleware.process_transaction(
                tx,
                network_state
            )

            scheme_name = result["scheme_used"]
            lane = result["lane"]
            predicted_threat = result["predicted_threat"]
            signature = result["signature"]
            sign_latency = result["sign_latency"]

            # ⭐ verification step
            start_verify = time.time()

            scheme_obj = self.middleware.select_scheme(lane)
            scheme_obj.verify(tx["payload"], signature)

            verify_latency = time.time() - start_verify
            last_verify_latency = verify_latency

            # ⭐ log metrics
            self.logger.log(
                i,
                scheme_name,
                lane,
                predicted_threat,
                network_state["congestion"],
                sign_latency,
                verify_latency
            )

            print(
                f"TX {i} | "
                f"Threat={predicted_threat} | "
                f"Lane={lane} | "
                f"Scheme={scheme_name} | "
                f"Sign={sign_latency:.5f}s | "
                f"Verify={verify_latency:.5f}s"
            )

            self.chain.append(tx)

        self.logger.close()

        end = time.time()

        print("\nExecution Time:", end - start)