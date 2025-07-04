import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import User
from app.extensions import db
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User()
    admin.username = "admin"
    admin.email = "admin@example.com"
    admin.password_hash = generate_password_hash("admin")
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print("✅ Tài khoản admin đã được tạo: admin / admin")