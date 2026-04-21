from flask_login import UserMixin
from datetime import datetime
from .extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    company = db.relationship("Company", backref="owner", uselist=False)

    def set_password(self, raw_password: str):
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    credit_balance = db.Column(db.Float, default=0.0, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    eth_address = db.Column(db.String(42), unique=True, nullable=True)
    eth_private_key = db.Column(db.String(66), nullable=True)

    credits = db.relationship("CarbonCredit", backref="company", lazy=True)
    sent_transactions = db.relationship("Transaction", foreign_keys="Transaction.sender_id", backref="sender", lazy=True)
    received_transactions = db.relationship("Transaction", foreign_keys="Transaction.receiver_id", backref="receiver", lazy=True)

    def __repr__(self) -> str:
        return f"<Company {self.name}>"


class CarbonCredit(db.Model):
    __tablename__ = "carbon_credits"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    issued_to = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<CarbonCredit {self.amount} to company {self.issued_to}>"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tx_hash = db.Column(db.String(255), nullable=True)
    tx_type = db.Column(db.String(50), nullable=False)  # "issue", "transfer"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Transaction {self.tx_type} {self.amount}>"