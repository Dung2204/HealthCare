import re
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, current_app, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .extensions import db
from .models import User, Prediction, SymptomCheck, ProfileHistory
from .forms import RegistrationForm, LoginForm, HealthForm, DeleteConfirmForm, SymptomCheckerForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm, UpdateProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import pandas as pd
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlalchemy.exc

main_bp = Blueprint('main', __name__)
mail = Mail()

# Định nghĩa ALLOWED_EXTENSIONS trong routes.py
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tải mô hình và các bộ mã hóa với đường dẫn tuyệt đối
condition_model_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\condition_model.pkl"
icd11_model_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\icd11_model.pkl"
action_model_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\action_model.pkl"
vectorizer_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\vectorizer.pkl"
condition_encoder_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\condition_encoder.pkl"
icd11_encoder_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\icd11_encoder.pkl"
action_encoder_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\action_encoder.pkl"
health_model_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\health_model.pkl"
health_encoder_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\app\models\health_encoder.pkl"

with open(condition_model_path, 'rb') as f:
    condition_model = pickle.load(f)
with open(icd11_model_path, 'rb') as f:
    icd11_model = pickle.load(f)
with open(action_model_path, 'rb') as f:
    action_model = pickle.load(f)
with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)
with open(condition_encoder_path, 'rb') as f:
    condition_encoder = pickle.load(f)
with open(icd11_encoder_path, 'rb') as f:
    icd11_encoder = pickle.load(f)
with open(action_encoder_path, 'rb') as f:
    action_encoder = pickle.load(f)
with open(health_model_path, 'rb') as f:
    health_model = pickle.load(f)
with open(health_encoder_path, 'rb') as f:
    health_encoder = pickle.load(f)

