from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String, nullable=True)   # será preenchida depois
    tags_funcionalidades = db.Column(db.JSON, nullable=True)
    confianca = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
