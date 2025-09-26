from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from db import get_db
from flask_jwt_extended import create_access_token

register_bp = Blueprint("register", __name__)
bcrypt = Bcrypt()

@register_bp.route("/register", methods=["POST"])
def register():
    db = get_db()
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    db = get_db()
    if db.users.find_one({"username": username}):
        return jsonify({"msg": "User already exists"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    db.users.insert_one({"username": username, "password": pw_hash})
    return jsonify({"msg": "User registered"}), 201
