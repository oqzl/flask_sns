from typing import Optional, List
from flask import current_app, render_template
from flask_mailman import EmailMessage
import resend

from app import mail


class EmailService:
    """メール送信関連の処理を行うサービスクラス"""
    
    @staticmethod
    def send_email(subject: str, recipients: List[str], body: str, html_body: Optional[str] = None) -> None:
        """メール送信処理
        
        Args:
            subject: メールの件名
            recipients: 宛先メールアドレスのリスト
            body: プレーンテキスト本文
            html_body: HTML本文（省略可）
        """
        # 開発環境では実際のメール送信をスキップしてコンソールに出力（MAIL_DEBUGがTrueかつUSE_RESENDがFalseの場合）
        if current_app.config.get('MAIL_DEBUG', False) and not current_app.config.get('USE_RESEND', False):
            print("\n" + "-" * 80)
            print(f"送信メール（開発モード - 実際には送信されません）")
            print(f"宛先: {', '.join(recipients)}")
            print(f"件名: {subject}")
            print("-" * 80)
            print(body)
            if html_body:
                print("\nHTML本文:")
                print(html_body)
            print("-" * 80 + "\n")
            
            # 開発モードでも検証用URLを利用可能にするために、URLログを別に出力
            if 'verify_email' in body:
                # URLを抽出（シンプルな方法）
                import re
                urls = re.findall(r'https?://\S+', body)
                if urls:
                    print("\n検証URL (これをクリックしてテスト):")
                    for url in urls:
                        print(url)
                    print("\n")
            
            return
        
        # Resendを使用する場合
        if current_app.config.get('USE_RESEND', False):
            resend_api_key = current_app.config.get('RESEND_API_KEY')
            if not resend_api_key:
                print("Error: RESEND_API_KEY is not configured")
                return
            
            from_email = current_app.config.get('RESEND_FROM_EMAIL')
            
            # Resend APIキーを設定
            resend.api_key = resend_api_key
            
            # メール送信
            try:
                params = {
                    "from": from_email,
                    "to": recipients,
                    "subject": subject,
                }
                
                # テキストまたはHTML本文を設定
                if html_body:
                    params["html"] = html_body
                else:
                    params["text"] = body
                
                response = resend.Emails.send(params)
                print(f"Resendメール送信成功: {response['id']}")
            except Exception as e:
                print(f"Resendメール送信エラー: {str(e)}")
            
            return
        
        # 標準のメール送信（Flask-Mailman）
        msg = EmailMessage(
            subject=subject,
            body=body,
            to=recipients
        )
        
        if html_body:
            msg.content_subtype = 'html'
            msg.body = html_body
        
        msg.send()
    
    @staticmethod
    def send_verification_email(recipient: str, verification_url: str) -> None:
        """メールアドレス検証メール送信
        
        Args:
            recipient: 宛先メールアドレス
            verification_url: 検証用URL
        """
        subject = "【SNS】メールアドレスの確認"
        
        text_body = f"""
こんにちは、

以下のURLをクリックしてメールアドレスの確認を完了してください:
{verification_url}

このメールに心当たりがない場合は無視してください。
        """
        
        html_body = f"""
<p>こんにちは、</p>
<p>以下のリンクをクリックしてメールアドレスの確認を完了してください:</p>
<p><a href="{verification_url}">{verification_url}</a></p>
<p>このメールに心当たりがない場合は無視してください。</p>
        """
        
        EmailService.send_email(subject, [recipient], text_body, html_body)
