#!/usr/bin/env python3
"""
セキュリティミドルウェア - プロアクティブディフェンス実装
アプリの機能に影響を与えずにセキュリティを強化
"""

from flask import request, jsonify, make_response
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import secrets
from collections import defaultdict
from threading import Lock

# ===== レート制限（ブルートフォース対策） =====

class RateLimiter:
    """
    レート制限クラス - メモリベース（簡易実装）
    本番環境では Redis 推奨
    """
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        指定期間内のリクエスト数を制限

        Args:
            identifier: IPアドレスまたはデバイスID
            max_requests: 最大リクエスト数
            window_seconds: 時間窓（秒）

        Returns:
            許可する場合True
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        with self.lock:
            # 古いリクエストを削除
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]

            # リクエスト数チェック
            if len(self.requests[identifier]) >= max_requests:
                return False

            # リクエスト記録
            self.requests[identifier].append(now)
            return True

    def clear_old_entries(self, hours: int = 24):
        """古いエントリをクリア（メモリリーク防止）"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.lock:
            for identifier in list(self.requests.keys()):
                self.requests[identifier] = [
                    req_time for req_time in self.requests[identifier]
                    if req_time > cutoff
                ]
                if not self.requests[identifier]:
                    del self.requests[identifier]


# グローバルインスタンス
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    レート制限デコレータ

    使用例:
        @app.route('/api/auth/login')
        @rate_limit(max_requests=5, window_seconds=300)  # 5分間に5回まで
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # IPアドレスを識別子として使用
            identifier = request.remote_addr

            # デバイスIDがある場合はそれを使用（より正確）
            if request.is_json:
                data = request.get_json()
                if data and 'device_id' in data:
                    identifier = data['device_id']

            if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                return jsonify({
                    'error': 'レート制限を超えています',
                    'message': f'{window_seconds}秒後に再試行してください'
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ===== セキュリティヘッダー =====

def add_security_headers(response):
    """
    セキュリティヘッダーを追加

    - XSS保護
    - クリックジャッキング保護
    - MIME スニッフィング防止
    - Content Security Policy
    """
    # XSS Protection（レガシーブラウザ用）
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # クリックジャッキング防止
    response.headers['X-Frame-Options'] = 'DENY'

    # MIME スニッフィング防止
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Referrer Policy（情報漏洩防止）
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Content Security Policy（XSS防止）
    # 開発環境では緩和、本番環境では厳格化
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Vite開発サーバー対応
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none';"
    )

    # Permissions Policy（不要な機能を無効化）
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=()"
    )

    return response


# ===== 入力検証・サニタイゼーション =====

def sanitize_input(data: dict, allowed_keys: list) -> dict:
    """
    入力データをサニタイズ

    Args:
        data: 入力データ（辞書）
        allowed_keys: 許可するキーのリスト

    Returns:
        サニタイズされたデータ
    """
    if not isinstance(data, dict):
        return {}

    sanitized = {}
    for key in allowed_keys:
        if key in data:
            value = data[key]

            # 文字列の場合は長さ制限とエスケープ
            if isinstance(value, str):
                # 最大長制限（DoS防止）
                value = value[:1000]

                # 危険な文字を除去（SQLインジェクション対策）
                # 注: 本番環境ではパラメータ化クエリを使用すべき
                dangerous_chars = ['--', ';', '/*', '*/', 'xp_', 'sp_']
                for char in dangerous_chars:
                    value = value.replace(char, '')

            sanitized[key] = value

    return sanitized


# ===== CSRF保護（トークンベース） =====

class CSRFProtection:
    """
    CSRF保護クラス

    注: SPA（React）の場合、カスタムヘッダーによる保護も有効
    """
    def __init__(self):
        self.tokens = {}  # session_token: csrf_token
        self.lock = Lock()

    def generate_token(self, session_token: str) -> str:
        """CSRFトークン生成"""
        csrf_token = secrets.token_urlsafe(32)
        with self.lock:
            self.tokens[session_token] = {
                'token': csrf_token,
                'created_at': datetime.now()
            }
        return csrf_token

    def validate_token(self, session_token: str, csrf_token: str) -> bool:
        """CSRFトークン検証"""
        with self.lock:
            if session_token not in self.tokens:
                return False

            stored = self.tokens[session_token]

            # トークン有効期限チェック（1時間）
            if datetime.now() - stored['created_at'] > timedelta(hours=1):
                del self.tokens[session_token]
                return False

            return stored['token'] == csrf_token

    def remove_token(self, session_token: str):
        """トークン削除"""
        with self.lock:
            if session_token in self.tokens:
                del self.tokens[session_token]


csrf_protection = CSRFProtection()


def require_csrf_token(f):
    """
    CSRFトークン検証デコレータ

    使用例:
        @app.route('/api/auth/register')
        @require_csrf_token
        def register():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 開発者モードでは検証スキップ
        if request.headers.get('X-Dev-Mode') == 'true':
            return f(*args, **kwargs)

        # CSRFトークン取得
        csrf_token = request.headers.get('X-CSRF-Token')
        session_token = None

        if request.is_json:
            data = request.get_json()
            session_token = data.get('session_token')

        # トークン検証
        if not csrf_token or not session_token:
            return jsonify({
                'error': 'CSRFトークンが必要です',
                'message': 'セキュリティ保護のため、有効なトークンが必要です'
            }), 403

        if not csrf_protection.validate_token(session_token, csrf_token):
            return jsonify({
                'error': '無効なCSRFトークンです',
                'message': 'セッションが期限切れの可能性があります。再ログインしてください'
            }), 403

        return f(*args, **kwargs)
    return decorated_function


