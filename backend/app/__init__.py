from flask_migrate import Migrate
from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db
from .routes import routes_bp
from .auth import auth_bp

jwt = JWTManager()

def create_app():
    """Initialize the Flask app."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db/ecommerce"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your_secret_key"

    # Initialize the db with the app
    db.init_app(app)
    jwt.init_app(app)
    with app.app_context():
        db.create_all()  # Create DB tables
    migrate = Migrate(app, db)
    # Register routes blueprint
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)

    return app