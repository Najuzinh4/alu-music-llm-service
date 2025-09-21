import os
import sys
import pytest

#raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import create_app
from app.models import db, User


@pytest.fixture
def app_instance():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-key",
        JWT_SECRET_KEY="test-jwt",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        #cria um usuário para o dashboard (n é usado no JWT)
        u = User(username="user")
        u.set_password("pass")
        db.session.add(u)
        db.session.commit()
    yield app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()
