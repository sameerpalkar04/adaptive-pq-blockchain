import json
import os
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

class OnChainLogger:
    def __init__(self, provider_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # Ensure this matches your deployment output
        self.contract_address = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        abi_path = os.path.join(project_root, "artifacts", "contracts", "PQRegistry.sol", "PQRegistry.json")
        
        self.contract = None
        if os.path.exists(abi_path):
            with open(abi_path, "r") as f:
                contract_json = json.load(f)
            self.abi = contract_json["abi"]
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def log_onchain(self, tx_id, scheme, threat, latency, verified, signature=b""):
        """Calls the logAndVerify function in the smart contract."""
        if not self.contract or not self.w3.is_connected():
            return None
        
        account = self.w3.eth.accounts[0]

        try:
            # Note: Changed function name to logAndVerify to match Solidity
            # Note: threat is passed as a string to match 'string memory _threat'
            tx_hash = self.contract.functions.logAndVerify(
                str(tx_id),
                str(scheme),
                str(threat),
                int(latency * 1000), # latency in ms
                signature # Passes the bytes signature
            ).transact({
                'from': account,
                'gas': 1000000,
                'gasPrice': self.w3.eth.gas_price
            })

            return self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            print(f"Blockchain Write Error: {e}")
            return None

    def get_all_logs(self):
        if not self.contract or not self.w3.is_connected():
            return []
        try:
            # Fetch the logs
            event_logs = self.contract.events.TransactionLogged().get_logs(from_block=0)
            
            extracted_data = []
            for entry in event_logs:
                args = entry['args']
                extracted_data.append({
                    "txHash": args.get('txHash', 'N/A'),
                    "scheme": args.get('scheme', 'N/A'),
                    "threatScore": args.get('threat', '0'), # Matches the 'threat' arg in event
                    "latency": args.get('latency', 0),
                    "verified": args.get('verified', False),
                    "block": entry['blockNumber']
                })
            return extracted_data
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []