import json
from web3 import Web3

# connect to local hardhat node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# paste your deployed contract address here
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# load ABI
with open(
    "artifacts/contracts/PQRegistry.sol/PQRegistry.json",
    "r"
) as f:
    contract_json = json.load(f)

abi = contract_json["abi"]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

def log_onchain(tx_hash, scheme, threat, latency, verified):
    tx = contract.functions.logTransaction(
        tx_hash,
        scheme,
        threat,
        int(latency),
        verified
    ).transact({
        "from": w3.eth.accounts[0]
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx)

    return receipt