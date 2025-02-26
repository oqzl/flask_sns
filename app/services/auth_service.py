from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from flask import current_app, url_for

from app.models.user import User
from app.repository.user_repository import UserRepository
from app.services.email_service import EmailService


class AuthService:
    """認証関連の処理を行うサービスクラス"""
    
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def register_user(self, email: str) -> Tuple[bool, str, Optional[User]]:
        """新規ユーザー登録処理
        
        Args:
            email: 登録するメールアドレス
            
        Returns:
            (成功フラグ, メッセージ, ユーザーインスタンス)
        """
        # 既存ユーザーチェック
        existing_user = self.user_repository.find_by_email(email)
        if existing_user:
            if existing_user.email_verified:
                return (False, "このメールアドレスは既に登録されています", None)
            else:
                # 未検証の場合は再度トークンを生成して送信
                user = existing_user
        else:
            # 新規ユーザー作成
            user = self.user_repository.create_user(email)
        
        # 検証トークン生成
        expiry_seconds = int(current_app.config['EMAIL_VERIFICATION_EXPIRY'].total_seconds())
        token = self.user_repository.generate_verification_token(user, expiry_seconds)
        
        # 検証メール送信
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        self.email_service.send_verification_email(user.email, verification_url)
        
        return (True, "確認メールを送信しました。メール内のリンクをクリックして登録を完了してください", user)
    
    def verify_email(self, token: str) -> Tuple[bool, str, Optional[User]]:
        """メールアドレス検証処理
        
        Args:
            token: 検証トークン
            
        Returns:
            (成功フラグ, メッセージ, ユーザーインスタンス)
        """
        user = self.user_repository.find_by_verification_token(token)
        if not user:
            return (False, "無効または期限切れのトークンです", None)
        
        # メール検証フラグを設定
        user = self.user_repository.mark_email_verified(user)
        
        return (True, "メールアドレスの確認が完了しました", user)
    
    def complete_registration(self, user_id: int, username: str) -> Tuple[bool, str, Optional[User]]:
        """ユーザー登録完了処理（ユーザー名設定）
        
        Args:
            user_id: ユーザーID
            username: 設定するユーザー名
            
        Returns:
            (成功フラグ, メッセージ, ユーザーインスタンス)
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return (False, "ユーザーが見つかりません", None)
        
        if not user.email_verified:
            return (False, "メールアドレスが確認されていません", None)
        
        # ユーザー名重複チェック
        if username != user.username:  # 変更がある場合のみチェック
            existing_user = self.user_repository.find_by_username(username)
            if existing_user and existing_user.id != user.id:
                return (False, "このユーザー名は既に使用されています", None)
        
        # ユーザー名更新
        user = self.user_repository.update_username(user, username)
        
        return (True, "アカウント設定が完了しました", user)
