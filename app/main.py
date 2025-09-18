from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from app.models import db
from app.routes import api_bp
from app.auth import auth_bp
import time
from sqlalchemy.exc import OperationalError


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    with app.app_context():
        connected = False
        for _ in range(5):  # tenta 5 vezes
            try:
                db.create_all()
                connected = True
                break
            except OperationalError:
                print("Banco ainda não disponível, tentando de novo...")
                time.sleep(3)
        if not connected:
            print("Não conseguiu conectar ao banco.")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)

