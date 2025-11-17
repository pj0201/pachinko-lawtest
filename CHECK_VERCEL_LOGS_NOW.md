# 🔴 緊急: Vercel Functions ログ確認手順

## Redis接続エラーが継続中

### エラー詳細
```json
{
  "error": "サーバーエラーが発生しました",
  "details": "Connection is closed."
}
```

## 今すぐ確認すること

### 1. Vercel Functions ログ確認

1. **Vercelダッシュボード**: https://vercel.com/dashboard
2. **pachinko-lawtest** → **Functions** タブ
3. **validate-token** をクリック
4. **Logs** タブを確認

### 2. エラーパターンを特定

#### パターンA: 環境変数が未設定
```
REDIS_PASSWORD is undefined
REDIS_HOST is undefined
```
**対処**: Settings → Environment Variables で設定

#### パターンB: 認証エラー
```
ReplyError: NOAUTH Authentication required
ReplyError: WRONGPASS invalid username-password pair
```
**対処**: Redis Cloudでパスワード再確認

#### パターンC: 接続拒否
```
Error: connect ECONNREFUSED
Error: connect ETIMEDOUT
```
**対処**: Redis Cloudのデータベース状態確認

### 3. 環境変数の確認方法

#### Vercel Dashboard で確認
1. Settings → Environment Variables
2. 以下が設定されているか確認：
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_PASSWORD`

#### もし Vercel KV を使っている場合
以下の環境変数が必要：
- `KV_REST_API_URL`
- `KV_REST_API_TOKEN`
- `KV_REST_API_READ_ONLY_TOKEN`
- `KV_URL`

### 4. 一時的な解決策: テスト用APIエンドポイント作成

もしRedis接続が解決しない場合、一時的にRedisを使わないテストエンドポイントを作成：

```javascript
// api/test-validate.js
export default async function handler(req, res) {
  const { token, email } = req.body;

  // TESTトークンは常に有効とする
  if (token.startsWith('TEST_') || token.match(/^[0-9a-f]{8}-/)) {
    return res.status(200).json({
      valid: true,
      message: "テスト用: 有効な招待URLです"
    });
  }

  return res.status(400).json({
    valid: false,
    error: "無効なトークン"
  });
}
```

### 5. Redis Cloud 状態確認

1. **Redis Cloud ログイン**: https://app.redislabs.com/
2. **redis-pink-notebook** データベース選択
3. 確認事項：
   - Status: **Active** か？
   - Connections: 接続数制限に達していないか？
   - Endpoint: 正しいか？
   - Password: 最近変更されていないか？

## 🚨 重要な質問

### Vercel KV を使っていますか？それとも Redis Cloud？

**もし「Vercel KV」を使っている場合**：
- コードの修正が必要（現在のコードは Redis Cloud を参照）
- `@vercel/kv` パッケージへの移行が必要

**もし「Redis Cloud」を使っている場合**：
- 環境変数の設定確認
- Redis Cloudの接続情報確認

## チェックリスト

- [ ] Vercel Functions ログ確認
- [ ] エラーメッセージ特定
- [ ] 環境変数の存在確認
- [ ] Redis Cloud/Vercel KV どちらを使うか確認
- [ ] 必要に応じてコード修正

---

**緊急度**: 🔴 最優先
**影響**: 全ての招待URLが使用不可