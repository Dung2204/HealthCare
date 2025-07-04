from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Gửi link đặt lại')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đặt lại mật khẩu')

class HealthForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    bmi = FloatField('BMI', validators=[DataRequired()])
    glucose = FloatField('Glucose', validators=[DataRequired()])
    heart_rate = FloatField('Heart Rate', validators=[DataRequired()])
    submit = SubmitField('Get Diagnosis')

class DeleteConfirmForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm Delete')

class SymptomCheckerForm(FlaskForm):
    """
    Form để nhập triệu chứng và bộ phận cơ thể.
    """
    symptoms = StringField(
        'Triệu chứng (cách nhau bằng dấu phẩy)',
        validators=[
            DataRequired(message='Vui lòng nhập triệu chứng'),
            Length(min=3, message='Triệu chứng phải có ít nhất 3 ký tự')
        ]
    )
    body_part = SelectField(
        'Bộ phận cơ thể',
        choices=[
            ('head', 'Đầu'),
            ('chest', 'Ngực'),
            ('abdomen', 'Bụng'),
            ('limbs', 'Tay/Chân')
        ],
        validators=[DataRequired(message='Vui lòng chọn bộ phận cơ thể')]
    )
    submit = SubmitField('Kiểm tra triệu chứng')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Đổi mật khẩu')

class UpdateProfileForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Mô tả bản thân', validators=[Optional(), Length(max=200)])
    notifications = BooleanField('Bật thông báo email')
    submit = SubmitField('Cập nhật thông tin')