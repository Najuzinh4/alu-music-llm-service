import os

class Config:
    # Usa variável de ambiente ou fallback local para dev
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Em produção, forneça via env: JWT_SECRET_KEY
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-insecure-change-me")
