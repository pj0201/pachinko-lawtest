# Pachinko Lawtest - プロジェクト状況レポート

**最終更新:** 2025-11-17
**ブランチ:** `claude/fix-vercel-kv-registration-01ALuL9dTijA2BygFtqW7kyj`
**ステータス:** ❌ 未解決 - 登録時にサーバー通信エラー

---

## 技術スタック

### フロントエンド
- **フレームワーク:** React 18.2.0
- **ルーティング:** React Router DOM 7.9.4
- **ビルドツール:** Vite 4.5.0
- **デバイス識別:** FingerprintJS 4.6.2
- **モバイル対応:** Capacitor 6.2.1 (iOS/Android)

### バックエンド（サーバーレス）
- **ホスティング:** Vercel
- **サーバーレス関数:** Node.js (ES Modules)
- **Webフレームワーク:** Express 5.1.0
- **Redis接続:** ioredis 5.8.2
- **データベース:** Redis Cloud (redis-pink-notebook)

### デプロイ
- **プラットフォーム:** Vercel
- **リポジトリ:** GitHub - pj0201/pachinko-lawtest
- **デプロイ方式:** Git push → 自動デプロイ（mainブランチ）

---

## プロジェクト概要

### 目的
パチンコ遊技場管理者試験の模擬試験アプリ（スマートフォン専用）

### 主な機能
1. **招待URL制限システム**
   - 1招待URL = 1アカウント（デバイス間で共有）
   - トークン使用済みチェック（Redis Cloud）
   - メールアドレス重複防止

2. **デバイス登録**
   - FingerprintJSでデバイス識別
   - スマートフォン専用制限（PC/タブレット除外）

3. **模擬試験**
   - 風営法・施行規則の問題データ（626問）
   - 成績履歴管理

---

## これまでの修正内容（時系列）

### Phase 1: 初期実装（Vercel KV使用を試みた）

**コミット:** `a0814e1` - `79aa5e7`

**実施内容:**
- `ioredis` から `@vercel/kv` に移行を試みた
- `api/index.js` でExpressアプリを使用
- トークン検証・登録APIを実装

**結果:** ❌ 失敗
- **理由:** `redis-pink-notebook` は Vercel KV ではなく、Redis Cloud の通常のRedisデータベースだった

---

### Phase 2: Redis Cloud への正しい接続（ioredis に戻す）

**コミット:** `f9a1920` - `47fac1a`

**実施内容:**
- `@vercel/kv` を削除、`ioredis` を再インストール
- Redis Cloud 接続設定を追加（TLS対応）
  ```javascript
  const redis = new Redis({
    host: 'redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com',
    port: 15687,
    password: process.env.REDIS_PASSWORD,
    tls: { rejectUnauthorized: false }
  });
  ```
- 環境変数を `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` に変更

**結果:** ❌ 部分的に動作
- `/api/health` のみ動作（個別ファイルだったため）
- Express アプリ（`api/index.js`）がVercelで動作しない

---

### Phase 3: ルーティング問題の修正

**コミット:** `54792d5` - `b0d26c5`

**実施内容:**
- `vercel.json` のrewriteルールを修正
  ```json
  "source": "/((?!api).*)"  // APIを除外
  ```
- APIルートから `/api` プレフィックスを削除
  - `app.get('/api/health')` → `app.get('/health')`

**結果:** ❌ 依然として動作せず
- Express アプリがサーバーレス関数として正しく動作しない

---

### Phase 4: 個別サーバーレス関数への分割

**コミット:** `a875670` - `cb0f74b`

**実施内容:**
- Express アプリを廃止
- 各エンドポイントを独立したサーバーレス関数に分割
  - `api/validate-token.js` - トークン検証
  - `api/register.js` - ユーザー登録
  - `api/verify-session.js` - セッション検証
  - `api/health.js` - ヘルスチェック
  - `api/test.js` - テスト用

- Redis接続をサーバーレス環境用に最適化
  ```javascript
  function createRedisClient() {
    return new Redis({
      connectTimeout: 10000,
      maxRetriesPerRequest: 3,
      retryStrategy: (times) => {
        if (times > 3) return null;
        return Math.min(times * 50, 2000);
      }
    });
  }

  // ハンドラー内で接続作成
  const redis = createRedisClient();
  await redis.ping();
  // 処理後にクローズ
  await redis.quit();
  ```

**結果:** ❌ 依然として動作せず
- 関数ファイルは作成したが、`vercel.json` で登録されていなかった

---

### Phase 5: vercel.json の修正（最新）

**コミット:** `a7c6908` (現在)

**実施内容:**
- `vercel.json` の functions セクションを修正
  ```json
  "functions": {
    "api/**/*.js": {  // すべてのAPIファイルを登録
      "memory": 1024,
      "maxDuration": 10
    }
  }
  ```
  **Before:** `"api/index.js"` のみ
  **After:** `"api/**/*.js"` で全関数を登録

