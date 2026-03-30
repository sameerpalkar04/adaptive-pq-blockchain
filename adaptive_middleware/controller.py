import time

from adaptive_middleware.ml_threat_predictor import MLThreatPredictor
from adaptive_middleware.decision_engine import DecisionEngine
from adaptive_middleware.hybrid import HybridSignature

from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme


class AdaptiveMiddleware:

    def __init__(self):

        self.threat_predictor = MLThreatPredictor()
        self.decision_engine = DecisionEngine()

        # cached schemes
        self.fast_scheme = FalconScheme()
        self.storage_scheme = OVScheme()
        self.strong_scheme = DilithiumScheme("5")

        self.hybrid_scheme = HybridSignature(
            self.fast_scheme,
            self.strong_scheme
        )

    def select_scheme(self, lane):

        if lane == "FALCON":
            return self.fast_scheme

        if lane == "OV":
            return self.storage_scheme

        if lane == "DILITHIUM":
            return self.strong_scheme

        if lane == "HYBRID":
            return self.hybrid_scheme

        raise Exception("Invalid lane selected")

    def process_transaction(self, tx_metadata, network_state):

        tx_value = tx_metadata["value"]
        urgency = tx_metadata["urgency"]
        congestion = int(network_state["congestion"])

        # use last known latency or default
        verify_latency = network_state.get("verify_latency", 0.005)

        # ⭐ ML threat prediction
        threat = self.threat_predictor.predict(
            tx_value,
            congestion,
            verify_latency
        )

        # ⭐ decision engine lane selection
        lane = self.decision_engine.choose_lane(
            tx_value,
            urgency,
            threat
        )

        scheme = self.select_scheme(lane)

        payload = tx_metadata["payload"]

        start_sign = time.time()
        signature = scheme.sign(payload)
        sign_latency = time.time() - start_sign

        return {
            "signature": signature,
            "scheme_used": scheme.name(),
            "lane": lane,
            "predicted_threat": threat,
            "sign_latency": sign_latency,
            "public_key": scheme.get_public_key()
        }