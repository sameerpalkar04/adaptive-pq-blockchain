from web3 import Web3
import json
from hexbytes import HexBytes

# Connect to local Hardhat node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

def simulate_classical_failure():
    # Ensure we are connected
    if not w3.is_connected():
        print("Error: Could not connect to Hardhat. Is 'npx hardhat node' running?")
        return

    # 1. SETUP: Use the first two accounts from Hardhat
    # Account 0 will be the Victim, Account 1 will be the Attacker
    victim_address = w3.eth.accounts[0]
    attacker_address = w3.eth.accounts[1]

    # 2. THE "QUANTUM" ATTACK:
    # IMPORTANT: Replace this string with a real private key from your Hardhat console output
    # It should look like: '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    attacker_private_key = "0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd" 

    if attacker_private_key == "0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd":
        print("❌ Error: You must paste a real private key from your Hardhat console into the script.")
        return

    # 3. FORGERY: Attacker creates a transaction to steal 10 ETH from the victim
    tx = {
        'from': victim_address,
        'to': attacker_address,
        'value': w3.to_wei(10, 'ether'),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(victim_address),
        'chainId': 31337 # Default Hardhat Chain ID
    }
    
    # 4. SIGNING: This is where the error occurred because the key was invalid
    signed_tx = w3.eth.account.sign_transaction(tx, attacker_private_key)
    
    # 5. EXECUTION: The blockchain accepts it because it's a valid ECC signature
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    print(f"✅ Success! Forged TX sent: {tx_hash.hex()}")
    print(f"Result: Blockchain accepted forged signature for {victim_address}")

if __name__ == "__main__":
    simulate_classical_failure()