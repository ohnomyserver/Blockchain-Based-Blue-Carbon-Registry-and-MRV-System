from web3 import Web3
from dotenv import load_dotenv
import json
import os

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
print(f"Connected to blockchain: {w3.is_connected()}")

# Load compiled contract
with open("contracts/CarbonRegistry.json", "r") as f:
    contract_data = json.load(f)

# Get admin account - strip whitespace and validate
private_key = os.getenv("ADMIN_PRIVATE_KEY").strip()
if private_key.startswith("0x") or private_key.startswith("0X"):
    private_key = private_key[2:]

# Ensure exactly 64 hex characters
private_key = private_key[:64]
admin_account = w3.eth.account.from_key(bytes.fromhex(private_key))
print(f"Deploying from: {admin_account.address}")

# Create contract instance
CarbonRegistry = w3.eth.contract(
    abi=contract_data["abi"],
    bytecode=contract_data["bytecode"]
)

# Build deployment transaction
tx = CarbonRegistry.constructor().build_transaction({
    'from': admin_account.address,
    'nonce': w3.eth.get_transaction_count(admin_account.address),
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'chainId': int(os.getenv("CHAIN_ID", 1337))
})

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, "0x" + private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

# Wait for receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt['contractAddress']

print(f"\n✅ Contract deployed at: {contract_address}")
print(f"\nAdd this to your .env file:")
print(f"CONTRACT_ADDRESS={contract_address}")