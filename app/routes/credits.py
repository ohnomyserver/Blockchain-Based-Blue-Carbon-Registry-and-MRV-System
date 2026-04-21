from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from web3 import Web3

from ..blockchain import get_contract, get_admin_account
from ..extensions import db
from ..models import Company, CarbonCredit, Transaction
from ..schemas import CompanyRegisterSchema, CreditIssueSchema, CreditTransferSchema
from ..utils.validators import validate_request

credits_bp = Blueprint("credits", __name__, url_prefix="/credits")


@credits_bp.route("/company/register", methods=["POST"])
@login_required
@validate_request(CompanyRegisterSchema)
def register_company():
    data = request.validated_data

    if Company.query.filter_by(user_id=current_user.id).first():
        return jsonify({"error": "You already have a registered company"}), 409

    if Company.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Company name already taken"}), 409

    w3 = Web3()
    account = w3.eth.account.create()

    company = Company(
        name=data["name"],
        description=data.get("description", ""),
        user_id=current_user.id,
        eth_address=account.address,
        eth_private_key=account.key.hex()
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": f"Company {company.name} registered", "id": company.id}), 201


@credits_bp.route("/issue", methods=["POST"])
@login_required
@validate_request(CreditIssueSchema)
def issue_credits():
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    data = request.validated_data
    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": "Company not found"}), 404

    # Blockchain transaction
    try:
        contract = get_contract()
        admin_account = get_admin_account()
        
        company_address = Web3.to_checksum_address(f"0x{company.user_id:040x}")
        
        tx = contract.functions.issueCredits(
            company_address,
            int(data["amount"] * 100)
        ).build_transaction({
            'from': admin_account.address,
            'nonce': contract.w3.eth.get_transaction_count(admin_account.address),
            'gas': 200000,
            'gasPrice': contract.w3.eth.gas_price
        })
        
        signed_tx = contract.w3.eth.account.sign_transaction(tx, admin_account.key)
        tx_hash = contract.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = contract.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        tx_hash_hex = tx_hash.hex()
    except Exception as e:
        return jsonify({"error": f"Blockchain transaction failed: {str(e)}"}), 500

    # Update database
    company.credit_balance += data["amount"]
    
    credit = CarbonCredit(
        amount=data["amount"],
        issued_to=company.id,
        issued_by=current_user.id,
        description=data.get("description", "")
    )
    db.session.add(credit)

    transaction = Transaction(
        sender_id=None,
        receiver_id=company.id,
        amount=data["amount"],
        tx_type="issue",
        tx_hash=tx_hash_hex
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": f"Issued {data['amount']} credits to {company.name}",
        "new_balance": company.credit_balance,
        "tx_hash": tx_hash_hex
    }), 200


@credits_bp.route("/transfer", methods=["POST"])
@login_required
@validate_request(CreditTransferSchema)
def transfer_credits():
    data = request.validated_data

    sender = Company.query.filter_by(user_id=current_user.id).first()
    if not sender:
        return jsonify({"error": "You don't have a registered company"}), 404

    receiver = Company.query.get(data["receiver_id"])
    if not receiver:
        return jsonify({"error": "Receiver company not found"}), 404

    if sender.id == receiver.id:
        return jsonify({"error": "Cannot transfer to yourself"}), 400

    if sender.credit_balance < data["amount"]:
        return jsonify({"error": "Insufficient credit balance"}), 400

    # Blockchain transaction
    try:
        contract = get_contract()
        sender_user = sender.owner
        
        sender_address = Web3.to_checksum_address(f"0x{sender.user_id:040x}")
        receiver_address = Web3.to_checksum_address(f"0x{receiver.user_id:040x}")
        
        tx = contract.functions.transferCredits(
            receiver_address,
            int(data["amount"] * 100)
        ).build_transaction({
            'from': sender_address,
            'nonce': contract.w3.eth.get_transaction_count(sender_address),
            'gas': 200000,
            'gasPrice': contract.w3.eth.gas_price
        })
        
        # Note: This requires sender's private key - needs proper key management
        # For now, using admin key as placeholder
        admin_account = get_admin_account()
        signed_tx = contract.w3.eth.account.sign_transaction(tx, admin_account.key)
        tx_hash = contract.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = contract.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        tx_hash_hex = tx_hash.hex()
    except Exception as e:
        return jsonify({"error": f"Blockchain transaction failed: {str(e)}"}), 500

    # Update database
    sender.credit_balance -= data["amount"]
    receiver.credit_balance += data["amount"]

    transaction = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=data["amount"],
        tx_type="transfer",
        tx_hash=tx_hash_hex
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": f"Transferred {data['amount']} credits to {receiver.name}",
        "your_new_balance": sender.credit_balance,
        "tx_hash": tx_hash_hex
    }), 200


@credits_bp.route("/balance", methods=["GET"])
@login_required
def get_balance():
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({"error": "You don't have a registered company"}), 404

    return jsonify({
        "company": company.name,
        "balance": company.credit_balance
    }), 200


@credits_bp.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({"error": "You don't have a registered company"}), 404

    txs = Transaction.query.filter(
        (Transaction.sender_id == company.id) |
        (Transaction.receiver_id == company.id)
    ).order_by(Transaction.timestamp.desc()).all()

    return jsonify([{
        "id": tx.id,
        "type": tx.tx_type,
        "amount": tx.amount,
        "sender": tx.sender_id,
        "receiver": tx.receiver_id,
        "tx_hash": tx.tx_hash,
        "timestamp": tx.timestamp.isoformat()
    } for tx in txs]), 200