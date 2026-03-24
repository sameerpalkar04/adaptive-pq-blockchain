class PolicyEngine:

    def choose_scheme(self, tx_metadata, threat_level, network_state):

        value = tx_metadata["value"]
        congestion = network_state["congestion"]

        if threat_level == "CRITICAL":
            return {
                "scheme": "HYBRID"
            }

        if value > 1500:
            return {
                "scheme": "DILITHIUM",
                "level": "5"
            }

        if congestion:
            return {
                "scheme": "FALCON"
            }

        return {
            "scheme": "DILITHIUM",
            "level": "2"
        }