import time

from adaptive_middleware.policy_engine import PolicyEngine
from adaptive_middleware.hybrid import HybridSignature

from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme


class AdaptiveMiddleware:

    def __init__(self):

        self.policy_engine = PolicyEngine()

        # Cached scheme instances (important)
        self.fast_scheme = FalconScheme()

        self.balanced_scheme = DilithiumScheme("2")
        self.strong_scheme = DilithiumScheme("5")

        self.hybrid_scheme = HybridSignature(
            self.fast_scheme,
            self.strong_scheme
        )

    def select_scheme(self, decision):

        if decision["scheme"] == "FALCON":
            return self.fast_scheme

        if decision["scheme"] == "DILITHIUM":

            if decision["level"] == "2":
                return self.balanced_scheme

            if decision["level"] == "5":
                return self.strong_scheme

        if decision["scheme"] == "HYBRID":
            return self.hybrid_scheme

        raise Exception("Invalid crypto decision")

    def process_transaction(self, tx_metadata, threat_level, network_state):

        decision = self.policy_engine.choose_scheme(
            tx_metadata,
            threat_level,
            network_state
        )

        scheme = self.select_scheme(decision)

        payload = tx_metadata["payload"]

        # ⭐ Measure signing latency
        start_sign = time.time()
        signature = scheme.sign(payload)
        end_sign = time.time()

        sign_latency = end_sign - start_sign

        return {
            "signature": signature,
            "scheme_used": scheme.name(),
            "public_key": scheme.get_public_key(),
            "sign_latency": sign_latency
        }