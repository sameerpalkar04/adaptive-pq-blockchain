import json
import os
from web3 import Web3

class OnChainLogger:
    def __init__(self, provider_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
        
        # --- PATH FIX ---
        # Find the project root relative to THIS file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        abi_path = os.path.join(project_root, "artifacts", "contracts", "PQRegistry.sol", "PQRegistry.json")
        
        if not os.path.exists(abi_path):
            print(f"Error: ABI not found at {abi_path}")
            self.contract = None
            return

        with open(abi_path, "r") as f:
            contract_json = json.load(f)
        
        self.abi = contract_json["abi"]
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def log_onchain(self, tx_hash, scheme, threat, latency, verified):
        if not self.contract or not self.w3.is_connected():
            return None
        
        # Ensure threat is an integer if Solidity expects uint256
        threat_val = int(threat * 100) if isinstance(threat, float) else threat
            
        tx = self.contract.functions.logTransaction(
            tx_hash,
            scheme,
            threat_val,
            int(latency),
            verified
        ).transact({"from": self.w3.eth.accounts[0]})

        return self.w3.eth.wait_for_transaction_receipt(tx)

    def get_all_logs(self):
        """Fetches events for the Streamlit UI"""
        if not self.contract: return []
        try:
            events = self.contract.events.TransactionLogged.get_all_entries()
            return [e['args'] for e in events]
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []