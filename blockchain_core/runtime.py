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
            "value": random.randint(1, 2000),
            "payload": f"tx_{random.randint(1,10000)}".encode()
        }

    def get_network_state(self):

        return {
            "congestion": self.tx_pool_size > 40
        }

    def run(self, num_tx=50):

        start = time.time()

        for i in range(num_tx):

            tx = self.generate_transaction()

            threat = self.threat_engine.get_current_threat()

            self.tx_pool_size = i

            network_state = self.get_network_state()

            # ---- SIGN ----
            result = self.middleware.process_transaction(
                tx,
                threat,
                network_state
            )

            scheme = result["scheme_used"]
            signature = result["signature"]
            sign_latency = result["sign_latency"]

            # ---- VERIFY ----
            start_verify = time.time()

            decision = self.middleware.policy_engine.choose_scheme(
                tx, threat, network_state
            )

            scheme_obj = self.middleware.select_scheme(decision)

            scheme_obj.verify(tx["payload"], signature)

            verify_latency = time.time() - start_verify

            # ---- LOG ----
            self.logger.log(
                i,
                scheme,
                threat,
                network_state["congestion"],
                sign_latency,
                verify_latency
            )

            print(
                f"TX {i} | Threat={threat} | "
                f"Scheme={scheme} | "
                f"Sign={sign_latency:.5f}s | "
                f"Verify={verify_latency:.5f}s"
            )

            self.chain.append(tx)

        self.logger.close()

        end = time.time()

        print("\nExecution Time:", end - start)