# 🚀 Vercelデプロイ手順

## ワンクリックデプロイ

以下のボタンをクリックするだけでVercelにデプロイできます：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/pj0201/pachinko-lawtest)

## 手動デプロイ手順

### 1. Vercelアカウントの準備

1. [Vercel](https://vercel.com)にアクセス
2. GitHubアカウントでサインアップ/ログイン

### 2. GitHubリポジトリと連携

1. Vercelダッシュボードで「Add New...」→「Project」をクリック
2. 「Import Git Repository」でこのリポジトリを選択
3. 「Import」をクリック

### 3. プロジェクト設定

**Framework Preset**: Vite

**Build Command**:
```bash
npm run build
```

**Output Directory**:
```
dist
```

**Install Command**:
```bash
npm install
```

### 4. 環境変数の設定（必要な場合）

Vercelダッシュボードの「Settings」→「Environment Variables」で設定：

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `NODE_ENV` | `production` | 本番環境モード |

### 5. デプロイ

「Deploy」ボタンをクリック

デプロイが完了すると、URLが発行されます：
- 本番環境: `https://your-project.vercel.app`
- プレビュー環境: PRごとに自動生成

## 自動デプロイ設定

GitHubリポジトリと連携後、以下のブランチへのpushで自動デプロイされます：

- **mainブランチ** → 本番環境に自動デプロイ
- **その他ブランチ** → プレビュー環境に自動デプロイ
- **Pull Request** → プレビュー環境に自動デプロイ

## APIエンドポイント

デプロイ後、以下のAPIエンドポイントが利用可能：

- `GET /api/health` - ヘルスチェック
- `GET /api/problems` - 全問題取得
- `GET /api/problems/count` - 問題総数
- `POST /api/problems/quiz` - クイズ問題取得
- `GET /api/problems/category/:category` - カテゴリ別問題
- `GET /api/problems/theme/:themeId` - テーマ別問題

## トラブルシューティング

### ビルドエラーが発生する場合

1. `package.json`の依存関係を確認
2. Vercelダッシュボードの「Deployments」でログを確認
3. Node.jsバージョンを確認（推奨: 18.x以上）

### APIが動作しない場合

1. `/api/health`エンドポイントでヘルスチェック
2. ブラウザの開発者ツールでネットワークタブを確認
3. Vercel Functions のログを確認

### データが表示されない場合

1. `backend/db/problems.json`が正しくデプロイされているか確認
2. APIレスポンスのステータスコードを確認
3. CORS設定を確認

## カスタムドメイン設定

1. Vercelダッシュボードで「Settings」→「Domains」
2. カスタムドメインを追加
3. DNSレコードを設定（Vercelが自動で指示）

## パフォーマンス最適化

Vercelでは自動的に以下が適用されます：

- ✅ CDN配信（グローバル）
- ✅ 自動SSL証明書
- ✅ Edge Caching
- ✅ Gzip圧縮
- ✅ HTTP/2対応

## サポート

問題が発生した場合：

1. [Vercelドキュメント](https://vercel.com/docs)を確認
2. GitHubのIssuesで報告
3. Vercelサポートに問い合わせ
