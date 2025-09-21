from __future__ import annotations

from datetime import datetime, timedelta

from app.main import create_app
from app.models import db, Comentario, WeeklySummary


def iso_week(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


def summarize_week(start: datetime, end: datetime) -> str:
    rows = (
        Comentario.query.filter(Comentario.created_at >= start, Comentario.created_at < end)
        .all()
    )
    if not rows:
        return "Semana sem novos comentários relevantes."

    total = len(rows)
    cats = {}
    tags = {}
    for r in rows:
        cats[r.categoria or ""] = cats.get(r.categoria or "", 0) + 1
        for t in (r.tags_funcionalidades or []) or []:
            code = t.get("code")
            if code:
                tags[code] = tags.get(code, 0) + 1

    top_cat = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5]

    parts = [
        f"Total de comentários: {total}.",
        "Top categorias: " + ", ".join(f"{c} ({n})" for c, n in top_cat) + ".",
    ]
    if top_tags:
        parts.append("Tags mais citadas: " + ", ".join(f"{t} ({n})" for t, n in top_tags) + ".")
    return " ".join(parts)


def main() -> int:
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        #essa é a semana corrente (segunda a segunda)
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=7)
        week_id = iso_week(now)

        existing = WeeklySummary.query.filter_by(week=week_id).first()
        content = summarize_week(start, end)
        if existing:
            existing.content = content
            msg = "updated"
        else:
            db.session.add(WeeklySummary(week=week_id, content=content))
            msg = "created"
        db.session.commit()
        print(f"Weekly summary {msg} for {week_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

