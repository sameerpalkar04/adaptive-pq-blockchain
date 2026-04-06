class DynamicOptimizer:
    def __init__(self):
        self.benchmarks = {
            "FALCON": {"security":0.7, "latency":0.2, "size":0.3},
            "OV": {"security":0.5, "latency":0.1, "size":0.4},
            "DILITHIUM": {"security":0.9, "latency":0.5, "size":0.8},
            "HYBRID": {"security":1.0, "latency":0.9, "size":1.0},
        }
    
    def find_optimal_lane(self, schemes, threat_score, congestion, alpha, beta):
        best_lane = None
        min_cost = float('inf')

        for name, metrics in self.benchmarks.items():
            security_risk = (1-metrics["security"])*threat_score
            latency_cost = metrics["latency"] * (1+congestion)

            total_cost = (alpha*latency_cost) + (beta*security_risk)

            if total_cost < min_cost:
                min_cost = total_cost
                best_lane = name
                
        return best_lane