# Vercel KV セットアップガイド

## 概要

Vercel KV（Redis）を使用して、サーバーレスでアカウントの独自性を担保します。

**実現する機能：**
- ✅ 1メールアドレス = 1アカウント（全デバイス共通）
- ✅ 1招待URL = 1アカウント（全デバイス共通）
- ✅ パソコンからのアクセスブロック（スマホ専用）
- ✅ 本番ビルドでconsole.log削除

---

## Vercel KV セットアップ手順

### 1. Vercel ダッシュボードにアクセス

https://vercel.com/dashboard にログイン

### 2. Storage タブを開く

プロジェクト → **Storage** タブ → **Create Database**

### 3. KV (Redis) を選択

- **KV (Redis)** をクリック
- Database Name: `pachinko-exam-kv`（任意）
- Region: `iad1` (推奨: ユーザーに近いリージョン)
- **Create** をクリック

### 4. プロジェクトに接続

- **Connect to Project** をクリック
- プロジェクトを選択: `pachinko-lawtest`
- Environment: **Production** と **Preview** の両方にチェック
- **Connect** をクリック

### 5. 環境変数を確認

自動的に以下の環境変数が設定されます：

```
KV_REST_API_URL=https://...
KV_REST_API_TOKEN=...
KV_REST_API_READ_ONLY_TOKEN=...
KV_URL=redis://...
```

**確認方法：**
Settings → Environment Variables で確認できます。

---

## デプロイ

### 自動デプロイ

main ブランチにマージすると自動デプロイされます。

```bash
git push origin main
```

Vercel が自動的に：
1. ビルド実行
2. KV 環境変数を注入
3. デプロイ
4. Production に昇格

---

## データ構造

### KV に保存されるデータ

#### 1. メールアドレスのキー
```
key: email:test@example.com
value: {
  username: "テスト001",
  email: "test@example.com",
  deviceId: "abc123...",
  inviteToken: "TEST_001_ABC123",
  sessionToken: "session_1234567890_abc123",
  registeredAt: "2025-11-14T12:00:00.000Z"
}
```

#### 2. トークンのキー
```
key: token:TEST_001_ABC123
value: {
  usedBy: "test@example.com",
  usedAt: "2025-11-14T12:00:00.000Z"
}
```

#### 3. セッションのキー
```
key: session:session_1234567890_abc123
value: {
  username: "テスト001",
  email: "test@example.com",
  deviceId: "abc123...",
  inviteToken: "TEST_001_ABC123",
  sessionToken: "session_1234567890_abc123",
  registeredAt: "2025-11-14T12:00:00.000Z"
}
```

---

## API エンドポイント

### 1. トークン検証 API

**URL:** `POST /api/validate-token`

**リクエスト：**
```json
{
  "token": "TEST_001_ABC123",
  "email": "test@example.com"
}
```

**レスポンス（成功）：**
```json
{
  "valid": true,
  "message": "トークンとメールアドレスは有効です"
}
```

**レスポンス（エラー）：**
```json
{
  "valid": false,
  "error": "この招待URLは既に使用されています"
}
```

### 2. ユーザー登録 API

**URL:** `POST /api/register`

**リクエスト：**
```json
{
  "email": "test@example.com",
  "username": "テスト001",
  "token": "TEST_001_ABC123",
  "deviceId": "abc123..."
}
```

**レスポンス（成功）：**
```json
{
  "success": true,
  "sessionToken": "session_1234567890_abc123",
  "user": {
    "username": "テスト001",
    "email": "test@example.com",
    "registeredAt": "2025-11-14T12:00:00.000Z"
  }
}
```

**レスポンス（エラー）：**
```json
{
  "success": false,
  "error": "このメールアドレスは既に登録されています"
}
```

---

## テスト

### ローカルテスト（開発環境）

ローカルでは KV が利用できないため、以下の方法でテストします：

#### 方法1: Vercel CLI を使用

```bash
# Vercel CLI インストール
npm install -g vercel

# ログイン
vercel login

# ローカルで実行（環境変数を自動取得）
vercel dev
```

#### 方法2: 本番環境で直接テスト

main ブランチにマージして Vercel にデプロイ後、スマホでテスト

---

## 本番環境でのテスト手順

### 1. スマホでアクセス

本番URL: https://pachinko-lawtest.vercel.app/register/TEST_001_ABC123

### 2. ユーザー登録

- ユーザー名: テスト001
- メールアドレス: test001@example.com
- **登録** ボタンをクリック

### 3. 重複チェック

同じメールアドレスで再登録を試みる：
- **エラー:** 「このメールアドレスは既に登録されています」

### 4. トークン使用済みチェック

別のデバイスで同じ招待URLにアクセス：
- **エラー:** 「この招待URLは既に使用されています」

### 5. 別のトークンでテスト

https://pachinko-lawtest.vercel.app/register/TEST_002_DEF456

- ユーザー名: テスト002
- メールアドレス: test002@example.com
- **成功:** 登録できる

---

## トラブルシューティング

### エラー: "KV_REST_API_URL is not defined"

**原因:** Vercel KV がプロジェクトに接続されていない

**解決策:**
1. Vercel ダッシュボード → Storage タブ
2. KV データベースを選択
3. **Connect to Project** をクリック
4. 再デプロイ

### エラー: "This database is already connected to this project"

**原因:** 既に接続済み

**解決策:**
1. Settings → Environment Variables で環境変数を確認
2. 再デプロイ（環境変数を再読み込み）

### ローカルで API が動かない

**原因:** ローカル環境では KV の環境変数がない

**解決策:**
```bash
vercel dev
```
または Vercel にデプロイして本番環境でテスト

---

## データの確認・管理

### Vercel ダッシュボードで確認

1. Storage → KV データベースを選択
2. **Data Browser** タブ
3. キーを検索：
   - `email:*` - 全ユーザー
   - `token:*` - 全トークン
   - `session:*` - 全セッション

### データ削除（テスト用）

```bash
# Vercel CLI を使用
vercel env pull .env.local
```

`.env.local` の環境変数を使って、Node.js スクリプトで削除：

```javascript
import { kv } from '@vercel/kv';

// 特定のメールアドレスを削除
await kv.del('email:test@example.com');

// 特定のトークンをリセット
await kv.del('token:TEST_001_ABC123');
```

---

## 料金

**Vercel KV 無料プラン:**
- 256 MB ストレージ
- 3,000 コマンド/日
- 十分なテスト用途に使用可能

**必要なストレージ見積もり:**
- 1ユーザー = 約 1 KB
- 256 MB = 約 26万ユーザー

---

## 次のステップ

1. ✅ Vercel KV をセットアップ
2. ✅ main ブランチにマージ
3. ✅ Vercel に自動デプロイ
4. ✅ スマホでテスト
5. ✅ データブラウザで確認

完了！
