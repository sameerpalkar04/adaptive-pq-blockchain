from sklearn.ensemble import RandomForestClassifier
import numpy as np

class MLThreatPredictor:
    def __init__(self):
        # Synthetic training data: [Value, Congestion, Latency]
        # We define what "Critical" or "High" threat looks like
        X = np.array([
            [100, 0, 0.002],   # Low value, no congestion
            [500, 0, 0.003],   # Low value
            [1500, 1, 0.010],  # Mid value, some congestion
            [1800, 1, 0.015],  # High value, high latency (Suspicious)
            [2500, 1, 0.025]   # Extreme values (Likely Quantum Attack)
        ])

        # Labels for training
        y = ["LOW", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

        self.model = RandomForestClassifier(n_estimators=10)
        self.model.fit(X, y)
        self.classes = self.model.classes_.tolist()

    def predict_score(self, tx_value, congestion, verify_latency):
        """
        Returns a float between 0 and 1 representing the risk level.
        """
        features = np.array([[tx_value, congestion, verify_latency]])
        
        # Get probability for each class
        probs = self.model.predict_proba(features)[0]
        
        # Map probabilities to a single risk score
        # We give higher weight to 'CRITICAL' and 'HIGH' classes
        class_weights = {
            "LOW": 0.1,
            "MEDIUM": 0.4,
            "HIGH": 0.7,
            "CRITICAL": 1.0
        }
        
        risk_score = 0.0
        for i, class_label in enumerate(self.classes):
            risk_score += probs[i] * class_weights.get(class_label, 0.1)
            
        return float(risk_score)