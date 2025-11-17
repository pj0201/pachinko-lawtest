# デプロイとテスト手順ガイド

## 📋 実施した修正内容

### 1. API URL修正
- **問題**: GitHub PagesからVercel APIへのリクエストが相対パス（`/api/*`）のため404エラー
- **解決**: API呼び出しを絶対パス（`https://pachinko-lawtest.vercel.app/api/*`）に変更

### 2. 修正ファイル一覧
- ✅ `src/config/api.js` - API設定ファイル（新規作成）
- ✅ `src/pages/Register.jsx` - 登録API呼び出し修正
- ✅ `src/components/ProtectedRoute.jsx` - セッション検証API修正
- ✅ `src/components/Home.jsx` - PDF URL生成修正
- ✅ `.env.production` - Vercel API URL環境変数

## 🚀 デプロイ手順

### 1. GitHubへプッシュ

```bash
# すでにコミット済み（commit: c83ea8c）
# GitHubへプッシュ
git push origin main
```

### 2. GitHub Pagesのデプロイ確認

1. **GitHub リポジトリにアクセス**
   - https://github.com/pj0201/pachinko-lawtest

2. **Actions タブを確認**
   - デプロイワークフローの実行状況を確認
   - 緑のチェックマークが表示されるまで待つ（約2-5分）

3. **Settings → Pages で状況確認**
   - Your site is published at: `https://pj0201.github.io/pachinko-lawtest/`

## 🧪 テスト手順

### 1. ブラウザでの基本動作確認

```bash
# 開発者ツールのコンソールを開いた状態でアクセス
```

1. **招待URLテスト**
   ```
   https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123
   ```

2. **コンソールログ確認**
   ```
   🔧 API Base URL: https://pachinko-lawtest.vercel.app/api
   🔧 Current hostname: pj0201.github.io
   ```

### 2. ネットワークタブでのAPI確認

1. **開発者ツール → Network タブ**

2. **確認すべきリクエスト**
   - ✅ `https://pachinko-lawtest.vercel.app/api/validate-token`
   - ✅ `https://pachinko-lawtest.vercel.app/api/register`
   - ❌ ~~`https://pj0201.github.io/pachinko-lawtest/api/*`~~ （これが出たらNG）

### 3. 登録フローテスト

```yaml
テストケース1: 新規登録
  1. URL: https://pj0201.github.io/pachinko-lawtest/?token=TEST_002_DEF456
  2. 入力:
     - ユーザー名: テストユーザー002
     - メール: test002@example.com
  3. 期待結果:
     - 登録成功 → ホーム画面遷移
     - localStorage にセッション情報保存

テストケース2: 重複トークン
  1. URL: https://pj0201.github.io/pachinko-lawtest/?token=TEST_001_ABC123
  2. 期待結果:
     - エラー: "この招待URLは既に使用されています"
```

### 4. APIヘルスチェック

```bash
# ターミナルから直接確認
curl https://pachinko-lawtest.vercel.app/api/health

# 期待される応答
{
  "status": "ok",
  "timestamp": "2025-11-17T...",
  "service": "pachinko-exam-backend",
  "problems_loaded": 540,
  "redis": {
    "status": "connected",
    "configured": true,
    "host": "redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com"
  }
}
```

## 🔍 トラブルシューティング

### 問題1: まだ404エラーが出る場合

**確認事項：**
1. GitHub Pages のデプロイが完了しているか
2. ブラウザのキャッシュをクリア（Ctrl+Shift+R）
3. コンソールでAPI_BASE_URLを確認

```javascript
// ブラウザコンソールで実行
console.log(window.location.hostname)  // "pj0201.github.io" であることを確認
```

### 問題2: CORSエラーが出る場合

**エラーメッセージ例：**
```
Access to fetch at 'https://pachinko-lawtest.vercel.app/api/...' from origin 'https://pj0201.github.io' has been blocked by CORS policy
```

**対策：**
- Vercel側のCORS設定を確認（vercel.jsonのheaders設定）

### 問題3: Redis接続エラー

**症状：**
- 登録時に "サーバーとの通信に失敗しました" エラー

**確認：**
- Vercel環境変数（REDIS_PASSWORD）が設定されているか
- Redis Cloud（redis-pink-notebook）が稼働中か

## ✅ チェックリスト

- [ ] GitHubへのプッシュ完了
- [ ] GitHub Pages デプロイ完了（約5分待つ）
- [ ] コンソールでAPI_BASE_URL確認
- [ ] validate-token APIへのリクエスト成功
- [ ] register APIへのリクエスト成功
- [ ] 新規登録フロー完了
- [ ] ホーム画面への遷移成功

## 📝 次のステップ

修正が正常に動作した場合：
1. ✅ サーバーエラー問題解決
2. 本番テスト実施
3. ユーザーへの通知

まだ問題がある場合：
1. エラーログの詳細を確認
2. ネットワークタブでリクエスト/レスポンスを詳細確認
3. 必要に応じて追加修正

---

**作成日時**: 2025-11-17 21:15
**作成者**: Claude Opus (Worker3)
**コミットID**: c83ea8c