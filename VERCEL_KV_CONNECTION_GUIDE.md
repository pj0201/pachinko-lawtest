# Vercel KV 接続確認ガイド

## 現在の状況

**エラーメッセージ:**
```
This project is already connected to the target store in one of the chosen environments
```

これは `redis-pink-notebook` が既に一部の環境（Production/Preview/Development）に接続されていることを示しています。

---

## 接続状態を確認する手順

### 1. Vercel Dashboard で環境変数を確認

1. **Vercel Dashboard にアクセス**
   - https://vercel.com/dashboard
   - `pachinko-lawtest` プロジェクトを選択

2. **Settings → Environment Variables に移動**
   - 左サイドバーの "Settings" をクリック
   - "Environment Variables" タブを選択

3. **KV 関連の環境変数を確認**

   以下の変数が設定されているか確認してください：

   | 変数名 | 必須 | どの環境に設定されているか |
   |--------|------|---------------------------|
   | `KV_REST_API_URL` | ✅ | Production / Preview / Development |
   | `KV_REST_API_TOKEN` | ✅ | Production / Preview / Development |
   | `KV_REST_API_READ_ONLY_TOKEN` | ✅ | Production / Preview / Development |
   | `KV_URL` | ⚠️ | Production / Preview / Development |

4. **確認ポイント**
   - ✅ すべての環境（Production, Preview, Development）に設定されているか？
   - ❌ 一部の環境のみに設定されている場合は、それが問題の原因

---

## 解決方法

### パターン1: 一部の環境のみ接続されている場合

**症状:**
- Production のみ接続済み、Preview と Development が未接続
- または逆のパターン

**解決手順:**

1. **Storage → redis-pink-notebook に移動**
   - 左サイドバーの "Storage" をクリック
   - `redis-pink-notebook` をクリック

2. **Connect Project を確認**
   - "Connected Projects" セクションを確認
   - どの環境が接続されているか表示されている

3. **不足している環境を追加**
   - 環境変数が不足している環境にだけチェックを入れる
   - 例: Production は既に接続済み → Preview と Development のみチェック
   - "Connect" をクリック

---

### パターン2: すべての環境が接続済みの場合

**症状:**
- すべての環境変数が既に設定されている
- エラーメッセージが出るが実際には接続済み

**確認方法:**

1. **ヘルスチェックAPIで確認**

   デプロイ後、以下のURLにアクセス：
   ```
   https://your-app.vercel.app/api/health
   ```

   **期待される応答:**
   ```json
   {
     "status": "ok",
     "kv": {
       "status": "connected",
       "error": null,
       "configured": true
     }
   }
   ```

2. **接続が確認できた場合**
   - エラーメッセージは無視してOK
   - 既に正しく接続されています

---

### パターン3: 接続を再設定する場合

**症状:**
- 環境変数が古い、または不正確
- 接続を完全にやり直したい

**解決手順:**

1. **既存の環境変数を削除**
   - Settings → Environment Variables
   - KV 関連の変数をすべて削除
   - `KV_REST_API_URL`, `KV_REST_API_TOKEN`, `KV_REST_API_READ_ONLY_TOKEN`, `KV_URL`

2. **KV データベースから接続を解除**
   - Storage → redis-pink-notebook
   - "Connected Projects" から `pachinko-lawtest` を削除
   - "Disconnect" をクリック

3. **再接続**
   - "Connect to a Project" をクリック
   - `pachinko-lawtest` を選択
   - すべての環境（Production, Preview, Development）にチェック
   - Custom Prefix: **空白のまま**
   - "Connect" をクリック

---

## 次のステップ

### 接続確認が完了したら：

1. **デプロイ**
   ```bash
   git push origin claude/fix-vercel-kv-registration-01ALuL9dTijA2BygFtqW7kyj
   ```

2. **本番環境でヘルスチェック**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

3. **招待URL重複テスト**
   - デバイスAで登録: `https://your-app.vercel.app/register/TEST_001_ABC123`
   - デバイスBで同じトークンで登録を試みる
   - **期待:** エラー「この招待URLは既に使用されています」

---

## トラブルシューティング

### KV接続エラーが出る場合

**確認項目:**

1. **環境変数の確認**
   ```bash
   # Settings → Environment Variables で以下が存在するか確認
   KV_REST_API_URL=https://...
   KV_REST_API_TOKEN=...
   KV_REST_API_READ_ONLY_TOKEN=...
   ```

2. **デプロイログを確認**
   - Deployments → 最新のデプロイ → "View Function Logs"
   - `❌ Redis接続エラー` または `KV error` を検索

3. **コードが正しいか確認**
   - `api/index.js` で `import { kv } from '@vercel/kv';` を使用している
   - ~~`import Redis from 'ioredis';`~~ は削除済み

---

## 現在のコード状態

### ✅ 完了している変更

1. **`api/index.js`**
   - ❌ `ioredis` を削除
   - ✅ `@vercel/kv` を使用
   - ✅ JSON.parse/stringify を削除（自動処理）

2. **パッケージ**
   - ❌ `ioredis` をアンインストール
   - ✅ `@vercel/kv` は既にインストール済み

3. **APIエンドポイント**
   - `/api/validate-token` - トークン検証
   - `/api/register` - ユーザー登録
   - `/api/verify-session` - セッション検証
   - すべて `kv.get/set` を使用

### ⚠️ 未完了

- Vercel KV の環境変数設定（上記手順で実施）
- 本番環境でのテスト

---

## 重要な注意事項

### Custom Prefix について

**質問:** "ストレージのURL を入力するべきですか？"

**回答:** **NO - 空白のままでOK**

- Custom Prefix は環境変数のプレフィックスを変更するための設定
- デフォルトでは `KV_` プレフィックスが使用される
- 通常は空白のままで問題なし
- 入力するのは特殊なケースのみ（複数のKVデータベースを使用する場合など）

---

## 接続後の検証コマンド

### ヘルスチェック
```bash
curl https://your-app.vercel.app/api/health
```

### トークン検証テスト
```bash
curl -X POST https://your-app.vercel.app/api/validate-token \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TEST_001_ABC123",
    "email": "test@example.com"
  }'
```

### 登録テスト
```bash
curl -X POST https://your-app.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "テストユーザー",
    "token": "TEST_001_ABC123",
    "deviceId": "test-device-001"
  }'
```

---

## まとめ

1. **Settings → Environment Variables で KV 変数を確認**
2. **不足している環境があれば、その環境のみ接続を追加**
3. **デプロイしてヘルスチェックで接続確認**
4. **招待URL重複テストを実施**

この手順で `redis-pink-notebook` が正しくすべての環境に接続されます。
