
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Company, CarbonCredit, Transaction

credits_bp = Blueprint("credits", __name__, url_prefix="/credits")


@credits_bp.route("/company/register", methods=["POST"])
@login_required
def register_company():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Company name is required"}), 400

    if Company.query.filter_by(user_id=current_user.id).first():
        return jsonify({"error": "You already have a registered company"}), 409

    if Company.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Company name already taken"}), 409

    company = Company(
        name=data["name"],
        description=data.get("description", ""),
        user_id=current_user.id
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": f"Company {company.name} registered", "id": company.id}), 201


@credits_bp.route("/issue", methods=["POST"])
@login_required
def issue_credits():
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    if not data or not all(k in data for k in ("company_id", "amount")):
        return jsonify({"error": "company_id and amount are required"}), 400

    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": "Company not found"}), 404

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
        tx_type="issue"
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": f"Issued {data['amount']} credits to {company.name}",
        "new_balance": company.credit_balance
    }), 200


@credits_bp.route("/transfer", methods=["POST"])
@login_required
def transfer_credits():
    data = request.get_json()
    if not data or not all(k in data for k in ("receiver_id", "amount")):
        return jsonify({"error": "receiver_id and amount are required"}), 400

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

    sender.credit_balance -= data["amount"]
    receiver.credit_balance += data["amount"]

    transaction = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=data["amount"],
        tx_type="transfer"
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": f"Transferred {data['amount']} credits to {receiver.name}",
        "your_new_balance": sender.credit_balance
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