# 🎰 遊技機取扱主任者試験 学習アプリ

風営法に基づく遊技機取扱主任者試験の学習用Webアプリケーションです。

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/pj0201/pachinko-lawtest)

## ✨ 特徴

- ✅ **626問の高品質問題**: ぱちんこ業界（第4号営業）に特化
- ✅ **カテゴリ別学習**: 遊技機管理、営業規制、保安・風紀、景品規制など
- ✅ **詳細な解説**: 各問題に法的根拠と詳細な説明
- ✅ **レスポンシブデザイン**: PC・タブレット・スマホ対応
- ✅ **進捗管理**: 学習履歴と成績を記録

## 🚀 クイックスタート

### Vercelでデプロイ（推奨）

上記の「Deploy with Vercel」ボタンをクリックするだけで、数分でデプロイ完了！

詳細は [DEPLOY.md](./DEPLOY.md) を参照

### ローカル開発

```bash
# 依存関係をインストール
npm install

# 開発サーバー起動
npm run dev

# バックエンドサーバー起動（別ターミナル）
node backend/server.js
```

アクセス:
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:3001

### ビルド

```bash
npm run build
```

ビルド成果物は `dist/` ディレクトリに出力されます。

## 📁 プロジェクト構成

```
.
├── api/                    # Vercelサーバーレス関数
│   └── index.js           # メインAPIエンドポイント
├── backend/               # ローカル開発用バックエンド
│   ├── server.js          # Express サーバー
│   ├── db-loader.js       # データローダー
│   └── db/
│       └── problems.json  # 問題データ（626問）
├── src/                   # フロントエンドソース
│   ├── components/        # Reactコンポーネント
│   ├── pages/            # ページコンポーネント
│   └── utils/            # ユーティリティ関数
├── public/               # 静的ファイル
├── dist/                 # ビルド出力（生成される）
├── vercel.json           # Vercel設定
└── package.json          # 依存関係
```

## 🔌 API エンドポイント

### ヘルスチェック
```http
GET /api/health
```

### 全問題取得
```http
GET /api/problems
```

### 問題総数
```http
GET /api/problems/count
```

### クイズ問題取得
```http
POST /api/problems/quiz
Content-Type: application/json

{
  "count": 10,
  "difficulty": "★★"
}
```

### カテゴリ別問題
```http
GET /api/problems/category/:category
```

例: `/api/problems/category/遊技機管理`

### テーマ別問題
```http
GET /api/problems/theme/:themeId
```

## 🛠️ 技術スタック

### フロントエンド
- **React 18** - UIライブラリ
- **Vite** - ビルドツール
- **React Router** - ルーティング
- **Axios** - HTTP クライアント

### バックエンド
- **Node.js** - ランタイム
- **Express** - Web フレームワーク
- **Vercel Functions** - サーバーレス関数

### インフラ
- **Vercel** - ホスティング・デプロイ
- **GitHub** - バージョン管理

## 📊 データ情報

**問題データ**: `backend/db/problems.json`
- 総問題数: 626問
- 最終更新: 2025-11-12
- バージョン: 8.3（ぱちんこ業界特化版）

カテゴリ構成:
- 遊技機管理
- 営業規制
- 保安・風紀
- 景品規制
- その他法令

## 🔧 開発

### 依存関係の追加

```bash
npm install <package-name>
```

### コードフォーマット

```bash
npm run lint
```

### テスト

```bash
# APIテスト
curl http://localhost:3001/api/health

# フロントエンドビルドテスト
npm run build
```

## 📝 ライセンス

このプロジェクトは教育目的で作成されています。

## 🤝 コントリビューション

Issue や Pull Request を歓迎します！

## 📮 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

Made with ❤️ for 遊技機取扱主任者試験受験者
