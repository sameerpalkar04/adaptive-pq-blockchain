import json
import os
import csv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

class OnChainLogger:
    def __init__(self, provider_url="http://127.0.0.1:8545", csv_path="logs/metrics.csv"):
        # Web3 Connection 
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Inject POA middleware
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        self.csv_path = os.path.join(project_root, csv_path)
    
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._initialize_csv()

        # Smart Contract
        self.contract_address = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
        abi_path = os.path.join(project_root, "artifacts", "contracts", "PQRegistry.sol", "PQRegistry.json")
        
        self.contract = None
        if os.path.exists(abi_path):
            try:
                with open(abi_path, "r") as f:
                    contract_json = json.load(f)
                self.abi = contract_json["abi"]
                self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            except Exception as e:
                print(f"Contract Initialization Warning: {e}")

    def _initialize_csv(self):
        headers = ["id", "lane", "threat", "threat_level", "latency", "verified"]
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def _get_threat_level_label(self, score):
        try:
            s = float(score)
            if s > 0.90: return "4_Critical"
            elif s > 0.70: return "3_High"
            elif s > 0.40: return "2_Medium"
            return "1_Low"
        except (ValueError, TypeError):
            return "1_Low"

    def log_onchain(self, tx_id, scheme, threat, latency, verified, signature=b""):
        threat_label = self._get_threat_level_label(threat)
        try:
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([tx_id, scheme, threat, threat_label, int(latency * 1000), verified])
        except Exception as e:
            print(f"CSV Write Error: {e}")

        if not self.contract or not self.w3.is_connected():
            return None
        
        try:
            accounts = self.w3.eth.accounts
            if not accounts:
                return None
                
            account = accounts[0]
            tx_hash = self.contract.functions.logAndVerify(
                str(tx_id),
                str(scheme),
                str(threat),
                int(latency * 1000), 
                signature 
            ).transact({
                'from': account,
                'gas': 1000000,
                'gasPrice': self.w3.eth.gas_price
            })

            return self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            return None

    def get_all_logs(self):
        if not self.contract or not self.w3.is_connected():
            return []
        try:
            event_logs = self.contract.events.TransactionLogged().get_logs(from_block=0)
            
            extracted_data = []
            for entry in event_logs:
                args = entry['args']
                extracted_data.append({
                    "txHash": args.get('txHash', 'N/A'),
                    "scheme": args.get('scheme', 'N/A'),
                    "threatScore": args.get('threat', '0'),
                    "latency_ms": args.get('latency', 0),
                    "verified": args.get('verified', False),
                    "block": entry['blockNumber']
                })
            return extracted_data
        except Exception as e:
            print(f"Error fetching on-chain logs: {e}")
            return []