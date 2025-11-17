# 🔴 Redis接続エラー修正ガイド

## 現在の問題
**招待URLアクセス時に「サーバーとの通信に失敗しました」エラーが発生**

### エラー詳細
```json
{
  "error": "サーバーエラーが発生しました",
  "details": "Connection is closed."
}
```

## 原因
Redis Cloud (redis-pink-notebook) への接続が切れている

## 修正方法

### 1. Vercel環境変数の確認（最優先）

1. **Vercelダッシュボードにログイン**
   ```
   https://vercel.com/dashboard
   ```

2. **プロジェクトを選択**
   - `pachinko-lawtest` を選択

3. **Settings → Environment Variables**

4. **以下の環境変数が設定されているか確認**：
   - `REDIS_HOST`: redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com
   - `REDIS_PORT`: 15687
   - `REDIS_PASSWORD`: (Redis Cloudのパスワード)
   - `REDIS_URL`: (代替: 完全な接続URL)

### 2. Redis Cloud側の確認

1. **Redis Cloud にログイン**
   ```
   https://app.redislabs.com/
   ```

2. **データベース状態確認**
   - データベース名: `redis-pink-notebook`
   - ステータス: Active であることを確認
   - エンドポイント: `redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com:15687`

3. **接続情報の確認**
   - パスワードが変更されていないか
   - 接続制限（IP制限等）が設定されていないか

### 3. 手動接続テスト

```bash
# Redis CLIで直接接続テスト
redis-cli -h redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com -p 15687 -a [PASSWORD] --tls ping
```

期待される応答: `PONG`

### 4. Vercel環境変数の更新（必要な場合）

Vercel CLIを使用：
```bash
vercel env add REDIS_PASSWORD production
# パスワードを入力

vercel env add REDIS_HOST production
# redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com を入力

vercel env add REDIS_PORT production
# 15687 を入力
```

または、Vercel KV を使用する場合：
```bash
vercel env add KV_REST_API_URL production
vercel env add KV_REST_API_TOKEN production
```

### 5. 再デプロイ

環境変数を更新した後：
```bash
vercel --prod
```

## テスト手順

1. **API Health チェック**
   ```bash
   curl https://pachinko-lawtest.vercel.app/api/health
   ```

2. **トークン検証テスト**
   ```bash
   curl -X POST https://pachinko-lawtest.vercel.app/api/validate-token \
     -H "Content-Type: application/json" \
     -d '{"token": "039742a2-f799-4574-8530-a8e1d81960f1", "email": "test@example.com"}'
   ```

3. **実際の招待URLでテスト**
   ```
   https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
   ```

## 代替案: Vercel KV への移行

Redis Cloudで問題が続く場合、Vercel KVへの完全移行を検討：

1. **Vercel KV データベース作成**
   - Vercel Dashboard → Storage → Create Database
   - KV を選択

2. **コード更新**
   - `@vercel/kv` パッケージを使用
   - Redis接続コードをVercel KV APIに置き換え

3. **データ移行**
   - 既存の招待トークンをVercel KVにコピー

## チェックリスト

- [ ] Vercel環境変数確認
- [ ] Redis Cloud状態確認
- [ ] 手動接続テスト実施
- [ ] 環境変数更新（必要な場合）
- [ ] 再デプロイ
- [ ] APIテスト
- [ ] 招待URLテスト

---

**作成日時**: 2025-11-17
**問題**: Redis接続エラーによる招待URL登録失敗