from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from db import get_db

login_bp = Blueprint("login", __name__)
bcrypt = Bcrypt()
jwt = JWTManager()



@login_bp.route("/login", methods=["POST"])
def login():
    db = get_db()
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    db = get_db()
    user = db.users.find_one({"username": username})
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200
