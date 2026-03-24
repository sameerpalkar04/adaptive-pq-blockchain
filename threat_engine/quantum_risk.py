import random

class QuantumThreatEngine:

    def __init__(self):
        self.levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def get_current_threat(self):

        # simple stochastic model
        return random.choices(
            self.levels,
            weights=[0.4, 0.3, 0.2, 0.1]
        )[0]