from .extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    notifications = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(128), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.LargeBinary, nullable=True)  # Lưu dữ liệu ảnh dưới dạng nhị phân
    avatar_extension = db.Column(db.String(10), nullable=True)  # Lưu phần mở rộng file
    bio = db.Column(db.String(200), nullable=True)
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    symptom_checks = db.relationship('SymptomCheck', backref='user', lazy=True)
    profile_history = db.relationship('ProfileHistory', backref='user', lazy=True)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    glucose = db.Column(db.Float, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SymptomCheck(db.Model):
    __tablename__ = 'symptom_checks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symptoms = db.Column(db.String(255), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    icd11 = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ProfileHistory(db.Model):
    __tablename__ = 'profile_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)