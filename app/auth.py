from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("username") == "admin" and data.get("password") == "123":
        token = create_access_token(identity="admin")
        return jsonify(access_token=token), 200
    return jsonify(msg="Invalid credentials"), 401
