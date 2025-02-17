from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from .routes import routes_bp
def create_app():
    """Initialize the Flask app."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your_secret_key"

    # Initialize the db with the app
    db.init_app(app)

    # Register routes blueprint
    app.register_blueprint(routes_bp)

    return app