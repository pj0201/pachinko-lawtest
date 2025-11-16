# 招待トークン設定手順

## 前提条件

✅ Vercel KVストレージが設定済み（環境変数: `KV_REST_API_URL`, `KV_REST_API_TOKEN`）

## 招待トークンの初期化

### ステップ1: Vercelダッシュボードで環境変数を確認

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクトを選択
3. **Settings** → **Environment Variables**で以下を確認：
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`

### ステップ2: ローカルで招待トークンを登録

```bash
# 依存関係をインストール（未実行の場合）
npm install

# 環境変数を設定（.env.localファイルを作成）
echo "KV_REST_API_URL=your_kv_url" > .env.local
echo "KV_REST_API_TOKEN=your_kv_token" >> .env.local

# 招待トークン初期化スクリプトを実行
node scripts/init-invite-tokens.js
```

### ステップ3: Vercelで直接実行（推奨）

Vercel CLIを使用して、本番環境で直接トークンを登録：

```bash
# Vercel CLIをインストール（未インストールの場合）
npm i -g vercel

# Vercelにログイン
vercel login

# プロジェクトにリンク
vercel link

# 本番環境でスクリプトを実行
vercel env pull .env.production.local
node scripts/init-invite-tokens.js
```

## 登録される招待トークン（10個）

1. `039742a2-f799-4574-8530-a8e1d81960f1`
2. `cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb`
3. `d0b28ab3-44b6-45aa-897b-e72e0e0da116`
4. `babcd6fb-b8a8-46a8-b3a6-fc00966d07a3`
5. `b1b281a3-6b76-4659-9827-bf3a07b6c3ba`
6. `12f622c2-cbf4-4631-abb7-7336c841b198`
7. `3c756c94-0d98-4d8b-b466-17e99f1b3240`
8. `2b1d54e2-97a0-4900-a513-fab986540358`
9. `d47c9566-cabd-4d96-91d0-41afc10a59b6`
10. `c502c94a-3e4e-471e-9835-2f05018751e4`

## 招待URL一覧

- https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
- https://pachinko-lawtest.vercel.app/invite/cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb
- https://pachinko-lawtest.vercel.app/invite/d0b28ab3-44b6-45aa-897b-e72e0e0da116
- https://pachinko-lawtest.vercel.app/invite/babcd6fb-b8a8-46a8-b3a6-fc00966d07a3
- https://pachinko-lawtest.vercel.app/invite/b1b281a3-6b76-4659-9827-bf3a07b6c3ba
- https://pachinko-lawtest.vercel.app/invite/12f622c2-cbf4-4631-abb7-7336c841b198
- https://pachinko-lawtest.vercel.app/invite/3c756c94-0d98-4d8b-b466-17e99f1b3240
- https://pachinko-lawtest.vercel.app/invite/2b1d54e2-97a0-4900-a513-fab986540358
- https://pachinko-lawtest.vercel.app/invite/d47c9566-cabd-4d96-91d0-41afc10a59b6
- https://pachinko-lawtest.vercel.app/invite/c502c94a-3e4e-471e-9835-2f05018751e4

## トラブルシューティング

### エラー: `KV_REST_API_URL is not defined`

環境変数が設定されていません。Vercelダッシュボードで確認してください。

### エラー: `Connection refused`

Vercel KVストレージがプロビジョニングされていない可能性があります。

1. Vercelダッシュボード → **Storage** → **Create Database** → **KV**
2. データベースを作成
3. 環境変数が自動的に追加されることを確認

### トークンが使用済みになっている

トークンをリセットする場合：

```javascript
// Vercel Functions > New Function で以下を実行
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  const token = 'トークンID';
  const tokenData = await kv.get(`invite:${token}`);

  if (tokenData) {
    await kv.set(`invite:${token}`, {
      ...tokenData,
      used: false,
      usedBy: null,
      usedAt: null
    });
    res.json({ success: true, message: 'トークンをリセットしました' });
  } else {
    res.status(404).json({ error: 'トークンが見つかりません' });
  }
}
```

## 確認方法

招待URLにアクセスして、登録フォームが表示されれば成功です：

https://pachinko-lawtest.vercel.app/invite/039742a2-f799-4574-8530-a8e1d81960f1
