# 🚀 セキュリティ機能統合ガイド

このドキュメントでは、実装したセキュリティ機能をアプリに統合する方法を説明します。

---

## 📦 必要なパッケージ

すでに package.json に含まれているため、追加インストールは不要です:
- `@fingerprintjs/fingerprintjs` (デバイスID生成)
- `axios` (HTTP通信)

---

## 1️⃣ フロントエンドの統合

### ステップ1: main.jsx でセキュリティを初期化

`src/main.jsx` を編集:

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { BrowserRouter } from 'react-router-dom';

// 🔒 セキュリティ機能を初期化
import { initSecurity } from './utils/security';
initSecurity();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

### ステップ2: API呼び出しを secureApiRequest に置き換え

**変更前**:
```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
```

**変更後**:
```javascript
import { secureApiRequest } from './utils/security';

const response = await secureApiRequest('/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
```

### ステップ3: セッション管理を置き換え

**変更前**:
```javascript
localStorage.setItem('session_token', token);
localStorage.setItem('device_id', deviceId);
```

**変更後**:
```javascript
import { saveSession } from './utils/security';
saveSession(token, deviceId);
```

**セッション取得**:
```javascript
import { getSession } from './utils/security';

const session = getSession();
if (session) {
  console.log('Token:', session.token);
  console.log('Device ID:', session.deviceId);
} else {
  // セッション期限切れまたは未ログイン
  navigate('/login');
}
```

### ステップ4: ユーザー入力の検証

**例: 登録フォーム**:
```javascript
import { validateEmail, validatePassword } from './utils/security';

function handleRegister(e) {
  e.preventDefault();

  // メール検証
  if (!validateEmail(email)) {
    alert('無効なメールアドレスです');
    return;
  }

  // パスワード検証
  const passwordCheck = validatePassword(password);
  if (!passwordCheck.valid) {
    alert(passwordCheck.message);
    return;
  }

  // 登録処理
  // ...
}
```

### ステップ5: 問題テキストのサニタイズ

**例: 問題表示コンポーネント**:
```javascript
import { sanitizeProblemText } from './utils/security';

function ProblemView({ problem }) {
  const safeText = sanitizeProblemText(problem.problem_text);

  return (
    <div>
      <p>{safeText}</p>
    </div>
  );
}
```

---

## 2️⃣ バックエンドの統合

### 既に統合済み！

バックエンドは `api_server.py` で既にセキュリティ機能が統合されています:

✅ レート制限が有効化
✅ セキュリティヘッダーが自動付与
✅ 入力検証・サニタイゼーションが実装済み
✅ 本番環境での開発者モード無効化

---

## 3️⃣ 環境設定

### .env ファイルの作成

```bash
cp .env.security.example .env
```

### 開発環境の設定

`.env` ファイルを編集:

```bash
FLASK_ENV=development
FLASK_DEBUG=true
DEV_MODE_ENABLED=true
PORT=5000
```

### 本番環境の設定

```bash
FLASK_ENV=production
FLASK_DEBUG=false
DEV_MODE_ENABLED=false
SECRET_KEY=<強力なランダム文字列>
FORCE_HTTPS=true
PORT=5000
```

---

## 4️⃣ 動作確認

### バックエンドの起動

```bash
# セキュリティ機能が初期化されることを確認
python3 backend/api_server.py
```

出力例:
```
🔒 セキュリティ機能を初期化中...
🔧 開発環境: 開発者モードが有効です
✅ セキュリティミドルウェアが初期化されました
✅ 認証データベース初期化成功
================================================================================
【風営法理解度チェック - バックエンド API】
================================================================================
✅ 問題集: backend/db/problems.json
✅ 総問題数: 230
✅ ポート: 5000
🔒 セキュリティ: 開発モード
================================================================================
```

### フロントエンドの起動

```bash
npm run dev
```

### セキュリティヘッダーの確認

ブラウザの開発者ツールで Network タブを開き、レスポンスヘッダーを確認:

✅ `X-Frame-Options: DENY`
✅ `X-Content-Type-Options: nosniff`
✅ `Content-Security-Policy: ...`
✅ `Referrer-Policy: strict-origin-when-cross-origin`

### レート制限のテスト

同じAPIエンドポイントに短時間で複数回リクエストを送信:

```javascript
// ブラウザのコンソールで実行
for (let i = 0; i < 20; i++) {
  fetch('/api/auth/verify-invite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: 'test' })
  }).then(res => console.log(`Request ${i}: ${res.status}`));
}
```

**期待される結果**:
- 最初の10回: `200` または `400`
- 11回目以降: `429 Too Many Requests`

---

## 5️⃣ トラブルシューティング

### 問題: レート制限が動作しない

**原因**: レート制限はメモリベースのため、サーバー再起動でリセットされます。

**解決策**: 本番環境では Redis を使用することを推奨:
```python
# backend/security_middleware.py
# Redis を使った実装に変更
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### 問題: CSPエラーが発生する

**原因**: Content Security Policy が厳しすぎる可能性があります。

**解決策**: `.env` で CSP モードを調整:
```bash
CSP_MODE=relaxed  # strict / moderate / relaxed
```

### 問題: セッションが期限切れになる

**原因**: セッション有効期限（デフォルト30日）が過ぎています。

**解決策**: `.env` で有効期限を調整:
```bash
SESSION_MAX_AGE_DAYS=90  # 90日に延長
```

---

## 6️⃣ 追加の推奨事項

### セキュリティスキャンの実行

定期的にセキュリティスキャンを実行:

```bash
# npm パッケージのスキャン
npm audit

# 脆弱性を自動修正
npm audit fix

# Python パッケージのスキャン
pip check
```

### ログ監視の設定

本番環境ではログ監視サービスを使用することを推奨:

- **Sentry**: エラー追跡
- **LogRocket**: セッション記録
- **Datadog**: インフラ監視

### HTTPS証明書の自動更新

Let's Encrypt の証明書は90日で期限切れになるため、自動更新を設定:

```bash
# crontab -e
0 0 1 * * certbot renew --quiet
```

---

## ✅ 統合完了チェックリスト

- [ ] `src/main.jsx` でセキュリティを初期化
- [ ] API呼び出しを `secureApiRequest` に置き換え
- [ ] セッション管理を `saveSession/getSession` に置き換え
- [ ] ユーザー入力の検証を追加
- [ ] 問題テキストのサニタイズを追加
- [ ] `.env` ファイルを作成・設定
- [ ] バックエンドの起動確認
- [ ] フロントエンドの起動確認
- [ ] セキュリティヘッダーの確認
- [ ] レート制限のテスト
- [ ] セキュリティスキャンの実行

---

## 🎉 完了！

これでセキュリティ機能の統合が完了しました。

**次のステップ**:
1. `SECURITY.md` を読んで詳細な設定を確認
2. 本番環境へのデプロイ前にセキュリティチェックリストを実行
3. 定期的なメンテナンスを実施

---

**質問や問題がある場合は**: [SECURITY.md](./SECURITY.md) の「お問い合わせ」セクションを参照してください。
