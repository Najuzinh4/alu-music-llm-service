from app.main import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    if not User.query.filter_by(username="admin").first():
        u = User(username="admin")
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()
        print("✅ created admin/secret")
    else:
        print("ℹ️ user already exists")
