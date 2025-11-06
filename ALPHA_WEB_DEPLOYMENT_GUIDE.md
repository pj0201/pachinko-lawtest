# アルファ版Webアプリ配布ガイド

## ✅ 結論: Android・iPhone自動対応

**Webアプリ版なら、両プラットフォームを自動対応**

## 🎯 推奨アプローチ: Progressive Web App (PWA)

### なぜWebアプリ版が最適か？

| 項目 | Webアプリ版 | ネイティブアプリ |
|------|------------|-----------------|
| **プラットフォーム対応** | ✅ Android・iPhone自動対応 | ❌ 別々のビルドが必要 |
| **配布方法** | ✅ URLだけでOK | ❌ ストア審査必要 |
| **更新** | ✅ サーバー更新で即座に反映 | ❌ 再ビルド→審査→配布 |
| **招待システム** | ✅ 完璧に統合可能 | ⚠️ 追加実装が必要 |
| **開発コスト** | ✅ 既存コード活用 | ❌ 両OS対応必要 |
| **アルファテスト** | ✅ 最適 | ⚠️ 過剰スペック |

---

## 📱 仕組み: 自動プラットフォーム検出

### ブラウザが自動判別

```javascript
// Reactアプリ内で自動検出
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
const isAndroid = /Android/.test(navigator.userAgent);

// Capacitor使用時も自動判別
import { Capacitor } from '@capacitor/core';
const platform = Capacitor.getPlatform(); // 'web', 'ios', 'android'
```

### ユーザー体験

1. **招待URLアクセス**: `https://yourserver.com/invite/abc-123`
2. **自動判別**: サーバーが User-Agent 自動検出
3. **登録**: メール・パス両方「987」でログイン
4. **アプリ起動**: デバイス登録後、自動的にアプリ画面表示

**Android でも iPhone でも同じフロー！**

---

## 🚀 デプロイ手順（3ステップ）

### ステップ1: Webアプリビルド

```bash
cd /home/planj/patshinko-exam-app

# 本番ビルド（既に実行済み）
npm run build
# → /dist にビルド済み
```

### ステップ2: 招待システム統合

#### 2.1 バックエンドAPIエンドポイント追加

`/backend/app.py` に追加:

```python
from flask import Flask, request, jsonify
from auth_database import AuthDatabase

app = Flask(__name__)
auth_db = AuthDatabase()

# 招待トークン検証
@app.route('/api/auth/verify-invite', methods=['POST'])
def verify_invite():
    data = request.json
    token = data.get('token')
    result = auth_db.verify_invite_token(token)
    return jsonify(result)

# デバイス登録
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    token = data['token']
    device_id = data['device_id']
    email = data['email']
    password = data['password']

    # 認証チェック
    if email != "987" or password != "987":
        return jsonify({"success": False, "message": "認証失敗"}), 401

    result = auth_db.register_device(token, device_id)
    return jsonify(result)

# セッション検証
@app.route('/api/auth/verify-session', methods=['POST'])
def verify_session():
    data = request.json
    session_token = data['session_token']
    device_id = data['device_id']
    result = auth_db.verify_session(session_token, device_id)
    return jsonify(result)

# 管理者用: 招待トークン生成
@app.route('/api/admin/generate-invite', methods=['POST'])
def generate_invite():
    count = request.json.get('count', 10)
    tokens = auth_db.generate_invite_tokens(count)
    base_url = "https://yourserver.com/invite"
    urls = [f"{base_url}/{token}" for token in tokens]
    return jsonify({"tokens": urls})
```

#### 2.2 フロントエンド: 登録ページ作成

`/src/pages/Register.jsx`:

```jsx
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  useEffect(() => {
    // デバイスID取得
    FingerprintJS.load().then(fp => {
      fp.get().then(result => {
        setDeviceId(result.visitorId);
      });
    });

    // トークン検証
    if (token) {
      fetch('/api/auth/verify-invite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      })
      .then(res => res.json())
      .then(data => {
        if (!data.valid) {
          setError(data.message);
        }
      });
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, device_id: deviceId, email, password })
    });

    const data = await response.json();

    if (data.success) {
      // セッショントークン保存
      localStorage.setItem('session_token', data.session_token);
      localStorage.setItem('device_id', deviceId);
      navigate('/');
    } else {
      setError(data.message);
    }
  };

  return (
    <div className="register-container">
      <h1>遊技機取扱主任者試験アプリ</h1>
      <h2>アルファ版登録</h2>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="メールアドレス"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="パスワード"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">登録して始める</button>
      </form>

      <p className="note">※ 招待URLは1台のみ登録可能</p>
    </div>
  );
}
```

#### 2.3 セッション検証ミドルウェア

`/src/components/ProtectedRoute.jsx`:

