from datetime import datetime, timedelta
import secrets
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """ユーザーモデル"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    
    # プロフィール情報
    bio = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # アカウント状態
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 検証用トークン
    verification_token = db.Column(db.String(64), index=True, unique=True)
    verification_token_expires_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_verified(self):
        """ユーザーのメール検証済みフラグを設定"""
        self.email_verified = True
        self.verification_token = None
        self.verification_token_expires_at = None
    
    def generate_verification_token(self, expires_in=86400):
        """新しい検証トークンを生成"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        return self.verification_token

    @staticmethod
    def verify_reset_token(token):
        """検証トークンによりユーザーを検索"""
        user = User.query.filter_by(
            verification_token=token
        ).filter(User.verification_token_expires_at > datetime.utcnow()).first()
        return user

    def update_last_seen(self):
        """最終ログイン時間を更新"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class Post(db.Model):
    """投稿モデル（ダミー）"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Post {self.id} by User {self.user_id}>'