from sklearn.ensemble import RandomForestClassifier
import numpy as np

class MLThreatPredictor:
    def __init__(self):
        # Expanded Synthetic Training Data
        # Features: [Transaction Value, Network Congestion (0-1), Verification Latency (s)]
        X = np.array([
            [100, 0.1, 0.002], [200, 0.2, 0.002], [50, 0.0, 0.001],   # LOW
            [1000, 0.4, 0.005], [1200, 0.5, 0.008], [800, 0.3, 0.004], # MEDIUM
            [3000, 0.7, 0.015], [4500, 0.8, 0.018], [2500, 0.6, 0.012], # HIGH
            [10000, 0.9, 0.030], [25000, 1.0, 0.045], [50000, 0.9, 0.05] # CRITICAL
        ])

        # Labels mapped to numerical indices for internal logic if needed
        y = ["LOW"]*3 + ["MEDIUM"]*3 + ["HIGH"]*3 + ["CRITICAL"]*3

        # Use a more stable Forest configuration
        self.model = RandomForestClassifier(
            n_estimators=50, 
            max_depth=5, 
            random_state=42
        )
        self.model.fit(X, y)
        self.classes = self.model.classes_.tolist()
        
        # Pre-defining weights as a NumPy array for fast vector multiplication
        self.weight_map = np.array([
            0.1 if c == "LOW" else 
            0.4 if c == "MEDIUM" else 
            0.7 if c == "HIGH" else 1.0 
            for c in self.classes
        ])

    def predict_score(self, tx_value, congestion, verify_latency):
        """
        Calculates a risk score (0.0 to 1.0) and a confidence interval.
        """
        # Ensure features are in the correct shape
        features = np.array([[tx_value, congestion, verify_latency]])
        
        # Step 1: Get class probabilities
        # Example: [0.1, 0.7, 0.2, 0.0] for [CRITICAL, HIGH, LOW, MEDIUM]
        probs = self.model.predict_proba(features)[0]
        
        # Step 2: Vectorized Risk Calculation
        # This is mathematically equivalent to your loop but much faster
        risk_score = np.dot(probs, self.weight_map)
        
        # Step 3: Confidence calculation (entropy-based)
        # If one class has very high probability, confidence is high
        confidence = np.max(probs) 

        return float(risk_score), float(confidence)

    def get_threat_report(self, tx_value, congestion, verify_latency):
        """
        Helper for the Controller telemetry.
        """
        score, conf = self.predict_score(tx_value, congestion, verify_latency)
        
        # Simple heuristic for qualitative label
        label = "SAFE"
        if score > 0.8: label = "CRITICAL"
        elif score > 0.5: label = "ELEVATED"
        
        return {
            "score": round(score, 4),
            "confidence": round(conf, 2),
            "label": label
        }