from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from app.repository.user_repository import UserRepository
from app.services.email_service import EmailService
from app.services.auth_service import AuthService


bp = Blueprint('auth', __name__, url_prefix='/auth')

# フォーム
class RegisterForm(FlaskForm):
    email = EmailField('メールアドレス', validators=[DataRequired(), Email()])
    submit = SubmitField('登録')


class SetupAccountForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('完了')
    
    def validate_username(self, username):
        # 使用不可の文字をチェック
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('ユーザー名には英数字とアンダースコアのみ使用できます')


# サービスのインスタンス化
user_repository = UserRepository()
email_service = EmailService()
auth_service = AuthService(user_repository, email_service)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """新規ユーザー登録"""
    if current_user.is_authenticated:
        return redirect(url_for('timeline.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        success, message, user = auth_service.register_user(form.email.data)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン画面（メールログインリンク用）"""
    if current_user.is_authenticated:
        return redirect(url_for('timeline.home'))
    
    # メールリンクでのログインを促すページを表示
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            user = user_repository.find_by_email(email)
            if user and user.email_verified:
                # トークン生成・送信
                token = user_repository.generate_verification_token(user)
                login_url = url_for('auth.verify_email', token=token, _external=True)
                email_service.send_verification_email(user.email, login_url)
                flash('ログイン用のメールを送信しました。メール内のリンクをクリックしてログインしてください', 'info')
            else:
                flash('このメールアドレスは登録されていないか、確認が完了していません', 'warning')
    
    return render_template('auth/login.html')


@bp.route('/verify/<token>')
def verify_email(token):
    """メールアドレス検証とログイン"""
    success, message, user = auth_service.verify_email(token)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('auth.login'))
    
    # ユーザーをログイン状態にする
    login_user(user, remember=True)
    flash(message, 'success')
    
    # ユーザー名が設定されていない場合はアカウント設定ページへ
    if not user.username:
        return redirect(url_for('auth.setup_account'))
    
    # 設定済みの場合はホームへ
    return redirect(url_for('timeline.home'))


@bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_account():
    """アカウント設定（ユーザー名設定）"""
    # 既に設定済みの場合はホームへ
    if current_user.username:
        return redirect(url_for('timeline.home'))
    
    form = SetupAccountForm()
    
    if form.validate_on_submit():
        success, message, user = auth_service.complete_registration(
            current_user.id, form.username.data)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('timeline.home'))
    
    return render_template('auth/setup_account.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """ログアウト処理"""
    logout_user()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))