def ai_diagnosis(symptoms=None, body_part=None, age=None, bmi=None, glucose=None, heart_rate=None):
    if symptoms and body_part:
        # Xử lý Kiểm tra triệu chứng
        if not symptoms or not isinstance(symptoms, str) or not body_part:
            return {
                'condition': 'Lỗi',
                'probability': 0.0,
                'icd11': 'N/A',
                'action': 'Vui lòng nhập đầy đủ triệu chứng và bộ phận cơ thể',
                'disclaimer': 'Đây là chẩn đoán sơ bộ. Vui lòng tham khảo bác sĩ.'
            }

        # Kiểm tra ký tự không hợp lệ
        symptoms = symptoms.strip().lower()
        body_part = body_part.lower()
        for symptom in symptoms.split(","):
            if not re.match(r'^[\w\s]+$', symptom.strip()):
                return {
                    'condition': 'Lỗi',
                    'probability': 0.0,
                    'icd11': 'N/A',
                    'action': 'Triệu chứng chứa ký tự không hợp lệ',
                    'disclaimer': 'Đây là chẩn đoán sơ bộ. Vui lòng tham khảo bác sĩ.'
                }

        # Tạo input cho mô hình
        input_text = symptoms + ' ' + body_part
        input_vector = vectorizer.transform([input_text]).toarray()

        # Dự đoán
        condition_pred = condition_model.predict(input_vector)[0]
        icd11_pred = icd11_model.predict(input_vector)[0]
        action_pred = action_model.predict(input_vector)[0]
        probability_pred = condition_model.predict_proba(input_vector)[0].max()

        # Giải mã kết quả
        condition = condition_encoder.inverse_transform([condition_pred])[0]
        icd11 = icd11_encoder.inverse_transform([icd11_pred])[0]
        action = action_encoder.inverse_transform([action_pred])[0]

        return {
            'condition': condition,
            'probability': probability_pred,
            'icd11': icd11,
            'action': action,
            'disclaimer': 'Đây là chẩn đoán sơ bộ. Vui lòng tham khảo bác sĩ.'
        }
    elif all([age, bmi, glucose, heart_rate]):
        # Xử lý Chẩn đoán sức khỏe
        try:
            # Chuyển đổi đầu vào thành numpy array
            input_data = np.array([[float(age), float(bmi), float(glucose), float(heart_rate)]])
            
            # Dự đoán
            result_pred = health_model.predict(input_data)[0]
            probability_pred = health_model.predict_proba(input_data)[0].max()
            
            # Giải mã kết quả
            result = health_encoder.inverse_transform([result_pred])[0]
            
            return {
                'result': result,
                'probability': probability_pred,
                'disclaimer': 'Đây là chẩn đoán sức khỏe sơ bộ. Vui lòng tham khảo bác sĩ.'
            }
        except ValueError:
            return {
                'result': 'Lỗi',
                'probability': 0.0,
                'disclaimer': 'Dữ liệu đầu vào không hợp lệ. Vui lòng kiểm tra lại.'
            }
    else:
        return {
            'result': 'Lỗi',
            'probability': 0.0,
            'disclaimer': 'Vui lòng cung cấp đầy đủ thông tin.'
        }

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Username đã tồn tại. Vui lòng chọn tên khác.', 'error')
            return redirect(url_for('main.register'))
        if existing_email:
            flash('Email đã tồn tại. Vui lòng sử dụng email khác.', 'error')
            return redirect(url_for('main.register'))
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            try:
                msg = Message('Chào mừng đến với HealthCare!',
                              sender='yourrealemail@gmail.com',
                              recipients=[form.email.data])
                msg.body = f'Xin chào {form.username.data},\n\nCảm ơn bạn đã đăng ký tài khoản tại HealthCare. Vui lòng đăng nhập để bắt đầu sử dụng dịch vụ.\n\nTrân trọng,\nHealthCare Team'
                mail.send(msg)
                flash('Đăng ký thành công! Vui lòng kiểm tra email để xác nhận.', 'success')
            except Exception as e:
                flash('Đăng ký thành công, nhưng không thể gửi email xác nhận. Vui lòng liên hệ hỗ trợ.', 'warning')
                print(f"Lỗi gửi email: {e}")
            return redirect(url_for('main.login'))
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            flash('Email đã tồn tại. Vui lòng sử dụng email khác.', 'error')
            return redirect(url_for('main.register'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Đăng nhập thành công!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
    return render_template('login.html', form=form)

@main_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            reset_url = url_for('main.reset_password', token=token, _external=True)
            msg = Message('Yêu cầu đặt lại mật khẩu',
                         sender='your-email@gmail.com',
                         recipients=[user.email])
            msg.body = f'Xin chào {user.username},\n\nĐể đặt lại mật khẩu, vui lòng truy cập liên kết sau:\n{reset_url}\n\nLiên kết này có hiệu lực trong 1 giờ.\n\nTrân trọng,\nHealthCare Team'
            mail.send(msg)

            flash('Một email chứa liên kết đặt lại mật khẩu đã được gửi đến email của bạn.', 'success')
        else:
            flash('Email này không tồn tại trong hệ thống.', 'error')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html', form=form)

@main_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expiration < datetime.utcnow():
        flash('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'error')
        return redirect(url_for('main.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Mật khẩu của bạn đã được đặt lại thành công!', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form, token=token)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = HealthForm()
    symptom_form = SymptomCheckerForm()
    
    if symptom_form.validate_on_submit():
        symptoms = symptom_form.symptoms.data
        body_part = symptom_form.body_part.data
        diagnosis = ai_diagnosis(symptoms=symptoms, body_part=body_part)
        new_symptom_check = SymptomCheck(
            user_id=current_user.id,
            symptoms=symptoms,
            body_part=body_part,
            condition=diagnosis['condition'],
            probability=diagnosis['probability'],
            icd11=diagnosis['icd11'],
            action=diagnosis['action']
        )
        db.session.add(new_symptom_check)
        db.session.commit()
        flash(f'Chẩn đoán triệu chứng: {diagnosis["condition"]} (Xác suất: {diagnosis["probability"]*100:.1f}%, Mã ICD-11: {diagnosis["icd11"]}). {diagnosis["action"]}', 'info')
        return redirect(url_for('main.dashboard'))

    if form.validate_on_submit():
        age = form.age.data
        bmi = form.bmi.data
        glucose = form.glucose.data
        heart_rate = form.heart_rate.data
        diagnosis = ai_diagnosis(age=age, bmi=bmi, glucose=glucose, heart_rate=heart_rate)
        new_prediction = Prediction(
            user_id=current_user.id,
            age=age,
            bmi=bmi,
            glucose=glucose,
            heart_rate=heart_rate,
            result=diagnosis['result'],
        )
        db.session.add(new_prediction)
        db.session.commit()
        flash(f'Chẩn đoán sức khỏe: {diagnosis["result"]} (Xác suất: {diagnosis["probability"]*100:.1f}%). {diagnosis["disclaimer"]}', 'success')
        return redirect(url_for('main.dashboard'))
    
    try:
        csv_path = r"C:\Users\Dell\OneDrive\Pictures\Documents\Code\python\OpenCV\Project\Web\dataset\health_dataset.csv"
        df = pd.read_csv(csv_path)
        
        stats = {
            'age': {
                'mean': round(df['Age'].mean(), 1) if 'Age' in df.columns else 0,
                'max': int(df['Age'].max()) if 'Age' in df.columns else 0,
                'min': int(df['Age'].min()) if 'Age' in df.columns else 0,
                'count': int(df['Age'].count()) if 'Age' in df.columns else 0
            },
            'bmi': {
                'mean': round(df['BMI'].mean(), 1) if 'BMI' in df.columns else 0,
                'max': round(df['BMI'].max(), 1) if 'BMI' in df.columns else 0,
                'min': round(df['BMI'].min(), 1) if 'BMI' in df.columns else 0,
                'count': int(df['BMI'].count()) if 'BMI' in df.columns else 0
            },
            'glucose': {
                'mean': round(df['Glucose'].mean(), 1) if 'Glucose' in df.columns else 0,
                'max': round(df['Glucose'].max(), 1) if 'Glucose' in df.columns else 0,
                'min': round(df['Glucose'].min(), 1) if 'Glucose' in df.columns else 0,
                'count': int(df['Glucose'].count()) if 'Glucose' in df.columns else 0
            },
            'heart_rate': {
                'mean': round(df['HeartRate'].mean(), 1) if 'HeartRate' in df.columns else 0,
                'max': round(df['HeartRate'].max(), 1) if 'HeartRate' in df.columns else 0,
                'min': round(df['HeartRate'].min(), 1) if 'HeartRate' in df.columns else 0,
                'count': int(df['HeartRate'].count()) if 'HeartRate' in df.columns else 0
            },
            'result': {
                'unique': int(df['Result'].nunique()) if 'Result' in df.columns else 0,
                'most_common': df['Result'].mode()[0] if 'Result' in df.columns and not df['Result'].empty else 'N/A'
            }
        }
    except FileNotFoundError:
        flash('Không tìm thấy tệp health_dataset.csv.', 'error')
        stats = {
            'age': {'mean': 0, 'max': 0, 'min': 0, 'count': 0},
            'bmi': {'mean': 0, 'max': 0, 'min': 0, 'count': 0},
            'glucose': {'mean': 0, 'max': 0, 'min': 0, 'count': 0},
            'heart_rate': {'mean': 0, 'max': 0, 'min': 0, 'count': 0},
            'result': {'unique': 0, 'most_common': 'N/A'}
        }
    
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.id).all()
    symptom_checks = SymptomCheck.query.filter_by(user_id=current_user.id).order_by(SymptomCheck.id).all()
    return render_template('dashboard.html', form=form, symptom_form=symptom_form, predictions=predictions, symptom_checks=symptom_checks, username=current_user.username, stats=stats)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UpdateProfileForm()
    password_form = ChangePasswordForm()
    if profile_form.validate_on_submit():
        existing_user = User.query.filter_by(username=profile_form.username.data).first()
        existing_email = User.query.filter_by(email=profile_form.email.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Tên đăng nhập đã tồn tại.', 'error')
            return redirect(url_for('main.profile'))
        if existing_email and existing_email.id != current_user.id:
            flash('Email đã được sử dụng.', 'error')
            return redirect(url_for('main.profile'))
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.bio = profile_form.bio.data if profile_form.bio.data and profile_form.bio.data.strip() else None
        current_user.notifications = profile_form.notifications.data
        db.session.commit()
        new_history = ProfileHistory(
            user_id=current_user.id,
            action='Cập nhật thông tin hồ sơ'
        )
        db.session.add(new_history)
        db.session.commit()
        flash('Cập nhật thông tin hồ sơ thành công!', 'success')
        return redirect(url_for('main.profile'))
    profile_form.username.data = current_user.username
    profile_form.email.data = current_user.email
    profile_form.bio.data = current_user.bio
    profile_form.notifications.data = current_user.notifications
    profile_history = ProfileHistory.query.filter_by(user_id=current_user.id).order_by(ProfileHistory.timestamp.desc()).all()
    current_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return render_template('profile.html', form=profile_form, password_form=password_form, profile_history=profile_history, current_time=current_time)

@main_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Chỉ admin mới có quyền truy cập.', 'error')
        return redirect(url_for('main.dashboard'))
    
    delete_form = DeleteConfirmForm()
    search_query = request.args.get('search', '')

    if request.method == 'POST':
        if delete_form.validate_on_submit():
            user_id = request.form.get('user_ids')
            print(f"Received user_id: {user_id}, type: {type(user_id)}")
            if not user_id:
                flash('Không tìm thấy ID người dùng để xóa.', 'error')
                return redirect(url_for('main.admin_panel', search=search_query))
            
            try:
                user_id = int(user_id)
            except ValueError:
                print(f"Invalid user_id format: {user_id}")
                flash('ID người dùng không hợp lệ.', 'error')
                return redirect(url_for('main.admin_panel', search=search_query))
            
            user_to_delete = User.query.get(user_id)
            if user_to_delete:
                print(f"Found user to delete: {user_to_delete.username}, ID: {user_to_delete.id}")
                if user_to_delete.is_admin:
                    flash('Không thể xóa tài khoản admin.', 'error')
                elif user_to_delete.id == current_user.id:
                    flash('Không thể xóa tài khoản của chính bạn.', 'error')
                else:
                    if check_password_hash(current_user.password_hash, delete_form.password.data):
                        Prediction.query.filter_by(user_id=user_id).delete()
                        SymptomCheck.query.filter_by(user_id=user_id).delete()
                        ProfileHistory.query.filter_by(user_id=user_id).delete()
                        db.session.delete(user_to_delete)
                        try:
                            db.session.commit()
                            flash('Tài khoản đã được xóa thành công.', 'success')
                        except Exception as e:
                            db.session.rollback()
                            flash(f'Lỗi khi xóa tài khoản: {str(e)}', 'error')
                            print(f"Error during deletion: {str(e)}")
                    else:
                        flash('Mật khẩu xác nhận không đúng.', 'error')
            else:
                print(f"No user found with ID: {user_id}")
                flash('Không tìm thấy tài khoản để xóa.', 'error')
            return redirect(url_for('main.admin_panel', search=search_query))

    if search_query:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) | (User.email.ilike(f'%{search_query}%'))
        ).all()
        searched_predictions = Prediction.query.filter(Prediction.user_id.in_([user.id for user in users])).all()
        searched_symptom_checks = SymptomCheck.query.filter(SymptomCheck.user_id.in_([user.id for user in users])).all()
    else:
        users = User.query.all()
        searched_predictions = []
        searched_symptom_checks = []
    predictions = Prediction.query.all()
    symptom_checks = SymptomCheck.query.all()
    return render_template('admin.html', users=users, predictions=predictions, delete_form=delete_form, search_query=search_query, symptom_checks=symptom_checks, searched_predictions=searched_predictions, searched_symptom_checks=searched_symptom_checks)

@main_bp.route('/export_pdf', methods=['GET'])
@login_required
def export_pdf():
    predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Báo cáo sức khỏe của {current_user.username}", styles['Title']))

    data = [['Tuổi', 'BMI', 'Glucose', 'Nhịp tim', 'Kết quả', 'Xác suất']]
    for p in predictions:
        result_style = 'Normal' if p.result == 'No Risk' else 'Heading5'
        data.append([
            str(p.age),
            str(p.bmi),
            str(p.glucose),
            str(p.heart_rate),
            Paragraph(p.result, styles[result_style]),
            f"{(p.probability * 100):.1f}%"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6fffa' if p.result == 'No Risk' else '#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=health_report.pdf'
    return response

@main_bp.route('/export_symptom_pdf', methods=['GET'])
@login_required
def export_symptom_pdf():
    symptom_checks = SymptomCheck.query.filter_by(user_id=current_user.id).all()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Báo cáo kiểm tra triệu chứng của {current_user.username}", styles['Title']))

    data = [['Triệu chứng', 'Bộ phận cơ thể', 'Chẩn đoán', 'Xác suất', 'Mã ICD-11', 'Hành động', 'Thời gian']]
    for sc in symptom_checks:
        data.append([
            sc.symptoms,
            sc.body_part.capitalize(),
            sc.condition,
            f"{(sc.probability * 100):.1f}%",
            sc.icd11,
            sc.action,
            sc.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6fffa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=symptom_report.pdf'
    return response

def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Không tìm thấy file ảnh.', 'error')
        return redirect(url_for('main.profile'))
    file = request.files['avatar']
    if file.filename == '':
        flash('Vui lòng chọn một file ảnh.', 'error')
        return redirect(url_for('main.profile'))
    if file and allowed_file(file.filename):
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
        if not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
            except OSError as e:
                flash(f'Không thể tạo thư mục lưu ảnh: {str(e)}', 'error')
                return redirect(url_for('main.profile'))
        old_extension = session.get('avatar_extension', None)
        if old_extension and current_user.avatar:
            old_file_path = os.path.join(upload_folder, f"{current_user.username}.{old_extension}")
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    print(f"Deleted old avatar: {old_file_path}")
                except Exception as e:
                    print(f"Error deleting old avatar: {str(e)}")
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{current_user.username}.{extension}")
        file_path = os.path.join(upload_folder, filename)
        try:
            file.save(file_path)
            if os.path.exists(file_path):
                current_user.avatar = True
                session['avatar_extension'] = extension
                new_history = ProfileHistory(
                    user_id=current_user.id,
                    action=f'Cập nhật avatar - Ảnh đại diện đã được cập nhật với tên {filename}'
                )
                db.session.add(new_history)
                db.session.commit()
                flash('Cập nhật ảnh đại diện thành công!', 'success')
            else:
                flash('Lỗi: Không thể lưu ảnh vào hệ thống.', 'error')
            return redirect(url_for('main.profile'))
        except Exception as e:
            flash(f'Lỗi khi lưu file: {str(e)}', 'error')
            print(f"Error saving avatar: {str(e)}")
            return redirect(url_for('main.profile'))
    flash('Định dạng file không được hỗ trợ.', 'error')
    return redirect(url_for('main.profile'))

@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            new_history = ProfileHistory(
                user_id=current_user.id,
                action='Đổi mật khẩu - Mật khẩu đã được cập nhật'
            )
            db.session.add(new_history)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
        else:
            flash('Mật khẩu hiện tại không đúng.', 'error')
        return redirect(url_for('main.profile'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Lỗi: {error}', 'error')
    return redirect(url_for('main.profile'))

@main_bp.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    data = request.get_json()
    enabled = data.get('enabled', False)
    current_user.notifications = enabled
    db.session.commit()
    new_history = ProfileHistory(
        user_id=current_user.id,
        action=f"{'Bật' if enabled else 'Tắt'} thông báo email"
    )
    db.session.add(new_history)
    db.session.commit()
    return jsonify({'success': True})