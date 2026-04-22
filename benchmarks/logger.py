import csv
import os
import time

class MetricsLogger:

    def __init__(self, filename="logs/metrics.csv"):

        self.filename = filename

        os.makedirs("logs", exist_ok=True)

        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "tx_id",
            "scheme",
            "lane",
            "predicted_threat",
            "congestion",
            "sign_latency",
            "verify_latency",
            "timestamp"
        ])

    def log(self, tx_id, scheme, lane, threat,
        congestion, sign_latency, verify_latency):

        self.writer.writerow([
            tx_id,
            scheme,
            lane,
            threat,
            congestion,
            sign_latency,
            verify_latency,
            time.time()
        ])

        self.file.flush()

    def close(self):
        self.file.close()