import time
import numpy as np
from web3 import Web3
from adaptive_middleware.ml_threat_predictor import MLThreatPredictor

class AdaptiveMiddleware:
    def __init__(self, schemes, rpc_url="http://127.0.0.1:8545"):
        self.threat_predictor = MLThreatPredictor()
        self.schemes = schemes
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Algorithm profiles including SPHINCS+
        self.algorithm_profiles = {
            "FALCON":    {"security": 0.65, "latency": 0.20, "size": 0.30},
            "OV":        {"security": 0.50, "latency": 0.10, "size": 0.45},
            "DILITHIUM": {"security": 0.85, "latency": 0.55, "size": 0.75},
            "HYBRID":    {"security": 0.98, "latency": 0.95, "size": 1.00},
            "SPHINCS+":  {"security": 0.99, "latency": 0.90, "size": 1.20}
        }

    def _calculate_utility(self, lane, threat_prob, congestion, alpha, beta):
        """Calculates utility cost where lower is better."""
        profile = self.algorithm_profiles[lane]
        
        # Security Risk: Heavily influenced by the ML Threat Score
        security_risk = (1.0 - profile["security"]) * threat_prob
        
        # Latency Cost: Scaled by current network congestion
        latency_cost = profile["latency"] * (1.0 + congestion)
        
        # Size Penalty: Fixed cost multiplier for gas impact
        size_penalty = profile["size"] * 0.15

        total_cost = (alpha * latency_cost) + (beta * security_risk) + size_penalty
        return total_cost

    def process_transaction(self, tx_metadata, network_state):
        # Step 1: Extraction
        tx_value = float(tx_metadata.get("value", 0))
        urgency = tx_metadata.get("urgency", "NORMAL")
        congestion = float(network_state.get("congestion", 0.1))
        verify_latency = float(network_state.get("verify_latency", 0.005))

        # Step 2: ML Threat Assessment
        threat_prob, confidence = self.threat_predictor.predict_score(
            tx_value, 
            congestion, 
            verify_latency
        )

        # Step 3: Dynamic Weight Assignment
        alpha = 0.8 if urgency == "HIGH" else 0.4
        beta = 0.9 if tx_value > 2000 else 0.5

        # Step 4: Optimization with Priority Override
        # Hard-coded safety thresholds: Bypass utility calculation for critical scenarios
        if threat_prob > 0.92 or tx_value > 10000:
            best_lane = "SPHINCS+"
            min_cost = self._calculate_utility(best_lane, threat_prob, congestion, alpha, beta)
        else:
            best_lane = None
            min_cost = float('inf')
            
            # Find the minimum cost among available schemes
            for lane in self.algorithm_profiles.keys():
                if lane not in self.schemes: 
                    continue
                
                cost = self._calculate_utility(lane, threat_prob, congestion, alpha, beta)
                if cost < min_cost:
                    min_cost = cost
                    best_lane = lane

        # Step 5: Cryptographic Execution
        scheme = self.schemes[best_lane]
        payload = tx_metadata.get("payloadData", b"")
        if isinstance(payload, str): 
            payload = payload.encode()

        start_time = time.time()
        signature = scheme.sign(payload)
        execution_time = time.time() - start_time

        # Step 6: Telemetry Package
        return {
            "tx_id": tx_metadata.get("id"),
            "signature_hex": signature.hex() if isinstance(signature, bytes) else signature,
            "selected_lane": best_lane,
            "scheme_name": best_lane, # Using key name for consistency
            "metrics": {
                "threat_score": round(float(threat_prob), 4),
                "optimization_cost": round(float(min_cost), 4),
                "sign_latency_ms": round(execution_time * 1000, 2),
                "signature_size_bytes": len(signature) if isinstance(signature, bytes) else 0,
                "congestion_at_execution": congestion
            },
            "public_key": scheme.get_public_key().hex() if hasattr(scheme, 'get_public_key') else "N/A"
        }