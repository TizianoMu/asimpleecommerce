from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
from .admin import admin_bp
routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/",)
@admin_bp.route("/home")
@jwt_required()
def home():
    """
    Serves the home page.
    """
    return render_template("home.html")