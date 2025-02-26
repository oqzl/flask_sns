from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.user import Post
from app.repository.user_repository import UserRepository

bp = Blueprint('timeline', __name__)

user_repository = UserRepository()


@bp.route('/')
def index():
    """インデックスページ（未ログイン時は登録画面、ログイン済みはホーム画面）"""
    if current_user.is_authenticated:
        return redirect(url_for('timeline.home'))
    else:
        return redirect(url_for('auth.register'))


@bp.route('/home')
@login_required
def home():
    """ホームタイムライン"""
    # ユーザー名が設定されていない場合は設定ページへリダイレクト
    if not current_user.username:
        flash('ユーザー名を設定してください', 'warning')
        return redirect(url_for('auth.setup_account'))
    
    # ダミーの投稿データを作成
    posts = [
        {
            'author': {'username': 'Akira'},
            'body': 'こんにちは！Flaskでのアプリ開発楽しいですね！',
            'timestamp': '2時間前'
        },
        {
            'author': {'username': 'Yuki'},
            'body': 'PostgreSQLとの連携に苦戦してます...',
            'timestamp': '4時間前'
        },
        {
            'author': {'username': 'Takeshi'},
            'body': 'Dockerが便利すぎてびっくり！',
            'timestamp': '1日前'
        },
        {
            'author': {'username': current_user.username},
            'body': 'はじめまして！よろしくお願いします。',
            'timestamp': 'たった今'
        }
    ]
    
    return render_template('timeline/home.html', posts=posts)
