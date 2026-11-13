from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from ..models.user import User

def create_token(user_id):
    return jwt.encode({"sub": str(user_id)}, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Authentication required."}), 401
        try:
            payload = jwt.decode(header.split(" ", 1)[1], current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            user = User.query.get(int(payload["sub"]))
            if not user:
                raise ValueError("User not found")
            g.current_user = user
        except Exception:
            return jsonify({"error": "Invalid or expired token."}), 401
        return fn(*args, **kwargs)
    return wrapper
