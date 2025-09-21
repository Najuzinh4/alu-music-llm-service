from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String, nullable=True)
    tags_funcionalidades = db.Column(db.JSON, nullable=True)
    confianca = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WeeklySummary(db.Model):
    __tablename__ = "weekly_summaries"

    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.String(10), index=True, nullable=False)  # e.g., 2025-W30
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
