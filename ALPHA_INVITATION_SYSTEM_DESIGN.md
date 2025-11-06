# アルファ版招待URL限定配布システム 設計書

## 概要

招待URL方式による1URL=1台限定のアルファ版配布システム

## システム構成

### 1. データベーススキーマ

#### `invite_tokens` テーブル
```sql
CREATE TABLE invite_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,           -- 招待トークン（UUID）
    is_used BOOLEAN DEFAULT 0,             -- 使用済みフラグ
    device_id TEXT,                        -- 登録デバイスID
    registered_at DATETIME,                -- 登録日時
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_sessions` テーブル
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token TEXT UNIQUE NOT NULL,    -- セッショントークン
    device_id TEXT NOT NULL,               -- デバイスID
    invite_token TEXT NOT NULL,            -- 使用した招待トークン
    last_access DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invite_token) REFERENCES invite_tokens(token)
);
```

### 2. 認証フロー

```
[ユーザー]
    ↓
招待URLアクセス: /invite/{token}
    ↓
トークン検証
    ├─ 無効 → エラーページ
    └─ 有効 → 登録ページ表示
         ↓
    メール・パス入力（両方「987」）
         ↓
    デバイスID取得（ブラウザフィンガープリント）
         ↓
    トークンを使用済みに + デバイスID記録
         ↓
    セッション発行 → アプリ画面へ
```

### 3. アクセス制御

- **登録済みデバイス**: アプリ画面表示
- **未登録デバイス**: `/register` へリダイレクト
- **使用済みトークン**: 「この招待URLは既に使用されています」エラー

### 4. API エンドポイント

#### POST `/api/auth/verify-invite`
招待トークン検証
```json
Request: { "token": "uuid-string" }
Response: { "valid": true/false, "message": "..." }
```

#### POST `/api/auth/register`
デバイス登録
```json
Request: {
    "token": "uuid-string",
    "email": "987",
    "password": "987",
    "device_id": "fingerprint-hash"
}
Response: {
    "success": true,
    "session_token": "session-uuid"
}
```

#### POST `/api/auth/verify-session`
セッション検証
```json
Request: {
    "session_token": "session-uuid",
    "device_id": "fingerprint-hash"
}
Response: {
    "valid": true/false,
    "redirect": "/register" (invalid時)
}
```

#### POST `/api/admin/generate-invite` (管理者用)
招待トークン生成
```json
Request: { "count": 10 }
Response: {
    "tokens": [
        "https://example.com/invite/uuid1",
        "https://example.com/invite/uuid2",
        ...
    ]
}
```

### 5. フロントエンド画面構成

#### `/invite/:token` - 招待URLページ
- トークン検証
- 有効なら `/register` へリダイレクト（トークンをstate保持）

#### `/register` - 登録ページ
```
┌─────────────────────────────┐
│  遊技機取扱主任者試験アプリ    │
│    アルファ版登録             │
├─────────────────────────────┤
│                             │
│  メールアドレス: [_______]   │
│  パスワード:     [_______]   │
│                             │
│        [登録して始める]       │
│                             │
│  ※ 招待URLは1台のみ登録可能  │
└─────────────────────────────┘
```

#### `/` - アプリメイン画面
- セッション検証
- 無効なら `/register` へリダイレクト
- 有効なら既存の試験アプリUI表示

### 6. デバイスID取得方法

**FingerprintJS（オープンソース版）**を使用
```javascript
import FingerprintJS from '@fingerprintjs/fingerprintjs';

const fp = await FingerprintJS.load();
const result = await fp.get();
const deviceId = result.visitorId; // ユニークなデバイスID
```

特徴:
- ブラウザ・デバイス情報から一意のIDを生成
- Cookie削除・プライベートモードでも同一ID
- 99.5%の精度

### 7. セキュリティ対策

1. **トークン管理**
   - UUID v4 使用（推測不可）
   - 使用済みトークンの再利用防止

2. **セッション管理**
   - セッショントークンは UUID v4
   - デバイスIDとの二重チェック
   - 最終アクセス時刻更新

3. **レート制限**
   - 登録API: 同一IPから1分間に3回まで
   - セッション検証: 1分間に60回まで

### 8. デプロイ構成

```
[Webサーバー]
    ├─ Nginx (リバースプロキシ)
    ├─ Flask (バックエンドAPI)
    ├─ SQLite (データベース)
    └─ React (フロントエンド静的ファイル)
```

### 9. 管理者機能

#### 招待URL生成ツール
```bash
python3 generate_invites.py --count 10
```

出力例:
```
✅ 10個の招待URLを生成しました:

1. https://example.com/invite/a1b2c3d4-...
2. https://example.com/invite/e5f6g7h8-...
...

📋 URLs.txt に保存しました
```

### 10. 実装優先順位

1. ✅ データベーススキーマ作成
2. ✅ 認証API実装（Flask）
3. ✅ 登録/ログインページ（React）
4. ✅ デバイスID取得・セッション管理
5. ✅ 既存UIへのセッション検証追加
6. ✅ 管理者用招待URL生成ツール
7. ⏳ デプロイ設定（Nginx + Flask）

---

**作成日**: 2025-10-22
**バージョン**: v1.0
**ステータス**: 実装準備完了
