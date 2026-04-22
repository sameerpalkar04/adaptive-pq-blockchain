import json
import os
import csv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

class OnChainLogger:
    def __init__(self, provider_url="http://127.0.0.1:8545", csv_path="logs/metrics.csv"):
        # 1. Web3 Connection (Adapts to RPC passed from app.py)
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Inject POA middleware (necessary for Hardhat/Local nodes)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # 2. File Path Management
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        self.csv_path = os.path.join(project_root, csv_path)
        
        # Ensure logs directory exists and refresh CSV for the new run
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._initialize_csv()

        # 3. Smart Contract Configuration
        # Default Hardhat Address
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
        """Standardizes headers for ResearchSimulator Sim 2 & 3."""
        headers = ["id", "lane", "threat", "threat_level", "latency", "verified"]
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def _get_threat_level_label(self, score):
        """Categorical labels for the Adaptive Heatmap."""
        try:
            s = float(score)
            if s > 0.90: return "4_Critical"
            elif s > 0.70: return "3_High"
            elif s > 0.40: return "2_Medium"
            return "1_Low"
        except (ValueError, TypeError):
            return "1_Low"

    def log_onchain(self, tx_id, scheme, threat, latency, verified, signature=b""):
        """Dual-Logger: Sinks data to CSV for Research and Blockchain for Audit."""
        
        # --- PHASE 1: LOCAL CSV LOGGING ---
        # Essential for Dashboard plots regardless of RPC mode
        threat_label = self._get_threat_level_label(threat)
        try:
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                # Ensure latency is converted to integer ms for consistent plotting
                writer.writerow([tx_id, scheme, threat, threat_label, int(latency * 1000), verified])
        except Exception as e:
            print(f"CSV Write Error: {e}")

        # --- PHASE 2: BLOCKCHAIN TRANSACTION ---
        # This only executes if we are connected to a node where we have an account (Hardhat)
        if not self.contract or not self.w3.is_connected():
            return None
        
        try:
            # Check if accounts exist (Prevents crash when using public Live RPCs like Llama)
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
            # We fail silently here because Blockchain logging is secondary to Research CSVs
            return None

    def get_all_logs(self):
        """Syncs the 'On-Chain Audit' tab in app.py."""
        if not self.contract or not self.w3.is_connected():
            return []
        try:
            # Fetch events from the contract
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