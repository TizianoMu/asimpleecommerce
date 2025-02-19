from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .models import db
from .routes.routes import routes_bp
from .routes.auth import auth_bp
from .routes.admin import admin_bp
from .config import Config  # Importa la configurazione
from .jwt_handlers import *
jwt = JWTManager()

def create_app():
    """Initialize the Flask app."""
    app = Flask(__name__)
    
    # Load config.py
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    init_jwt_handlers(app)

    migrate = Migrate(app, db)

    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