**結果:** ⚠️ 未確認
- GitHub PR #11 がmainにマージ済み
- Vercelデプロイ状況が不明
- スマホで「サーバーとの通信に失敗しました」エラーが継続

---

## 現在の問題

### 症状

**スマートフォンから招待URLで登録を試みると失敗**

1. 招待URLにアクセス: https://pachinko-lawtest.vercel.app/invite/[token]
2. 登録フォームが表示される（正常）
3. ユーザー名・メールアドレスを入力
4. 「登録」ボタンをタップ
5. 「読み込み中...」表示
6. ❌ **エラー:** 「サーバーとの通信に失敗しました」

### 確認済みの動作状況

#### ✅ 動作しているエンドポイント

**1. `/api/health`**
```bash
GET https://pachinko-lawtest.vercel.app/api/health
```
**レスポンス:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-17T09:37:16.041Z",
  "service": "pachinko-exam-backend",
  "message": "API is working!"
}
```
⚠️ **問題:** Redis接続情報が含まれていない（期待: `"redis": {"status": "connected"}`）

**2. `/api/test`**
```bash
GET https://pachinko-lawtest.vercel.app/api/test
```
**レスポンス:**
```json
{
  "success": true,
  "message": "Test endpoint is working!",
  "method": "GET",
  "timestamp": "2025-11-17T09:37:35.311Z"
}
```

#### ❌ 動作不明のエンドポイント

**1. `/api/validate-token`**
- フロントエンドから呼ばれる（Register.jsx:116）
- トークンとメールアドレスの検証
- Redis Cloudで使用済みチェック

**2. `/api/register`**
- フロントエンドから呼ばれる（Register.jsx:136）
- ユーザー情報をRedis Cloudに保存

---

## ファイル構造

### API関数（/api ディレクトリ）

```
api/
├── health.js           ✅ 動作中（ただしRedis情報なし）
├── test.js             ✅ 動作中
├── validate-token.js   ❓ 動作不明（404の可能性）
├── register.js         ❓ 動作不明（404の可能性）
├── verify-session.js   ❓ 動作不明
├── index.js            ⚠️ 旧Expressアプリ（使用されていない可能性）
└── auth/
    └── register.py     （未使用）
```

### フロントエンド（/src ディレクトリ）

```
src/
├── pages/
│   └── Register.jsx    登録ページ（招待URL処理）
├── components/
│   ├── Home.jsx        ホーム画面
│   ├── ExamScreen.jsx  試験画面
│   └── ProtectedRoute.jsx  セッション検証
└── utils/
    └── deviceCheck.js  スマホ専用チェック
```

### 設定ファイル

```
vercel.json            Vercel設定（functions定義）
package.json           依存関係
```

---

## 環境変数（Vercel設定済み）

以下の環境変数がVercelに設定されています（全環境: Production, Preview, Development）:

| 変数名 | 値 | 用途 |
|--------|---|------|
| `REDIS_HOST` | `redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com` | Redis Cloud接続先 |
| `REDIS_PORT` | `15687` | Redis Cloudポート |
| `REDIS_PASSWORD` | [設定済み] | Redis Cloud認証 |

---

## 次のエージェントが確認すべき項目

### 🔴 最優先: Vercel Deployments 確認

1. **Vercel Dashboard にアクセス**
   ```
   https://vercel.com/dashboard → pachinko-lawtest
   ```

2. **Deployments タブ → 最新デプロイをクリック**
   - **コミットハッシュ:** `c28ece6` (Merge PR #11) または `a7c6908` か確認
   - **ステータス:** "Ready" (緑色) になっているか
   - **デプロイ時刻:** PR #11マージ後（最新）か

3. **Functions タブを確認**
   - **期待:** 5個の関数が表示される
     - `api/health.js`
     - `api/test.js`
     - `api/validate-token.js` ← **重要**
     - `api/register.js` ← **重要**
     - `api/verify-session.js`

   - **もし1個だけ表示（api/index.js）:**
     - 古いバージョンがデプロイされている
     - "Redeploy" を実行（Build Cacheを無効化）

4. **Function Logs を確認**
   - スマホで登録を試みた時刻のログを検索
   - エラーメッセージ:
     - `❌ Redis接続エラー`
     - `404 Not Found`
     - `500 Internal Server Error`

### 🟡 API動作テスト

デスクトップブラウザまたはcurlで以下をテスト:

```bash
# 1. トークン検証API（重要）
curl -X POST https://pachinko-lawtest.vercel.app/api/validate-token \
  -H "Content-Type: application/json" \
  -d '{
    "token": "039742a2-f799-4574-8530-a8e1d81960f1",
    "email": "test@example.com"
  }'

# 期待: {"valid": true, "message": "トークンとメールアドレスは有効です"}
# エラー: 404 Not Found = 関数が登録されていない
#        500 Internal Server Error = Redis接続失敗

