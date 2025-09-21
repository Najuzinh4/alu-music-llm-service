AluMusic LLM Service
====================

Serviço Flask para ingestão, classificação e análise de comentários musicais, com dashboard privado (Jinja e React SPA), relatório público em tempo real, evals e testes automatizados.

Stack
- Backend: Flask, Flask‑SQLAlchemy, Flask‑JWT‑Extended, Flask‑Caching
- DB: Postgres (Docker Compose)
- Relatórios: Pandas + Matplotlib
- Testes: PyTest (unitários e integração)
- Frontend (bônus): React + Vite (SPA servida pelo Flask)

Requisitos
- Python 3.10+, Docker + Docker Compose, Node 18+ (apenas para build do frontend)

Rodando com Docker (recomendado)
- Subir serviços: `docker compose up --build`
- App: http://localhost:5000
- Banco: Postgres exposto na porta 5432
- (Opcional) Definir segredos: `JWT_SECRET_KEY`, `SECRET_KEY`

Rodando local (sem Docker)
1) Instale deps: `pip install -r requirements.txt`
2) Tenha Postgres e DB `alu_music` criado
3) Exporte vars (PowerShell):
   - `$env:DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:5432/alu_music"`
   - `$env:JWT_SECRET_KEY="dev-key"; $env:SECRET_KEY="dev-key"`
4) Suba: `python -m app.main`

Autenticação
- JWT (API dev): `POST /auth/login` body `{ "username":"admin", "password":"123" }`
- Sessão (dashboard): `GET/POST /dashboard/login` (usuários na tabela `users`)
  - Seed do admin: `docker compose exec web python -m scripts.seed_user` (admin/secret)

Dashboard
- Clássico (Jinja): `GET /dashboard` → busca, filtros, export CSV
- SPA React (bônus): `GET /dashboard/app` (após login)
  - Build do frontend:
    - `cd frontend && npm install && npm run build`
    - copie `frontend/dist/*` para `app/static/ui/`
  - Dev opcional: `npm run dev` em `frontend/` com proxy para o backend

Relatório em tempo real (cache 60s)
- HTML: `GET /relatorio/semana`
- JSON: `GET /relatorio/semana?format=json`
- Inclui: volume diário, categorias frequentes, evolução de críticas, top tags 48h, confiança média

API principal
- `POST /api/comentarios` (JWT)
  - Entrada: objeto ou lista de `{ id?: UUID, texto: string }`
  - Processo: classificação em paralelo (ThreadPoolExecutor), persistência em transação única
  - Saída: `{ id, texto, categoria, tags_funcionalidades, confianca }` por item

Insights Q&A (bônus)
- `POST /insights/perguntar` (JWT)
  - Usa os três resumos semanais mais recentes (últimas 8 semanas)
  - Responde ≤150 palavras e retorna `{ resposta, semanas }`

Seeds e dados de exemplo
- Usuário admin: `docker compose exec web python -m scripts.seed_user`
- Comentários exemplo: `docker compose exec web python -m scripts.seed_comments`
- Resumo semanal: `docker compose exec web python -m scripts.generate_weekly_summary`

Evals & Métricas
- Dataset exemplo: `data/evals.jsonl`
- Rodar:
  - Docker: `docker compose exec web python -m scripts.run_evals --out reports/evals.json`
  - Local: `python -m scripts.run_evals --out reports/evals.json`
- Saída: JSON (accuracy, precision/recall/F1 por classe, confusion matrix)

Testes
- Docker: `docker compose exec web pytest -q`
- Local: `pytest -q`
- Cobrem: auth JWT, API com mock da LLM, evals runner, relatório semanal (JSON), insights Q&A

Decisões e hipóteses
- Classificação heuristicamente determinística em dev (plugável para LLM real) → reproduzível e testável
- Paralelismo com `ThreadPoolExecutor` na ingestão; DB fora das threads; commit único
- Relatórios com Pandas/Matplotlib e cache 60s (Flask‑Caching)
- Dashboard com sessão e usuários no banco; SPA React como bônus
- `db.create_all()` para simplificar; em prod, usar Alembic

Próximos passos sugeridos
- Celery + Redis (lotes grandes, retries, beat para resumo semanal)
- Alembic migrations
- Integração com LLM real + observabilidade
- CI (GitHub Actions) rodando testes e sanity de evals

