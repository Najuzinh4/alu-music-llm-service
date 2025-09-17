from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .models import db
from .routes import api_bp
from .auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    with app.app_context():
        db.create_all()

    return app

app = create_app()
