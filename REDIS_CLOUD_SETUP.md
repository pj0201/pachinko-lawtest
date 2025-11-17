# Redis Cloud セットアップガイド

## 接続情報

**データベース名:** redis-pink-notebook
**Public endpoint:** redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com:15687
**バージョン:** 8.2

---

## 1. Redis Cloudのパスワードを取得

### 手順:

1. **Redis Cloudダッシュボードにアクセス**
   - https://app.redislabs.com/
   - ログイン

2. **redis-pink-notebook データベースを選択**
   - Database #13739096

3. **Configuration タブ → Security セクション**
   - "Default user" の設定を確認
   - "View password" または "Copy password" をクリック
   - パスワードをコピー

---

## 2. Vercel に環境変数を設定

### 手順:

1. **Vercel Dashboard にアクセス**
   - https://vercel.com/dashboard
   - `pachinko-lawtest` プロジェクトを選択

2. **Settings → Environment Variables に移動**

3. **以下の環境変数を追加**

   | 変数名 | 値 | 環境 |
   |--------|---|------|
   | `REDIS_HOST` | `redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com` | Production, Preview, Development |
   | `REDIS_PORT` | `15687` | Production, Preview, Development |
   | `REDIS_PASSWORD` | [Redis Cloudでコピーしたパスワード] | Production, Preview, Development |

4. **"Save" をクリック**

---

## 3. 環境変数の確認

設定後、以下のコマンドで確認できます（ローカル開発用の .env ファイル作成）:

```bash
cat > .env << 'EOF'
# Redis Cloud 接続情報
REDIS_HOST=redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com
REDIS_PORT=15687
REDIS_PASSWORD=<your-password-here>
EOF
```

⚠️ **注意:** `.env` ファイルは `.gitignore` に含まれているため、Git にコミットされません。

---

## 4. デプロイして接続確認

### デプロイ:

```bash
git add .
git commit -m "fix: Redis Cloud接続に修正（@vercel/kv → ioredis）"
git push origin claude/fix-vercel-kv-registration-01ALuL9dTijA2BygFtqW7kyj
```

### ヘルスチェック:

デプロイ完了後、以下のURLにアクセス:

```
https://your-app.vercel.app/api/health
```

**期待される応答:**

```json
{
  "status": "ok",
  "timestamp": "2025-11-17T...",
  "service": "pachinko-exam-backend",
  "problems_loaded": 540,
  "redis": {
    "status": "connected",
    "error": null,
    "configured": true,
    "host": "redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com"
  }
}
```

**エラーの場合:**

```json
{
  "redis": {
    "status": "disconnected",
    "error": "Connection refused" // または認証エラー
  }
}
```

原因:
- パスワードが間違っている
- 環境変数が設定されていない
- Redis Cloud のデータベースが停止している

---

## 5. ローカルでのテスト（オプション）

### .env ファイルを作成:

```bash
cat > .env << 'EOF'
REDIS_HOST=redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com
REDIS_PORT=15687
REDIS_PASSWORD=<your-password-here>
EOF
```

### ローカルサーバーを起動:

```bash
npm run dev
```

### ヘルスチェック:

```bash
curl http://localhost:5173/api/health
```

---

## 6. 招待URL重複テスト

### デバイスA（またはブラウザのプライベートモード）:

1. 登録ページにアクセス:
   ```
   https://your-app.vercel.app/register/TEST_001_ABC123
   ```

2. フォームを入力して登録:
   - Email: test1@example.com
   - Username: テストユーザー1

3. **登録成功を確認**

### デバイスB（または別のブラウザ）:

1. **同じトークン**で登録ページにアクセス:
   ```
   https://your-app.vercel.app/register/TEST_001_ABC123
   ```

2. フォームを入力:
   - Email: test2@example.com
   - Username: テストユーザー2

3. **期待:** エラーメッセージ
   ```
   この招待URLは既に使用されています
   ```

### メール重複テスト:

1. デバイスBで別のトークンを使用:
   ```
   https://your-app.vercel.app/register/TEST_002_DEF456
   ```

2. **同じメールアドレス**で登録を試みる:
   - Email: test1@example.com
   - Username: テストユーザー3

3. **期待:** エラーメッセージ
   ```
   このメールアドレスは既に登録されています
   ```

---

## トラブルシューティング

### Redis接続エラー

**症状:**
```
❌ Redis接続エラー: Connection refused
```

**解決方法:**
1. Vercel の環境変数を確認
2. Redis Cloud でデータベースが稼働中か確認
3. パスワードが正しいか確認

### 認証エラー

**症状:**
```
❌ Redis接続エラー: NOAUTH Authentication required
```

**解決方法:**
- `REDIS_PASSWORD` 環境変数が設定されていません
- Vercel Dashboard で環境変数を追加してください

### TLS/SSLエラー

**症状:**
```
❌ Redis接続エラー: SSL handshake failed
```

**解決方法:**
- Redis Cloud は TLS 接続が必要です
- `api/index.js` で以下の設定を確認:
  ```javascript
  tls: {
    rejectUnauthorized: false
  }
  ```

---

## 重要な変更点

### ❌ 以前（誤り）:
- `@vercel/kv` を使用
- Vercel KV データベースだと思っていた

### ✅ 現在（正しい）:
- `ioredis` を使用
- Redis Cloud の通常の Redis データベース
- TLS 接続が必要
- 環境変数: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`

---

## まとめ

1. ✅ `ioredis` に変更
2. ⚠️ Redis Cloud のパスワードを取得
3. ⚠️ Vercel に環境変数を設定
4. ⚠️ デプロイして接続確認
5. ⚠️ 招待URL重複テストを実施

次のステップ: **Redis Cloudのパスワードを取得して、Vercel環境変数に設定してください。**