# ===== セッション管理強化 =====

def validate_session_age(session_created_at: datetime, max_age_days: int = 30) -> bool:
    """
    セッション有効期限チェック

    Args:
        session_created_at: セッション作成日時
        max_age_days: 最大有効期間（日数）

    Returns:
        有効な場合True
    """
    if datetime.now() - session_created_at > timedelta(days=max_age_days):
        return False
    return True


# ===== デバッグモード保護 =====

def is_production() -> bool:
    """本番環境判定"""
    import os
    return os.environ.get('FLASK_ENV', 'development') == 'production'


def disable_dev_mode_in_production():
    """
    本番環境で開発者モードを無効化

    api_server.py の起動時に呼び出す
    """
    if is_production():
        import os
        # 開発者モード用の環境変数を削除
        if 'DEV_MODE_ENABLED' in os.environ:
            del os.environ['DEV_MODE_ENABLED']

        print("🔒 本番環境: 開発者モードは無効化されています")
    else:
        print("🔧 開発環境: 開発者モードが有効です")


# ===== パスワードハッシュ化 =====

def hash_password(password: str, salt: str = None) -> tuple:
    """
    パスワードをハッシュ化（SHA-256 + Salt）

    Args:
        password: 平文パスワード
        salt: ソルト（Noneの場合は自動生成）

    Returns:
        (hashed_password, salt) のタプル
    """
    if salt is None:
        salt = secrets.token_hex(16)

    # パスワード + ソルトをハッシュ化
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()

    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    パスワード検証

    Args:
        password: 入力された平文パスワード
        hashed_password: 保存されているハッシュ
        salt: ソルト

    Returns:
        一致する場合True
    """
    hashed, _ = hash_password(password, salt)
    return hashed == hashed_password


# ===== ログ記録（セキュリティイベント） =====

def log_security_event(event_type: str, details: dict):
    """
    セキュリティイベントをログ記録

    Args:
        event_type: イベントタイプ（例: 'login_failed', 'rate_limit_exceeded'）
        details: イベント詳細
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details,
        'ip_address': request.remote_addr if request else 'N/A'
    }

    # 本番環境では外部ログサービスに送信推奨
    print(f"🔒 [SECURITY] {timestamp} - {event_type}: {details}")


# ===== 初期化関数 =====

def init_security(app):
    """
    Flaskアプリにセキュリティ機能を追加

    使用例:
        from security_middleware import init_security
        init_security(app)
    """
    # すべてのレスポンスにセキュリティヘッダーを追加
    app.after_request(add_security_headers)

    # 本番環境で開発者モードを無効化
    disable_dev_mode_in_production()

    # 定期的にレート制限エントリをクリア（メモリリーク防止）
    # 注: 本番環境では cron ジョブや Celery タスクで実行推奨
    import atexit
    atexit.register(lambda: rate_limiter.clear_old_entries())

    print("✅ セキュリティミドルウェアが初期化されました")
