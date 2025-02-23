import re
from flask import Blueprint, render_template, request, url_for, jsonify, make_response
from flask_jwt_extended import create_access_token,set_access_cookies,create_refresh_token, jwt_required, get_jwt_identity, unset_jwt_cookies,set_refresh_cookies
from ..models import db, User
from flask_bcrypt import Bcrypt
from datetime import datetime,timedelta

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)

# List of temporary email domains
TEMP_EMAIL_DOMAINS = ["tempmail.com", "10minutemail.com", "disposablemail.com"]

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON: No data provided"}), 400

        email = data.get("email")
        password = data.get("password")
        remember = data.get("remember", False)  # Default to False if not provided

        if not email:
            return jsonify({"error": "Email is required"}), 400

        if not password:
            return jsonify({"error": "Password is required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Invalid email or password"}), 401

        try:
            expires = timedelta(days=30) if remember else timedelta(hours=3)
            access_token = create_access_token(identity=user.id, expires_delta=expires)
            refresh_token = create_refresh_token(identity=user.id)

            # Update last_login field
            user.last_login = datetime.utcnow()
            db.session.commit()

            response = jsonify({
                "msg": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "redirect_url": url_for("admin.home")
            })

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response

        except Exception as e:
            db.session.rollback() # Rollback in case of error
            return jsonify({"error": f"An error occurred during login: {str(e)}"}), 500

    return render_template("auth/login.html")

def is_valid_email(email):
    """Check if email format is valid and not from a temporary service."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False
    domain = email.split("@")[-1]
    return domain not in TEMP_EMAIL_DOMAINS

def is_strong_password(password):
    """Ensure password contains at least 8 characters, an uppercase letter, a number, and a special character."""
    return bool(re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON: No data provided"}), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name:
            return jsonify({"error": "Name is required"}), 400

        if not email:
            return jsonify({"error": "Email is required"}), 400

        if not password:
            return jsonify({"error": "Password is required"}), 400

        # Check if email is valid and not temporary
        if not is_valid_email(email):
            return jsonify({"error": "Invalid or temporary email address"}), 400

        # Check if password is strong
        if not is_strong_password(password):
            return jsonify({"error": "Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character"}), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email is already registered"}), 400

        try:
            # Create new user
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"message": "Registration successful!"}), 201  # Use 201 for resource creation

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": f"An error occurred during registration: {str(e)}"}), 500

    return render_template("auth/register.html")

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        response = jsonify({"message": "Logged out"})
        unset_jwt_cookies(response)  # Delete JWT token from cookies
        return response

    except Exception as e:
        return jsonify({"error": f"An error occurred during logout: {str(e)}"}), 500

@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": f"Access granted for user {current_user_id}"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred during verification: {str(e)}"}), 500