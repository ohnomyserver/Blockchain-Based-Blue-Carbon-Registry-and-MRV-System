from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from .extensions import db
from .models import User
from .schemas import UserRegisterSchema, UserLoginSchema
from .utils.validators import validate_request

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
@validate_request(UserRegisterSchema)
def register():
    data = request.validated_data

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": f"User {user.username} created successfully"}), 201


@auth.route("/login", methods=["POST"])
@validate_request(UserLoginSchema)
def login():
    data = request.validated_data

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)
    return jsonify({"message": f"Welcome back, {user.username}"}), 200


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }), 200