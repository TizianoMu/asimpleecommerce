from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required
routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/")
@jwt_required()
def home():
    return render_template("dashboard.html")
