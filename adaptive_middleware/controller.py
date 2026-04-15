import time
import numpy as np
from adaptive_middleware.ml_threat_predictor import MLThreatPredictor

class AdaptiveMiddleware:
    def __init__(self, schemes):
        self.threat_predictor = MLThreatPredictor()
        self.schemes = schemes
        
        # Updated to include SPHINCS+
        self.algorithm_profiles = {
            "FALCON":    {"security": 0.65, "latency": 0.20, "size": 0.30},
            "OV":        {"security": 0.50, "latency": 0.10, "size": 0.45},
            "DILITHIUM": {"security": 0.85, "latency": 0.55, "size": 0.75},
            "HYBRID":    {"security": 0.98, "latency": 0.95, "size": 1.00},
            "SPHINCS+":  {"security": 0.99, "latency": 0.90, "size": 1.20} # Added
        }

    def _calculate_utility(self, lane, threat_prob, congestion, alpha, beta):
        profile = self.algorithm_profiles[lane]
        
        # Security Risk: Heavily influenced by the ML Threat Score
        security_risk = (1.0 - profile["security"]) * threat_prob
        
        # Latency Cost: Scaled by current network congestion
        latency_cost = profile["latency"] * (1.0 + congestion)
        
        # Size Penalty: Important for SPHINCS+ (high gas/storage impact)
        size_penalty = profile["size"] * 0.15

        total_cost = (alpha * latency_cost) + (beta * security_risk) + size_penalty
        return total_cost

    def process_transaction(self, tx_metadata, network_state):
        tx_value = tx_metadata["value"]
        urgency = tx_metadata.get("urgency", "NORMAL")
        congestion = float(network_state.get("congestion", 0))
        verify_latency = network_state.get("verify_latency", 0.005)

        # Step 1: ML Threat Assessment
        threat_prob, confidence = self.threat_predictor.predict_score(
            tx_value, 
            congestion, 
            verify_latency
        )

        # Step 2: Dynamic Weight Assignment
        alpha = 0.8 if urgency == "HIGH" else 0.4
        beta = 0.9 if tx_value > 2000 else 0.5

        # Step 3: Optimization with Priority Override
        # If threat is critical (>0.9) or value is massive, bypass cost and force SPHINCS+
        if threat_prob > 0.92 or tx_value > 10000:
            best_lane = "SPHINCS+"
            min_cost = self._calculate_utility(best_lane, threat_prob, congestion, alpha, beta)
        else:
            best_lane = None
            min_cost = float('inf')
            for lane in self.algorithm_profiles.keys():
                if lane not in self.schemes: continue
                cost = self._calculate_utility(lane, threat_prob, congestion, alpha, beta)
                if cost < min_cost:
                    min_cost = cost
                    best_lane = lane

        # Step 4: Execution
        scheme = self.schemes[best_lane]
        payload = tx_metadata["payloadData"]
        if isinstance(payload, str): payload = payload.encode()

        start_time = time.time()
        signature = scheme.sign(payload)
        execution_time = time.time() - start_time

        # Step 5: Telemetry
        return {
            "tx_id": tx_metadata.get("id"),
            "signature_hex": signature.hex() if isinstance(signature, bytes) else signature,
            "selected_lane": best_lane,
            "scheme_name": scheme.name(),
            "metrics": {
                "threat_score": round(threat_prob, 4),
                "optimization_cost": round(min_cost, 4),
                "sign_latency_ms": round(execution_time * 1000, 2),
                "signature_size_bytes": len(signature) if isinstance(signature, bytes) else 0,
                "congestion_at_execution": congestion
            },
            "public_key": scheme.get_public_key().hex()
        }