AluMusic LLM Service
====================

Serviço Flask para ingestão e classificação de comentários musicais, com dashboard privado, evals/métricas e testes automatizados.

Requisitos
- Python ≥ 3.10, Docker
- Postgres (via docker-compose)

Como rodar (Docker)
- docker-compose up --build
- Variáveis (opcional): DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY

Endpoints
- POST /auth/login → retorna JWT (admin/secret para dev)
- POST /api/comentarios (JWT) → ingere e classifica (lote ou unitário)
- GET/POST /dashboard/login → login de sessão
- GET /dashboard → lista com filtros e export CSV

Evals & Métricas
- Dataset exemplo: data/evals.jsonl
- Rodar: python -m scripts.run_evals --out reports/evals.json
- Saída: JSON com accuracy, precision/recall/F1 por classe e confusion matrix

Testes
- pip install -r requirements.txt
- pytest -q

Principais decisões
- Classificador heurístico determinístico para desenvolvimento (facilita testes) em app/services/llm.py
- Paralelismo simples com ThreadPoolExecutor no /api/comentarios; DB fora das threads
- Dashboard com sessão e usuários no banco (tabela users)
