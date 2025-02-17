from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Define the db and bcrypt instances globally
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """User model with hashed password."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def check_password(self, password):
        """Verify password hash."""
        return bcrypt.check_password_hash(self.password, password)
