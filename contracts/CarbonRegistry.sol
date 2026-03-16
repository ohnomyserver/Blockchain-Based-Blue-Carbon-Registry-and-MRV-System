// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CarbonRegistry {

    address public admin;

    mapping(address => uint256) public balances;

    event CreditsIssued(address indexed to, uint256 amount);
    event CreditsTransferred(address indexed from, address indexed to, uint256 amount);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function issueCredits(address to, uint256 amount) external onlyAdmin {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be greater than zero");
        balances[to] += amount;
        emit CreditsIssued(to, amount);
    }

    function transferCredits(address to, uint256 amount) external {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be greater than zero");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit CreditsTransferred(msg.sender, to, amount);
    }

    function getBalance(address account) external view returns (uint256) {
        return balances[account];
    }
}