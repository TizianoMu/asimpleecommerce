import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import create_access_token
from .models import db, User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
routes_bp = Blueprint("routes", __name__)
# List of temporary email domains
TEMP_EMAIL_DOMAINS = ["tempmail.com", "10minutemail.com", "disposablemail.com"]
@routes_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return f"Login successful! Your token: {access_token}"

        flash("Invalid email or password", "danger")

    return render_template("login.html")

# List of temporary email domains
TEMP_EMAIL_DOMAINS = ["tempmail.com", "10minutemail.com", "disposablemail.com"]

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

@routes_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration with validations."""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email is valid and not temporary
        if not is_valid_email(email):
            flash("Invalid or temporary email address.", "danger")
            return render_template("register.html")

        # Check if password is strong
        if not is_strong_password(password):
            flash("Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character.", "danger")
            return render_template("register.html")

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("register.html")

        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("routes.index"))

    return render_template("register.html")