# サーバーエラー修正案

## 🚨 問題の根本原因

### 現在の構成と問題点

| コンポーネント | URL | 問題 |
|--------------|-----|------|
| **フロントエンド** | `https://pj0201.github.io/pachinko-lawtest/` | GitHub Pages |
| **バックエンドAPI** | `https://pachinko-lawtest.vercel.app/api/` | Vercel |
| **API呼び出し** | `/api/validate-token` (相対パス) | **❌ エラー発生** |

### エラーの詳細

```javascript
// src/pages/Register.jsx での API 呼び出し
fetch('/api/validate-token', {  // 相対パス
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token, email })
});
```

**実際のリクエスト先（誤り）：**
- `https://pj0201.github.io/pachinko-lawtest/api/validate-token` → **404 Not Found**

**正しいリクエスト先：**
- `https://pachinko-lawtest.vercel.app/api/validate-token` ✅

## 🎯 修正方法（3つのオプション）

### 修正案1: API URLを環境変数で管理（推奨）

#### 1. API設定ファイルを作成

```javascript
// src/config/api.js
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (window.location.hostname === 'pj0201.github.io'
    ? 'https://pachinko-lawtest.vercel.app/api'
    : '/api');

export const apiEndpoints = {
  validateToken: `${API_BASE_URL}/validate-token`,
  register: `${API_BASE_URL}/register`,
  health: `${API_BASE_URL}/health`,
  problems: `${API_BASE_URL}/problems`
};
```

#### 2. Register.jsxを修正

```javascript
// src/pages/Register.jsx
import { apiEndpoints } from '../config/api';

// 変更前:
// const validateResponse = await fetch('/api/validate-token', {

// 変更後:
const validateResponse = await fetch(apiEndpoints.validateToken, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token, email })
});

// 同様に register エンドポイントも修正
const registerResponse = await fetch(apiEndpoints.register, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, username, token, deviceId })
});
```

#### 3. 環境変数ファイルを作成

```bash
# .env.production
VITE_API_URL=https://pachinko-lawtest.vercel.app/api
```

### 修正案2: APIベースURLをハードコード（即座の修正）

#### Register.jsxに直接記述

```javascript
// src/pages/Register.jsx
const API_BASE_URL = 'https://pachinko-lawtest.vercel.app/api';

// API呼び出し部分を修正
const validateResponse = await fetch(`${API_BASE_URL}/validate-token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token, email })
});

const registerResponse = await fetch(`${API_BASE_URL}/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, username, token, deviceId })
});
```

### 修正案3: フロントエンドもVercelに移行（最適解）

#### メリット
- CORSの問題が完全に解消
- API呼び出しが相対パスのままで動作
- デプロイと管理が一元化

#### 実装方法
```bash
# GitHub Pages を廃止
vercel --prod

# デプロイ後のURL
https://pachinko-lawtest.vercel.app/
```

## 📝 その他の必要な修正

### 1. CORS設定の確認（vercel.json）

現在の設定：
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"  // すべてのドメインを許可
        }
      ]
    }
  ]
}
```

GitHub Pagesからのアクセスに限定する場合：
```json
{
  "key": "Access-Control-Allow-Origin",
  "value": "https://pj0201.github.io"
}
```

### 2. ExamScreen.jsxなど他のコンポーネントの確認

```bash
# API呼び出しがある可能性のある他のファイル
src/components/ExamScreen.jsx
src/components/History.jsx
src/components/Home.jsx
```

これらのファイルも同様に修正が必要

## ✅ 実装手順

### 最速修正（5分）
1. Register.jsxにAPI_BASE_URLをハードコード
2. コミット＆プッシュ
3. GitHub Pagesの自動デプロイを待つ
4. テスト

### 推奨修正（15分）
1. src/config/api.js を作成
2. Register.jsx を修正
3. 他のコンポーネントも確認・修正
4. .env.production を作成
5. コミット＆プッシュ
6. デプロイ＆テスト

## 🧪 テスト方法

```bash
# 1. ローカルでビルド
npm run build

# 2. ビルド後のファイルを確認
grep -r "pachinko-lawtest.vercel.app" dist/

# 3. 本番環境でテスト
# ブラウザで開く:
https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123

# 4. 開発者ツールでネットワークタブを確認
# APIリクエストが https://pachinko-lawtest.vercel.app/api/ に送信されているか確認
```

## 📊 修正後の期待される動作

1. **招待URL アクセス**
   - `https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123`

2. **API呼び出し**
   - ✅ `https://pachinko-lawtest.vercel.app/api/validate-token`
   - ✅ `https://pachinko-lawtest.vercel.app/api/register`

3. **Redis Cloud接続**
   - ✅ `redis-pink-notebook` データベース使用
   - ✅ 環境変数設定済み

4. **正常な登録フロー**
   - トークン検証 → ユーザー登録 → ホーム画面遷移

## 🚀 結論

**問題**: フロントエンド（GitHub Pages）からバックエンドAPI（Vercel）への通信が相対パスのため失敗

**解決策**: APIのベースURLを絶対パスに変更

**推奨アプローチ**: 修正案1（環境変数で管理）を実装

---

**作成日時**: 2025-11-17 21:10
**作成者**: Claude Opus (Worker3)
**ステータス**: 実装待ち