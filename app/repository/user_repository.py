from typing import Optional, List
from datetime import datetime, timedelta

from app import db
from app.models.user import User


class UserRepository:
    """ユーザーデータを操作するリポジトリクラス"""
    
    @staticmethod
    def create_user(email: str) -> User:
        """新しいユーザーを作成

        Args:
            email: ユーザーのメールアドレス

        Returns:
            作成されたユーザーインスタンス
        """
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        """メールアドレスによりユーザーを検索

        Args:
            email: 検索するメールアドレス

        Returns:
            ユーザーインスタンス、見つからない場合はNone
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        """IDによりユーザーを検索

        Args:
            user_id: 検索するユーザーID

        Returns:
            ユーザーインスタンス、見つからない場合はNone
        """
        return User.query.get(user_id)
    
    @staticmethod
    def find_by_username(username: str) -> Optional[User]:
        """ユーザー名によりユーザーを検索

        Args:
            username: 検索するユーザー名

        Returns:
            ユーザーインスタンス、見つからない場合はNone
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_verification_token(token: str) -> Optional[User]:
        """検証トークンによりユーザーを検索

        Args:
            token: 検索する検証トークン

        Returns:
            ユーザーインスタンス、見つからない場合やトークンが期限切れの場合はNone
        """
        now = datetime.utcnow()
        return User.query.filter(
            User.verification_token == token,
            User.verification_token_expires_at > now
        ).first()
    
    @staticmethod
    def save(user: User) -> User:
        """ユーザー情報を保存

        Args:
            user: 保存するユーザーインスタンス

        Returns:
            保存されたユーザーインスタンス
        """
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_username(user: User, username: str) -> User:
        """ユーザー名を更新

        Args:
            user: 更新するユーザーインスタンス
            username: 新しいユーザー名

        Returns:
            更新されたユーザーインスタンス
        """
        user.username = username
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def mark_email_verified(user: User) -> User:
        """メール検証済みに設定

        Args:
            user: 更新するユーザーインスタンス

        Returns:
            更新されたユーザーインスタンス
        """
        user.set_verified()
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def generate_verification_token(user: User, expires_in: int = 86400) -> str:
        """検証トークンを生成

        Args:
            user: トークンを生成するユーザー
            expires_in: 有効期限（秒）

        Returns:
            生成されたトークン
        """
        token = user.generate_verification_token(expires_in)
        db.session.add(user)
        db.session.commit()
        return token
