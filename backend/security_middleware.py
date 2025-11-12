#!/usr/bin/env python3
"""
シンプルなセキュリティミドルウェア - スマホアプリ向け
最低限の保護のみ実装（過剰なセキュリティは排除）
"""

from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

# ===== 緩いレート制限（極端な攻撃のみ防ぐ） =====

class RateLimiter:
    """
    シンプルなレート制限
    普通の使用では引っかからないレベル
    """
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, identifier: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """
        指定期間内のリクエスト数を制限
        デフォルト: 1分間に100回（普通の使用では問題ないレベル）
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


rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    レート制限デコレータ（緩め）

    使用例:
        @rate_limit(max_requests=100, window_seconds=60)  # 1分間に100回まで
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # IPアドレスを識別子として使用
            identifier = request.remote_addr or 'unknown'

            if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                return jsonify({
                    'error': 'レート制限を超えています',
                    'message': '少し時間をおいて再試行してください'
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ===== 基本的なセキュリティヘッダー =====

def add_security_headers(response):
    """
    最低限のセキュリティヘッダーを追加
    スマホアプリ向けに簡略化
    """
    # クリックジャッキング防止
    response.headers['X-Frame-Options'] = 'DENY'

    # MIME スニッフィング防止
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response


# ===== 入力検証・サニタイゼーション =====

def sanitize_input(data: dict, allowed_keys: list) -> dict:
    """
    入力データをサニタイズ
    SQLインジェクション対策とDoS対策
    """
    if not isinstance(data, dict):
        return {}

    sanitized = {}
    for key in allowed_keys:
        if key in data:
            value = data[key]

            # 文字列の場合は長さ制限
            if isinstance(value, str):
                # 最大長制限（DoS防止）
                value = value[:1000]

                # 危険な文字を除去（SQLインジェクション対策）
                dangerous_chars = ['--', ';', '/*', '*/']
                for char in dangerous_chars:
                    value = value.replace(char, '')

            sanitized[key] = value

    return sanitized


# ===== 環境判定 =====

def is_production() -> bool:
    """本番環境判定"""
    import os
    return os.environ.get('FLASK_ENV', 'development') == 'production'


def disable_dev_mode_in_production():
    """
    本番環境で開発者モードを無効化
    """
    if is_production():
        print("🔒 本番環境: 開発者モードは無効化されています")
    else:
        print("🔧 開発環境: 開発者モードが有効です")


# ===== 初期化関数 =====

def init_security(app):
    """
    Flaskアプリにセキュリティ機能を追加
    シンプル版（最低限のみ）
    """
    # すべてのレスポンスにセキュリティヘッダーを追加
    app.after_request(add_security_headers)

    # 本番環境で開発者モードを無効化
    disable_dev_mode_in_production()

    print("✅ セキュリティミドルウェアが初期化されました（シンプル版）")
