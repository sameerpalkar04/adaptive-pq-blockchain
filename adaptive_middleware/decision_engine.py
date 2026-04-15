class DynamicOptimizer:
    def __init__(self):
        self.benchmarks = {
            "FALCON": {"security": 0.7, "latency": 0.2, "size": 0.3},
            "OV": {"security": 0.5, "latency": 0.1, "size": 0.4},
            "DILITHIUM": {"security": 0.9, "latency": 0.5, "size": 0.8},
            "HYBRID": {"security": 1.0, "latency": 0.9, "size": 1.0},
            "SPHINCS+": {"security": 0.99, "latency": 0.95, "size": 1.2} # Added SPHINCS+
        }
    
    def find_optimal_lane(self, schemes, threat_score, congestion, alpha, beta):
        best_lane = None
        min_cost = float('inf')

        for name, metrics in self.benchmarks.items():
            # Check if the scheme is actually provided in the hardware/software schemes
            if name not in schemes:
                continue

            security_risk = (1 - metrics["security"]) * threat_score
            latency_cost = metrics["latency"] * (1 + congestion)
            
            # Adding a small size penalty to the core cost function
            size_cost = metrics["size"] * 0.1

            total_cost = (alpha * latency_cost) + (beta * security_risk) + size_cost

            if total_cost < min_cost:
                min_cost = total_cost
                best_lane = name
                
        return best_lane