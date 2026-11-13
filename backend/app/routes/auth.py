from flask import Blueprint, request, jsonify, g
from sqlalchemy import func
from ..extensions import db
from ..models.user import User
from ..utils.auth import create_token, require_auth

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = (data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("password", ""))
    if not name or len(name) > 120 or "@" not in email or len(password) < 8:
        return jsonify({"error": "Provide a name, valid email, and password of at least 8 characters."}), 400
    if User.query.filter(func.lower(User.email) == email).first():
        return jsonify({"error": "An account with this email already exists."}), 409
    user = User(name=name, email=email); user.set_password(password)
    db.session.add(user); db.session.commit()
    return jsonify({"user": user.to_dict(), "token": create_token(user.id)}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower(); password = data.get("password", "")
    user = User.query.filter(func.lower(User.email) == email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    return jsonify({"user": user.to_dict(), "token": create_token(user.id)})

@auth_bp.get("/me")
@require_auth
def me():
    return jsonify({"user": g.current_user.to_dict()})
