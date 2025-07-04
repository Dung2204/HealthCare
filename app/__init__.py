import smtplib
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from .extensions import db
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Dell/OneDrive/Pictures/Documents/Code/python/OpenCV/Project/Web/instance/mydb.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'tenemailthuctecuaaban@gmail.com'  # Thay bằng email thật
    app.config['MAIL_PASSWORD'] = 'matkhaungdung16kytu'  # Thay bằng mật khẩu ứng dụng Gmail

    # Thêm cấu hình thư mục lưu ảnh avatar và định dạng cho phép
    app.config['UPLOAD_FOLDER'] = r'C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\static\images\avatar'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    try:
        os.makedirs(app.instance_path, exist_ok=True)
        print(f"Instance path: {app.instance_path}")
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            raise OSError(f"Không có quyền ghi vào thư mục: {app.config['UPLOAD_FOLDER']}")
    except OSError as e:
        print(f"Error creating instance folder or checking permissions: {e}")
        raise

    db.init_app(app)
    mail = Mail(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)
        db.create_all()

    try:
        smtp = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        smtp.starttls()
        smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        print("SMTP connection successful!")
        smtp.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}. Vui lòng kiểm tra email và mật khẩu ứng dụng Gmail.")
    except Exception as e:
        print(f"SMTP Connection Error: {e}")

    return app