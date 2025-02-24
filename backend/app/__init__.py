from flask import Flask, g, request, jsonify, render_template, url_for
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from .models import db, User  # Ensure User is imported
from .routes.routes import routes_bp
from .routes.auth import auth_bp
from .routes.admin import admin_bp, analytics_bp
from .config import Config
from .jwt_handlers import *
from datetime import timedelta, datetime
from flask_bcrypt import Bcrypt

# Initialize JWTManager and Bcrypt
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    """Initialize the Flask app."""
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object(Config)

    # Initialize database, JWT, and Bcrypt with the app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    init_jwt_handlers(app) # Initialize JWT handlers

    # Initialize Flask-Migrate for database migrations
    migrate = Migrate(app, db)

    # Register blueprints for different parts of the application
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(analytics_bp, url_prefix="/admin")

    # Context processor to inject the current user into templates
    @app.context_processor
    def inject_user():
        try:
            # Verify JWT token in the request
            verify_jwt_in_request()
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()
            # Retrieve the user from the database
            user = User.query.get(user_id)
            # Return the user as a dictionary to be used in templates
            return dict(current_user=user)
        except:
            # If JWT verification fails or user is not found, return None
            return dict(current_user=None)
    
    # Return the initialized Flask app
    return app