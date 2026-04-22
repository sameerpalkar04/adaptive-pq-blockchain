import random
import time
from web3 import Web3

# Middleware + PQC imports
from adaptive_middleware.controller import AdaptiveMiddleware
from pq_crypto_engine.signatures.dilithium import DilithiumScheme
from pq_crypto_engine.signatures.falcon import FalconScheme
from pq_crypto_engine.signatures.ov import OVScheme
from pq_crypto_engine.signatures.sphincs_plus import SPHINCSScheme

# Utilities
from benchmarks.logger import MetricsLogger
from blockchain_core.onchain_logger import OnChainLogger

class BlockchainRuntime:
    def __init__(self, rpc_url="http://127.0.0.1:8545"):
        # 1. Initialize PQC Schemes
        self.schemes_dict = {
            "FALCON": FalconScheme(),
            "DILITHIUM": DilithiumScheme("5"),
            "OV": OVScheme(),
            "SPHINCS+": SPHINCSScheme(), 
        }

        self.middleware = AdaptiveMiddleware(schemes=self.schemes_dict, rpc_url=rpc_url)
        self.onchain_helper = OnChainLogger(provider_url=rpc_url) 
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    def fetch_live_transaction(self):
        try:
            block = self.w3.eth.get_block('latest', full_transactions=True)
            if not block or not block.transactions:
                return None
            
            tx = random.choice(block.transactions) 
            payload = tx['input'] if tx['input'] and tx['input'] != '0x' else b"pqc_secure_payload"
            if isinstance(payload, str): payload = payload.encode()

            return {
                "id": tx['hash'].hex(),
                "value": float(self.w3.from_wei(tx['value'], 'ether')),
                "urgency": "HIGH" if tx['gasPrice'] > self.w3.eth.gas_price * 1.2 else "LOW",
                "payloadData": payload
            }
        except Exception as e:
            print(f"Live Fetch Warning: {e}")
            return None

    def run(self, num_tx=50, live_mode=False):

        mode_label = "LIVE BLOCKCHAIN" if live_mode else "MOCKED SIMULATION"
        print(f"--- Starting {mode_label} for {num_tx} Transactions ---")
        
        processed_count = 0
        error_streak = 0
        last_verify_latency = 0.005 

        while processed_count < num_tx:
            if live_mode:
                tx = self.fetch_live_transaction()
                if not tx:
                    error_streak += 1
                    time.sleep(min(error_streak, 5)) 
                    continue
                error_streak = 0
                network_state = {
                    "congestion": random.uniform(0.1, 0.6),
                    "verify_latency": last_verify_latency
                }
            else:
                is_critical = (processed_count > 0 and processed_count % 10 == 0)
                is_high = (processed_count > 0 and processed_count % 5 == 0 and not is_critical)

                if is_critical:
                    tx = {
                        "id": f"CRIT_{int(time.time())}_{processed_count}",
                        "value": random.uniform(500.0, 1000.0), 
                        "urgency": "HIGH",
                        "payloadData": b"critical_vault_transfer_payload"
                    }
                    network_state = {"congestion": random.uniform(0.85, 0.99), "verify_latency": 0.040}
                
                elif is_high:
                    tx = {
                        "id": f"HIGH_{int(time.time())}_{processed_count}",
                        "value": random.uniform(50.0, 150.0),
                        "urgency": "NORMAL",
                        "payloadData": b"high_risk_contract_interaction"
                    }
                    network_state = {"congestion": random.uniform(0.60, 0.80), "verify_latency": 0.020}
                
                else:
                    tx = {
                        "id": f"sim_{int(time.time())}_{processed_count}",
                        "value": random.uniform(0.01, 5.0),
                        "urgency": random.choice(["LOW", "NORMAL"]),
                        "payloadData": f"standard_tx_{processed_count}".encode()
                    }
                    network_state = {
                        "congestion": random.uniform(0.05, 0.50),
                        "verify_latency": last_verify_latency
                    }

            result = self.middleware.process_transaction(tx, network_state)
            lane = result["selected_lane"]
            threat_score = result["metrics"]["threat_score"]
            signature = result.get("signature_hex")

            scheme_obj = self.schemes_dict[lane]
            sig_bytes = bytes.fromhex(signature) if isinstance(signature, str) else signature

            start_verify = time.time()
            is_valid = scheme_obj.verify(tx["payloadData"], sig_bytes, scheme_obj.get_public_key())
            verify_latency = time.time() - start_verify
            last_verify_latency = verify_latency

            try:
                self.onchain_helper.log_onchain(
                    tx_id=str(tx["id"]), 
                    scheme=lane, 
                    threat=threat_score, 
                    latency=verify_latency, 
                    verified=is_valid, 
                    signature=sig_bytes
                )
            except Exception as e:
                print(f"Logging Sync Error: {e}")

            if threat_score > 0.9:
                alert = "Tx"
            elif threat_score > 0.7:
                alert = "Tx"
            elif threat_score > 0.4:
                alert = "Tx" 
            else:
                alert = "Tx"

            print(f"{alert} [{processed_count+1}/{num_tx}] Lane: {lane:<10} | Threat: {threat_score:.2f} | Val: {tx['value']:.2f} ETH")

            processed_count += 1
            if live_mode:
                time.sleep(0.5)

        print(f"\nRuntime Complete. Scenarios logged to CSV and Blockchain.")