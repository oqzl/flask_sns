import os
from datetime import timedelta


class Config:
    """アプリケーションの設定クラス"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # データベース
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/flask_sns'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # メール設定
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'yes', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'yes', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@sns.local'
    MAIL_DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Resend設定
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    USE_RESEND = os.environ.get('USE_RESEND', 'false').lower() in ['true', 'yes', '1']
    RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL') or 'onboarding@resend.dev'
    
    # セッション設定
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # アプリケーション固有設定
    SNS_ADMIN_EMAIL = os.environ.get('SNS_ADMIN_EMAIL') or 'admin@sns.local'
    EMAIL_VERIFICATION_EXPIRY = timedelta(hours=24)