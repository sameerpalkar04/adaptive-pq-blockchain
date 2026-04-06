import time
import numpy as np
from adaptive_middleware.ml_threat_predictor import MLThreatPredictor

class AdaptiveMiddleware:
    def __init__(self, schemes):
        """
        :param schemes: A dictionary mapping lane names to Scheme objects
        e.g., {"FALCON": falcon_inst, "DILITHIUM": dilithium_inst, ...}
        """
        self.threat_predictor = MLThreatPredictor()
        self.schemes = schemes
        
        # Research-grade Benchmarks: Normalized 0.0 to 1.0
        # These constants represent the inherent properties of the algorithms
        self.algorithm_profiles = {
            "FALCON":    {"security": 0.65, "latency": 0.20, "size": 0.30},
            "OV":        {"security": 0.50, "latency": 0.10, "size": 0.45},
            "DILITHIUM": {"security": 0.85, "latency": 0.55, "size": 0.75},
            "HYBRID":    {"security": 0.98, "latency": 0.95, "size": 1.00}
        }

    def _calculate_utility(self, lane, threat_prob, congestion, alpha, beta):
        """
        The Core Novelty: A Multi-Objective Cost Function
        Goal: Minimize Cost = (Latency * Alpha) + (Security_Risk * Beta)
        """
        profile = self.algorithm_profiles[lane]
        
        # 1. Security Risk: Inverse of security strength multiplied by threat probability
        # Higher threat_prob makes security_risk the dominant factor
        security_risk = (1.0 - profile["security"]) * threat_prob
        
        # 2. Latency Cost: Base latency scaled by current network congestion
        # If congestion is high, even 'fast' schemes become more expensive
        latency_cost = profile["latency"] * (1.0 + congestion)
        
        # 3. Weighted Summation
        total_cost = (alpha * latency_cost) + (beta * security_risk)
        return total_cost

    def process_transaction(self, tx_metadata, network_state):
        tx_value = tx_metadata["value"]
        urgency = tx_metadata.get("urgency", "NORMAL")
        congestion = float(network_state.get("congestion", 0)) # 0.0 to 1.0
        verify_latency = network_state.get("verify_latency", 0.005)

        # Step 1: ML Threat Assessment (Returns a probability score 0.0-1.0)
        # Higher score = higher probability of a Quantum Attack
        threat_prob = self.threat_predictor.predict_score(
            tx_value, 
            congestion, 
            verify_latency
        )

        # Step 2: Dynamic Weight Assignment
        # alpha = Latency sensitivity | beta = Security sensitivity
        alpha = 0.8 if urgency == "HIGH" else 0.4
        beta = 0.9 if tx_value > 2000 else 0.5

        # Step 3: Heuristic Optimization
        # Find the lane that minimizes the Cost Function
        best_lane = None
        min_cost = float('inf')

        for lane in self.algorithm_profiles.keys():
            cost = self._calculate_utility(lane, threat_prob, congestion, alpha, beta)
            if cost < min_cost:
                min_cost = cost
                best_lane = lane

        # Step 4: Execution
        scheme = self.schemes[best_lane]
        payload = tx_metadata["payloadData"]

        start_time = time.time()
        signature = scheme.sign(payload)
        execution_time = time.time() - start_time

        # Step 5: Comprehensive Telemetry for the Research Report
        return {
            "tx_id": tx_metadata.get("id"),
            "signature": signature,
            "selected_lane": best_lane,
            "scheme_name": scheme.name(),
            "metrics": {
                "threat_score": round(threat_prob, 4),
                "optimization_cost": round(min_cost, 4),
                "sign_latency_ms": round(execution_time * 1000, 2),
                "congestion_at_execution": congestion
            },
            "public_key": scheme.get_public_key()
        }