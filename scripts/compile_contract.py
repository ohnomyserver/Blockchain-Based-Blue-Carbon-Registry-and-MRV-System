import json
from solcx import compile_standard, install_solc

install_solc("0.8.0")

with open("contracts/CarbonRegistry.sol", "r") as f:
    source = f.read()

compiled = compile_standard({
    "language": "Solidity",
    "sources": {"CarbonRegistry.sol": {"content": source}},
    "settings": {
        "outputSelection": {
            "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
        }
    }
}, solc_version="0.8.0")

contract_data = compiled["contracts"]["CarbonRegistry.sol"]["CarbonRegistry"]

with open("contracts/CarbonRegistry.json", "w") as f:
    json.dump({
        "abi": contract_data["abi"],
        "bytecode": contract_data["evm"]["bytecode"]["object"]
    }, f, indent=2)

print("Contract compiled successfully!")
print(f"ABI saved to contracts/CarbonRegistry.json")