#!/usr/bin/env python3
"""
アルファ版招待URL限定配布システム - データベース管理
✨ ユーザー情報管理機能追加（メール、デバイス種類）
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# データベースパス
DB_PATH = Path(__file__).parent / "alpha_auth.db"


class AuthDatabase:
    """認証データベース管理クラス"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """データベース初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS invite_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    device_id TEXT,
                    registered_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT UNIQUE NOT NULL,
                    device_id TEXT NOT NULL,
                    invite_token TEXT NOT NULL,
                    last_access DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (invite_token) REFERENCES invite_tokens(token)
                )
            """)

            # ✨ ユーザー情報テーブル（新規）
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT UNIQUE NOT NULL,
                    email TEXT,
                    device_type TEXT,
                    user_agent TEXT,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """)

            conn.commit()

    def generate_invite_tokens(self, count: int = 1) -> List[str]:
        """招待トークン生成"""
        tokens = []
        with sqlite3.connect(self.db_path) as conn:
            for _ in range(count):
                token = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO invite_tokens (token) VALUES (?)",
                    (token,)
                )
                tokens.append(token)
            conn.commit()
        return tokens

    def verify_invite_token(self, token: str) -> Dict:
        """招待トークン検証"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM invite_tokens WHERE token = ?",
                (token,)
            )
            row = cursor.fetchone()

            if not row:
                return {"valid": False, "message": "無効な招待URLです"}

            if row['is_used']:
                return {
                    "valid": False,
                    "message": "この招待URLは既に使用されています"
                }

            return {"valid": True, "message": "有効な招待URLです"}

    def register_device(self, token: str, device_id: str, email: str = None,
                       device_type: str = None, user_agent: str = None) -> Dict:
        """
        デバイス登録（拡張版）

        Args:
            token: 招待トークン
            device_id: デバイスID
            email: メールアドレス
            device_type: デバイス種類（Android/iPhone/PC）
            user_agent: User-Agent文字列
        """
        with sqlite3.connect(self.db_path) as conn:
            # トークン検証
            cursor = conn.execute(
                "SELECT is_used, device_id FROM invite_tokens WHERE token = ?",
                (token,)
            )
            row = cursor.fetchone()

            if not row:
                return {"success": False, "message": "無効な招待URLです"}

            # ✅ 同じデバイスからの再アクセスなら許可（複数ブラウザ対応）
            if row[0] and row[1]:  # 既に使用済み
                if row[1] == device_id:
                    # 同じデバイスからの再アクセス → セッション生成のみ
                    session_token = str(uuid.uuid4())
                    conn.execute(
                        """INSERT INTO user_sessions
                           (session_token, device_id, invite_token)
                           VALUES (?, ?, ?)""",
                        (session_token, device_id, token)
                    )
                    conn.commit()
                    return {
                        "success": True,
                        "session_token": session_token,
                        "message": "登録が完了しました"
                    }
                else:
                    # 異なるデバイス → エラー
                    return {
                        "success": False,
                        "message": "この招待URLは既に別のデバイスで使用されています"
                    }

            # デバイス登録
            now = datetime.now().isoformat()
            conn.execute(
                """UPDATE invite_tokens
                   SET is_used = 1, device_id = ?, registered_at = ?
                   WHERE token = ?""",
                (device_id, now, token)
            )

            # ✨ ユーザー情報を保存
            conn.execute(
                """INSERT OR REPLACE INTO users
                   (device_id, email, device_type, user_agent, registered_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (device_id, email, device_type, user_agent, now)
            )

            # セッション作成
            session_token = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO user_sessions
                   (session_token, device_id, invite_token)
                   VALUES (?, ?, ?)""",
                (session_token, device_id, token)
            )

            conn.commit()

            return {
                "success": True,
                "session_token": session_token,
                "message": "登録が完了しました"
            }

    def verify_session(self, session_token: str, device_id: str) -> Dict:
        """セッション検証"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM user_sessions
                   WHERE session_token = ? AND device_id = ?""",
                (session_token, device_id)
            )
            row = cursor.fetchone()

            if not row:
                return {
                    "valid": False,
                    "message": "無効なセッションです",
                    "redirect": "/register"
                }

            # 最終アクセス時刻更新
            now = datetime.now().isoformat()
            conn.execute(
                "UPDATE user_sessions SET last_access = ? WHERE id = ?",
                (now, row['id'])
            )

            # ✨ ユーザーの最終ログイン時刻も更新
            conn.execute(
                "UPDATE users SET last_login = ? WHERE device_id = ?",
                (now, device_id)
            )

            conn.commit()

            return {"valid": True, "message": "有効なセッションです"}

    def get_session_by_device(self, device_id: str) -> Optional[Dict]:
        """デバイスIDからセッション取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM user_sessions
                   WHERE device_id = ?
                   ORDER BY created_at DESC
                   LIMIT 1""",
                (device_id,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_stats(self) -> Dict:
        """統計情報取得"""
        with sqlite3.connect(self.db_path) as conn:
            # 招待トークン統計
            cursor = conn.execute(
                "SELECT COUNT(*) as total, SUM(is_used) as used FROM invite_tokens"
            )
            token_stats = cursor.fetchone()

            # セッション統計
            cursor = conn.execute("SELECT COUNT(*) FROM user_sessions")
            session_count = cursor.fetchone()[0]

            # ユーザー統計
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            return {
                "total_tokens": token_stats[0] or 0,
                "used_tokens": token_stats[1] or 0,
                "available_tokens": (token_stats[0] or 0) - (token_stats[1] or 0),
                "active_sessions": session_count,
                "total_users": user_count
            }

    # ===== 開発者向け機能 =====

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        全ユーザー一覧を取得（開発者ダッシュボード用）

        Args:
            limit: 取得件数
            offset: オフセット

        Returns:
            ユーザー情報のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT
                    u.id,
                    u.device_id,
                    u.email,
                    u.device_type,
                    u.registered_at,
                    u.last_login,
                    COUNT(s.id) as session_count
                FROM users u
                LEFT JOIN user_sessions s ON u.device_id = s.device_id
                GROUP BY u.id
                ORDER BY u.registered_at DESC
                LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """メールアドレスでユーザー検索"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_device_type_stats(self) -> Dict:
        """デバイス種類別の統計"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT device_type, COUNT(*) as count
                   FROM users
                   WHERE device_type IS NOT NULL
                   GROUP BY device_type"""
            )
            rows = cursor.fetchall()

            stats = {"Android": 0, "iPhone": 0, "PC": 0, "Unknown": 0}
            for row in rows:
                device_type = row[0] or "Unknown"
                stats[device_type] = row[1]

            return stats


if __name__ == "__main__":
    # テスト
    db = AuthDatabase()

    print("✅ データベース初期化完了")
    print("\n📊 統計情報:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 招待トークン生成テスト
    print("\n🎫 テスト: 招待トークン生成")
    tokens = db.generate_invite_tokens(3)
    for i, token in enumerate(tokens, 1):
        print(f"  {i}. {token}")

    print("\n✅ テスト完了")
