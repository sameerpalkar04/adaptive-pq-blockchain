from sklearn.ensemble import RandomForestClassifier
import numpy as np


class MLThreatPredictor:

    def __init__(self):

        # synthetic training data
        X = np.array([
            [100, 0, 0.002],
            [500, 0, 0.003],
            [1500, 1, 0.010],
            [1800, 1, 0.015],
            [2000, 1, 0.020]
        ])

        y = ["LOW", "LOW", "HIGH", "CRITICAL", "CRITICAL"]

        self.model = RandomForestClassifier()
        self.model.fit(X, y)

    def predict(self, tx_value, congestion, verify_latency):

        features = np.array([[tx_value, congestion, verify_latency]])

        return self.model.predict(features)[0]