```jsx
import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const [isValid, setIsValid] = useState(null);

  useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');

    if (!sessionToken || !deviceId) {
      setIsValid(false);
      return;
    }

    fetch('/api/auth/verify-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: sessionToken, device_id: deviceId })
    })
    .then(res => res.json())
    .then(data => {
      setIsValid(data.valid);
    });
  }, []);

  if (isValid === null) return <div>Loading...</div>;
  if (!isValid) return <Navigate to="/register" />;

  return children;
}
```

### ステップ3: サーバーにデプロイ

#### オプション1: Nginx + Flask

```bash
# Nginx設定
sudo nano /etc/nginx/sites-available/patshinko

# 内容:
server {
    listen 80;
    server_name yourserver.com;

    # Webアプリ（静的ファイル）
    root /var/www/patshinko/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # バックエンドAPI
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 有効化
sudo ln -s /etc/nginx/sites-available/patshinko /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### オプション2: Heroku

```bash
# heroku.yml 作成
echo "web: python3 backend/app.py" > Procfile
git add .
git commit -m "Deploy alpha version"
heroku create patshinko-exam-alpha
git push heroku master
```

---

## 🎫 招待URL生成ツール

`/backend/generate_invites.py`:

```python
#!/usr/bin/env python3
from auth_database import AuthDatabase
import sys

def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    db = AuthDatabase()
    tokens = db.generate_invite_tokens(count)

    base_url = "https://yourserver.com/invite"

    print(f"✅ {count}個の招待URLを生成しました:\n")

    with open("invite_urls.txt", "w") as f:
        for i, token in enumerate(tokens, 1):
            url = f"{base_url}/{token}"
            print(f"{i}. {url}")
            f.write(url + "\n")

    print(f"\n📋 invite_urls.txt に保存しました")

if __name__ == "__main__":
    main()
```

**使用方法**:
```bash
cd /home/planj/patshinko-exam-app/backend
python3 generate_invites.py 10  # 10個生成
```

---

## 📊 プラットフォーム別の自動最適化

### CSS Media Queries

```css
/* iOS Safari 特有のスタイル */
@supports (-webkit-touch-callout: none) {
  .app-container {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

/* Android Chrome 特有のスタイル */
@media (max-width: 600px) {
  .button {
    min-height: 48px; /* Android タッチターゲット */
  }
}
```

### JavaScript プラットフォーム検出

```javascript
// プラットフォーム別の振る舞い
const platform = {
  isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent),
  isAndroid: /Android/.test(navigator.userAgent),
  isMobile: /Mobile|Android|iPhone/.test(navigator.userAgent)
};

// iOS の場合、スクロールバウンス無効化
if (platform.isIOS) {
  document.body.style.overscrollBehavior = 'none';
}

// Android の場合、戻るボタン対応
if (platform.isAndroid) {
  window.addEventListener('popstate', (e) => {
    // カスタム戻る処理
  });
}
```

---

## 🔐 セキュリティ対策

### 1. HTTPS必須

```bash
# Let's Encrypt（無料SSL）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourserver.com
```

### 2. CORS設定

```python
# /backend/app.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://yourserver.com"])
```

### 3. レート制限

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    # ...
```

---

## 📈 アルファテスト → 本番移行

### アルファ版（現在）

- ✅ Webアプリ版
- ✅ 招待URL限定配布
- ✅ Android・iPhone自動対応
- ✅ 簡単に更新可能

### 本番版（将来）

- ⏳ ネイティブアプリ（Android APK + iOS IPA）
- ⏳ Google Play + App Store配布
- ⏳ ProGuard難読化（Android）
- ⏳ ビットコード最適化（iOS）

**Webアプリでテスト → 成功したらネイティブ化**

---

## 🐛 トラブルシューティング

### Q: iPhoneで「ホーム画面に追加」できない

A: PWA manifest.json を設定:

```json
{
  "name": "遊技機取扱主任者試験アプリ",
  "short_name": "遊技機試験",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3f51b5",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Q: Androidで通知が表示されない

A: Service Worker を設定（通知が必要な場合）

---

## 📝 まとめ

| 質問 | 回答 |
|------|------|
| **AndroidとiPhoneを自動対応？** | ✅ はい、Webアプリ版なら自動対応 |
| **招待URL限定配布は可能？** | ✅ はい、完全に実現可能 |
| **1台のみ登録制限は可能？** | ✅ はい、デバイスフィンガープリントで実現 |
| **ネイティブアプリは不要？** | ⚠️ アルファ版では不要、本番は検討 |

**推奨**: まずWebアプリ版でアルファテスト → 成功したらネイティブアプリ化

---

**作成日**: 2025-10-22
**対象**: アルファ版配布
**対応環境**: Android・iPhone（ブラウザ）
