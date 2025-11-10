#!/usr/bin/env python3
"""
アルファ版招待URL限定配布システム - データベース管理
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
                    email TEXT,
                    username TEXT,
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

    def register_device(self, token: str, device_id: str, email: str = None, username: str = None) -> Dict:
        """デバイス登録"""
        with sqlite3.connect(self.db_path) as conn:
            # トークン検証
            cursor = conn.execute(
                "SELECT is_used, device_id, email, username FROM invite_tokens WHERE token = ?",
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
                        "email": row[2],
                        "username": row[3],
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
                   SET is_used = 1, device_id = ?, email = ?, username = ?, registered_at = ?
                   WHERE token = ?""",
                (device_id, email, username, now, token)
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
                "email": email,
                "username": username,
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

    def login_with_credentials(self, email: str, username: str, device_id: str) -> Dict:
        """メールアドレスとユーザー名でログイン認証"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT token, device_id FROM invite_tokens
                   WHERE email = ? AND username = ? AND is_used = 1""",
                (email, username)
            )
            row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "message": "メールアドレスまたはユーザー名が正しくありません"
                }

            # デバイスIDの確認（登録したデバイスと同じか）
            if row['device_id'] != device_id:
                return {
                    "success": False,
                    "message": "このアカウントは別のデバイスで登録されています"
                }

            # 新しいセッショントークンを生成
            session_token = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO user_sessions
                   (session_token, device_id, invite_token)
                   VALUES (?, ?, ?)""",
                (session_token, device_id, row['token'])
            )
            conn.commit()

            return {
                "success": True,
                "session_token": session_token,
                "email": email,
                "username": username,
                "message": "ログインしました"
            }

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

            return {
                "total_tokens": token_stats[0] or 0,
                "used_tokens": token_stats[1] or 0,
                "available_tokens": (token_stats[0] or 0) - (token_stats[1] or 0),
                "active_sessions": session_count
            }


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
