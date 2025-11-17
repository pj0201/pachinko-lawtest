# 🔴 今すぐ実行: Vercel環境変数設定手順

## 📝 必要な情報を準備

### Redis Cloud の接続情報
- **Host**: `redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com`
- **Port**: `15687`
- **Password**: Redis Cloudダッシュボードで確認（下記手順参照）

---

## 🚀 手順1: Redis Cloud パスワード確認

1. **Redis Cloud にログイン**
   ```
   https://app.redislabs.com/
   ```

2. **データベース選択**
   - `redis-pink-notebook` をクリック

3. **Configuration タブ**
   - Default password をコピー（表示/非表示ボタンで確認）

---

## 🚀 手順2: Vercel 環境変数設定

### A. Vercelダッシュボードから設定（推奨）

1. **Vercelダッシュボードを開く**
   ```
   https://vercel.com/dashboard
   ```

2. **プロジェクトを選択**
   - `pachinko-lawtest` をクリック

3. **Settings → Environment Variables**

4. **以下の3つの環境変数を追加**

   #### REDIS_HOST
   - Key: `REDIS_HOST`
   - Value: `redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com`
   - Environment: ✅ Production, ✅ Preview, ✅ Development
   - 「Add」をクリック

   #### REDIS_PORT
   - Key: `REDIS_PORT`
   - Value: `15687`
   - Environment: ✅ Production, ✅ Preview, ✅ Development
   - 「Add」をクリック

   #### REDIS_PASSWORD
   - Key: `REDIS_PASSWORD`
   - Value: `[Redis Cloudからコピーしたパスワード]`
   - Environment: ✅ Production, ✅ Preview, ✅ Development
   - 「Add」をクリック

### B. Vercel CLIから設定（代替方法）

```bash
# Vercel CLIでログイン
vercel login

# 環境変数を設定
vercel env add REDIS_HOST
# 入力: redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com
# Environment: Production, Preview, Development を選択

vercel env add REDIS_PORT
# 入力: 15687
# Environment: Production, Preview, Development を選択

vercel env add REDIS_PASSWORD
# 入力: [Redis Cloudのパスワード]
# Environment: Production, Preview, Development を選択
```

---

## 🚀 手順3: 再デプロイ（重要！）

### 方法1: Vercelダッシュボードから再デプロイ

1. **Deployments タブ**を開く
2. 最新のデプロイの「...」メニューをクリック
3. **「Redeploy」**を選択
4. **「Use existing Build Cache」のチェックを外す**（重要！）
5. **「Redeploy」**ボタンをクリック

### 方法2: 空コミットで再デプロイ

```bash
cd /home/planj/patshinko-exam-app
git commit --allow-empty -m "fix: Redeploy with Redis environment variables"
git push origin main
```

---

## 🧪 手順4: 動作確認

### 1. API Health チェック
```bash
curl https://pachinko-lawtest.vercel.app/api/health
```

期待される結果:
```json
{
  "status": "ok",
  "message": "API is working!"
}
```

### 2. トークン検証テスト
```bash
curl -X POST https://pachinko-lawtest.vercel.app/api/validate-token \
  -H "Content-Type: application/json" \
  -d '{"token": "039742a2-f799-4574-8530-a8e1d81960f1", "email": "test001@example.com"}'
```

期待される結果:
```json
{
  "valid": true,
  "message": "有効な招待URLです"
}
```

### 3. ブラウザでテスト
```
https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
```

---

## ⚠️ トラブルシューティング

### 環境変数が反映されない場合

1. **キャッシュクリア**
   - Redeployする際、必ず「Use existing Build Cache」のチェックを外す

2. **Function Logs確認**
   ```
   Vercel Dashboard → Functions → validate-token → View Logs
   ```

3. **環境変数の確認**
   ```bash
   vercel env ls
   ```

### まだエラーが出る場合

1. **Redis Cloud側の確認**
   - データベースがActiveか
   - 接続数制限に達していないか
   - パスワードが正しいか

2. **Vercel Logsでエラー詳細確認**
   ```
   Vercel Dashboard → Functions → エラーログを確認
   ```

---

## 📊 チェックリスト

- [ ] Redis Cloudでパスワード確認
- [ ] Vercelで REDIS_HOST 設定
- [ ] Vercelで REDIS_PORT 設定
- [ ] Vercelで REDIS_PASSWORD 設定
- [ ] 再デプロイ実行（キャッシュなし）
- [ ] API Health チェック成功
- [ ] トークン検証テスト成功
- [ ] 招待URLアクセステスト成功

---

**所要時間**: 約5分
**優先度**: 🔴 最優先（今すぐ実行）