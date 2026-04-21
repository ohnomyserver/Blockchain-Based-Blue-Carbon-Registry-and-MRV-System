from web3 import Web3
import os
import json

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")))

def get_contract():
    contract_address = os.getenv("CONTRACT_ADDRESS")
    if not contract_address:
        return None
    
    with open("contracts/CarbonRegistry.json", "r") as f:
        contract_data = json.load(f)
    
    return w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=contract_data["abi"]
    )

def get_admin_account():
    private_key = os.getenv("ADMIN_PRIVATE_KEY")
    if not private_key:
        return None
    return w3.eth.account.from_key(private_key)