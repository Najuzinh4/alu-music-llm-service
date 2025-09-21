from flask import Flask
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from app.config import Config
from app.models import db
from app.routes import api_bp
from app.auth import auth_bp
from app.dashboard import dashboard_bp
from app.reports import reports_bp
from app.insights import insights_bp
import time
from sqlalchemy.exc import OperationalError


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    Cache(app)

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(reports_bp, url_prefix="")
    app.register_blueprint(insights_bp, url_prefix="/insights")

    @app.route("/")
    def root():
        from flask import redirect
        return redirect("/dashboard/login")

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
