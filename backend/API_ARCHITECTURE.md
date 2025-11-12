# バックエンドAPIアーキテクチャ

このアプリケーションは2つのバックエンドサーバーで構成されています。

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                     Vite Dev Server (port 5173)              │
│                         React Frontend                       │
└────────────────────┬──────────────────┬─────────────────────┘
                     │                  │
        ┌────────────▼──────────┐      │
        │   Flask (port 5000)   │      │
        │   メインバックエンド    │      │
        │  - 問題取得API        │      │
        │  - 認証API           │      │
        │  - フロントエンド配信   │      │
        └───────────────────────┘      │
                                       │
                        ┌──────────────▼─────────────┐
                        │   Express (port 3001)      │
                        │   サポートバックエンド       │
                        │  - OCR処理                 │
                        │  - データベース操作          │
                        │  - ログ取得                │
                        └────────────────────────────┘
```

## エンドポイント振り分け（vite.config.js）

| パス                  | 転送先         | 役割                     |
|----------------------|---------------|-------------------------|
| `/api/ocr`           | Express:3001  | OCR処理                 |
| `/api/pdf-ocr`       | Express:3001  | OCR処理                 |
| `/api/db`            | Express:3001  | データベース操作          |
| `/api/logs`          | Express:3001  | ログ取得                 |
| `/api/*` (その他)     | Flask:5000    | 問題取得、認証、PDF配信   |

## Flask (port 5000) - メインバックエンド

### 担当機能
- **フロントエンド配信**: React distフォルダを配信
- **問題取得API**: 試験問題データの提供
- **認証API**: ユーザー登録・セッション管理
- **PDF配信**: 法律文書のPDF配信

### 主要エンドポイント
```
GET  /                              # React アプリ
GET  /api/health                    # ヘルスチェック
POST /api/auth/verify-invite        # 招待URL検証
POST /api/auth/register             # ユーザー登録
POST /api/auth/verify-session       # セッション検証
POST /api/problems/quiz             # ランダム問題取得
GET  /api/problems/all              # 全問題取得
GET  /api/problems/stats            # 問題統計
GET  /api/problems/<int:problem_id> # 特定問題取得
GET  /api/pdf/<path:filename>       # PDF配信
```

## Express (port 3001) - サポートバックエンド

### 担当機能
- **OCR処理**: PDF文書のOCR処理
- **データベース操作**: 問題データベースの直接操作（開発用）
- **ログ取得**: バックエンドログの取得

### 主要エンドポイント
```
GET  /health                    # ヘルスチェック
POST /api/pdf-ocr               # OCR処理開始
GET  /api/pdf-ocr/results       # OCR結果取得
GET  /api/pdf-ocr/stats         # OCR統計
GET  /api/logs                  # ログ取得
GET  /api/db/*                  # データベース操作（database_routes.jsで定義）
```

### 開発用エンドポイント（非推奨）
以下のエンドポイントは開発用として残していますが、本番では Flask が担当します：
```
GET  /api/problems              # 全問題取得 → Flask使用を推奨
GET  /api/problems/theme/:id    # テーマ別問題 → Flask使用を推奨
GET  /api/problems/category/:id # カテゴリ別問題 → Flask使用を推奨
POST /api/problems/quiz         # ランダム問題 → Flask使用を推奨
```

## 起動方法

### 開発環境
```bash
# Flask バックエンド起動
python3 backend/api_server.py

# Express バックエンド起動（別ターミナル）
node backend/server.js

# Vite 開発サーバー起動（別ターミナル）
npm run dev
```

### 本番環境
```bash
# ビルド
npm run build

# Flask のみ起動（フロントエンドも配信）
python3 backend/api_server.py
```

## 注意事項

1. **問題取得は Flask を使用**: `/api/problems/*` へのリクエストは Flask に転送されます
2. **OCR処理は Express を使用**: `/api/pdf-ocr` へのリクエストは Express に転送されます
3. **本番環境では Flask のみ**: 本番環境では Flask がフロントエンドと問題APIを提供します
4. **Express は開発支援ツール**: Express は主にOCR処理や開発時のデータベース操作に使用します

## トラブルシューティング

### 問題取得APIが動作しない
- Flask (port 5000) が起動しているか確認
- `/backend/db/problems.json` が存在するか確認

### OCR処理が動作しない
- Express (port 3001) が起動しているか確認
- Python依存関係がインストールされているか確認

### フロントエンドが表示されない
- `npm run build` でビルドしたか確認
- Flask が起動しているか確認
- `/dist` ディレクトリが存在するか確認