# 2. ユーザー登録API（重要）
curl -X POST https://pachinko-lawtest.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apitest@example.com",
    "username": "APIテスト",
    "token": "039742a2-f799-4574-8530-a8e1d81960f1",
    "deviceId": "test-device-12345"
  }'

# 期待: {"success": true, "sessionToken": "session_...", ...}
# エラー: 404 Not Found = 関数が登録されていない
#        400 Bad Request = トークン検証失敗
#        500 Internal Server Error = Redis接続失敗
```

### 🟢 Redis接続確認

1. **Redis Cloud Dashboard**
   - https://app.redislabs.com/
   - データベース: `redis-pink-notebook`
   - ステータスが "Active" か確認

2. **Vercel環境変数の再確認**
   - Settings → Environment Variables
   - `REDIS_PASSWORD` が正しく設定されているか
   - すべての環境（Production, Preview, Development）に設定されているか

---

## デバッグ情報

### スマホでのエラー詳細

**エラーの発生箇所:** `src/pages/Register.jsx:176-178`
```javascript
} catch (err) {
  console.error('❌ 登録エラー:', err);
  setError('サーバーとの通信に失敗しました');
}
```

**このエラーがトリガーされる条件:**
1. `fetch('/api/validate-token')` でネットワークエラー
2. `fetch('/api/register')` でネットワークエラー
3. レスポンスがJSONではない（404 HTML等）
4. タイムアウト

### 登録フローの詳細

```
1. スマホで招待URLにアクセス
   ↓
2. Register.jsx マウント
   ↓
3. デバイスIDを取得（FingerprintJS）
   ↓
4. トークンフォーマットチェック（フロントエンド）
   ↓
5. ユーザーが名前・メール入力して「登録」タップ
   ↓
6. POST /api/validate-token  ← ここで失敗している可能性
   ↓
7. POST /api/register
   ↓
8. localStorage に保存
   ↓
9. ホーム画面にリダイレクト
```

---

## 招待URL（テスト用）

### UUID v4形式（10個）

1. https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
2. https://pachinko-lawtest.vercel.app/invite/cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb
3. https://pachinko-lawtest.vercel.app/invite/d0b28ab3-44b6-45aa-897b-e72e0e0da116
4. https://pachinko-lawtest.vercel.app/invite/babcd6fb-b8a8-46a8-b3a6-fc00966d07a3
5. https://pachinko-lawtest.vercel.app/invite/b1b281a3-6b76-4659-9827-bf3a07b6c3ba
6. https://pachinko-lawtest.vercel.app/invite/12f622c2-cbf4-4631-abb7-7336c841b198
7. https://pachinko-lawtest.vercel.app/invite/3c756c94-0d98-4d8b-b466-17e99f1b3240
8. https://pachinko-lawtest.vercel.app/invite/2b1d54e2-97a0-4900-a513-fab986540358
9. https://pachinko-lawtest.vercel.app/invite/d47c9566-cabd-4d96-91d0-41afc10a59b6
10. https://pachinko-lawtest.vercel.app/invite/c502c94a-3e4e-471e-9835-2f05018751e4

---

## 疑われる根本原因

### 仮説1: サーバーレス関数が登録されていない（最有力）

**証拠:**
- `/api/health` は動作するが、Redis情報がない（古いバージョン）
- `/api/validate-token`, `/api/register` が404の可能性

**確認方法:**
- Vercel Dashboard → Functions タブで関数数を確認
- 1個だけ（api/index.js）→ 古いバージョン
- 5個表示 → 正しいバージョン

**解決方法:**
- Vercel Dashboard で "Redeploy" を実行（Build Cacheを無効化）

---

### 仮説2: Redis接続エラー

**証拠:**
- `/api/health` のレスポンスにRedis情報がない

**確認方法:**
- Function Logs で `❌ Redis接続エラー` を検索
- Redis Cloud のステータス確認

**解決方法:**
- 環境変数 `REDIS_PASSWORD` を再設定
- Redis Cloud のIPホワイトリスト確認（Vercel IPを許可）

---

### 仮説3: ビルドエラー

**確認方法:**
- Vercel Dashboard → Deployments → 最新デプロイ → "Building" タブ
- エラーメッセージを確認

---

## 関連ドキュメント

- `SMARTPHONE_TEST_GUIDE.md` - スマホでのテスト手順書
- `REDIS_CLOUD_SETUP.md` - Redis Cloud接続手順
- `INVITE_URL_TEST.md` - 招待URL制限のテスト方法

---

## 連絡先・リポジトリ

- **GitHub:** https://github.com/pj0201/pachinko-lawtest
- **ブランチ:** `claude/fix-vercel-kv-registration-01ALuL9dTijA2BygFtqW7kyj`
- **Vercel:** https://vercel.com/dashboard (pachinko-lawtest)

---

**最終更新:** 2025-11-17 09:37 UTC
**ステータス:** 🔴 未解決 - サーバーレス関数のデプロイ状況要確認
