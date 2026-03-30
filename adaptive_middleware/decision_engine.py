class DecisionEngine:

    def choose_lane(self, tx_value, urgency, threat):

        if threat == "CRITICAL":
            return "HYBRID"

        if urgency == "HIGH":
            return "FALCON"

        if tx_value > 1500:
            return "DILITHIUM"

        return "OV"