from flask import jsonify, redirect, url_for
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def init_jwt_handlers(app):
    """Configura i gestori di errori JWT per l'app Flask."""
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return redirect(url_for("auth.login"))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return redirect(url_for("auth.login"))

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return redirect(url_for("auth.login"))
