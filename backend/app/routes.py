from flask import Blueprint, render_template

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/")
def home():
    return render_template("login.html")  # La pagina principale è la login
