from sklearn.ensemble import RandomForestClassifier
import numpy as np

class MLThreatPredictor:
    def __init__(self):
        # Features: [Value, Congestion (0-1), Latency (s)]
        # Expanded to cover both Ether scales (0.1 - 100) and Mock scales (100 - 50k)
        X = np.array([
            # LOW RISK (Small values, low congestion)
            [0.1, 0.1, 0.001], [0.5, 0.2, 0.002], [50, 0.1, 0.002], 
            # MEDIUM RISK (Mid values or rising congestion)
            [2.0, 0.4, 0.005], [5.0, 0.5, 0.008], [1000, 0.4, 0.006], 
            # HIGH RISK (Large values or heavy congestion)
            [20.0, 0.7, 0.015], [50.0, 0.8, 0.020], [5000, 0.7, 0.018],
            # CRITICAL RISK (Whale movements or network saturation)
            [100.0, 0.9, 0.040], [500.0, 1.0, 0.050], [50000, 0.9, 0.045]
        ])

        y = ["LOW"]*3 + ["MEDIUM"]*3 + ["HIGH"]*3 + ["CRITICAL"]*3

        # Random Forest is robust to scale, but we limit depth to prevent 
        # overfitting on our small synthetic research set.
        self.model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=4, 
            random_state=42
        )
        self.model.fit(X, y)
        self.classes = self.model.classes_.tolist()
        
        # Weight mapping for risk score calculation
        # These weights drive the 'threat_score' column in your dashboard
        self.weight_map = np.array([
            0.1 if c == "LOW" else 
            0.4 if c == "MEDIUM" else 
            0.7 if c == "HIGH" else 1.0 
            for c in self.classes
        ])

    def predict_score(self, tx_value, congestion, verify_latency):
        """
        Calculates a risk score (0.0 to 1.0) synchronized for Dashboard CSVs.
        Handles both Live (Ether) and Simulated (Mock) value scales.
        """
        # Ensure input is float and handle potential None types from live RPCs
        val = float(tx_value if tx_value is not None else 0)
        cong = float(congestion if congestion is not None else 0.1)
        lat = float(verify_latency if verify_latency is not None else 0.005)

        features = np.array([[val, cong, lat]])

        # Step 1: Probability Distribution across categories
        probs = self.model.predict_proba(features)[0]

        # Step 2: Risk Calculation (Dot product of probabilities and category weights)
        risk_score = np.dot(probs, self.weight_map)

        # Step 3: Confidence (Max probability assigned to a single class)
        confidence = np.max(probs) 

        return float(risk_score), float(confidence)

    def get_threat_report(self, tx_value, congestion, verify_latency):
        """
        Generates qualitative labels for the 'Category' column in app.py.
        """
        score, conf = self.predict_score(tx_value, congestion, verify_latency)

        if score > 0.90:
            label = "4_Critical" # Matches 'levels' in ResearchSimulator
        elif score > 0.70:
            label = "3_High"
        elif score > 0.40:
            label = "2_Medium"
        else:
            label = "1_Low"

        return {
            "score": round(score, 4),
            "confidence": round(conf, 2),
            "label": label
        }