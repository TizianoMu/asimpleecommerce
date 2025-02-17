import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User
from flask_bcrypt import Bcrypt
from datetime import datetime,timedelta

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)

# List of temporary email domains
TEMP_EMAIL_DOMAINS = ["tempmail.com", "10minutemail.com", "disposablemail.com"]

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            expires = timedelta(days=30) if remember else timedelta(hours=1)
            access_token = create_access_token(identity=user.id, expires_delta=expires)
            # Update last_login field
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({"access_token": access_token}), 200
            #return redirect(url_for("routes.home"))  # Reindirizza alla home
        
        return jsonify("Invalid email or password", "danger"),401

    return render_template("login.html")

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
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        errors = []
        # Check if email is valid and not temporary
        if not is_valid_email(email):
            return jsonify("Invalid or temporary email address."),400

        # Check if password is strong
        if not is_strong_password(password):
            return jsonify("Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character."),400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify("Email is already registered."),400
    
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Registration successful!"}), 200

    return render_template("register.html")

@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Access granted for user {current_user}"}), 200
