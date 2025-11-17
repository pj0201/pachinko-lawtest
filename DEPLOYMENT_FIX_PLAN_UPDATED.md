# デプロイメント修正計画書（更新版）

## 🚨 重要な発見：デプロイ環境の根本的変更

### 最新のマージ内容（2025-11-17確認）

**リポジトリは Railway から Vercel に完全移行済み**

#### 最近のPRマージ：
1. PR #11: Vercel KV登録APIをサーバーレス関数に統合
2. PR #10: Redis接続とUUID v4トークン対応
3. PR #9: 登録ルート修正
4. PR #8: @vercel/kvからioredisに変更（Redis Cloud対応）

## 📋 現在のアーキテクチャ

### **現在：Vercelサーバーレス構成**

| コンポーネント | 技術スタック | ファイル |
|-------------|------------|---------|
| **フロントエンド** | React + Vite | `/dist` (ビルド済み) |
| **バックエンド** | Node.js サーバーレス | `/api/index.js` |
| **データベース** | Redis Cloud | 外部サービス |
| **ホスティング** | Vercel | `vercel.json` |
| **認証API** | Python（未使用？） | `/api/auth/register.py` |

### **旧構成（廃止済み）**

| コンポーネント | 技術スタック | ファイル |
|-------------|------------|---------|
| **フロントエンド** | React + Vite | 同じ |
| **バックエンド** | Python Flask | `/backend/api_server.py` |
| **データベース** | SQLite | `/backend/alpha_auth.db` |
| **ホスティング** | Railway | `Dockerfile`, `nixpacks.toml` |

## 🔍 問題の再定義

### 元の問題理解（誤り）
- **誤認**: Railwayへのデプロイが失敗している
- **誤認**: DockerfileとNixpacksの競合が原因

### 実際の状況（正しい理解）
- **事実**: すでにVercelに移行済み
- **事実**: テストURLは GitHub Pages（静的ホスティング）
- **問題**: サーバーレス関数が正常に動作していない可能性

## 🎯 真の問題と対策

### 問題1: API エンドポイントの不整合

#### 症状：
- GitHub Pagesからのリクエストがサーバーレス関数に到達していない

#### 原因：
```javascript
// フロントエンドのAPI設定が旧環境のまま
const API_URL = process.env.VITE_API_URL || 'http://localhost:5000'
```

#### 対策：
```javascript
// .env.production
VITE_API_URL=https://patshinko-exam-app.vercel.app/api
```

### 問題2: Redis Cloud 接続エラー

#### 症状：
- 認証・データ保存が機能しない

#### 確認事項：
```bash
# Vercel環境変数に以下が設定されているか
REDIS_HOST=redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com
REDIS_PORT=15687
REDIS_PASSWORD=<実際のパスワード>
```

### 問題3: GitHub Pages と Vercel API の CORS 問題

#### 症状：
- `https://pj0201.github.io` から Vercel API へのリクエストがブロック

#### 対策：
```javascript
// vercel.json の CORS設定を更新
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://pj0201.github.io"  // * から特定ドメインに変更
        }
      ]
    }
  ]
}
```

## 📊 修正アクションプラン

### Phase 1: 設定ファイルの更新（即座）

1. **環境変数設定ファイル作成**
```bash
# .env.production
VITE_API_URL=https://patshinko-exam-app.vercel.app/api
```

2. **ビルドコマンド更新**
```json
// package.json
{
  "scripts": {
    "build": "vite build --mode production"
  }
}
```

### Phase 2: Vercel設定の確認（5分）

1. **Vercel ダッシュボードで環境変数確認**
   - REDIS_HOST
   - REDIS_PORT
   - REDIS_PASSWORD

2. **デプロイメントログ確認**
   ```bash
   vercel logs --follow
   ```

### Phase 3: API テスト（10分）

1. **ヘルスチェック**
```bash
curl https://patshinko-exam-app.vercel.app/api/health
```

2. **問題データ取得**
```bash
curl https://patshinko-exam-app.vercel.app/api/problems
```

### Phase 4: フロントエンド修正（必要な場合）

1. **API URLの動的設定**
```javascript
// src/config/api.js
export const API_BASE_URL =
  process.env.NODE_ENV === 'production'
    ? 'https://patshinko-exam-app.vercel.app/api'
    : 'http://localhost:3000/api';
```

## 🚀 推奨デプロイ方法

### オプション1: Vercel完全移行（推奨）

1. **フロントエンドもVercelにデプロイ**
```bash
# GitHub Pages を廃止し、Vercelで全てホスト
vercel --prod
```

**メリット**:
- API と同一ドメイン（CORS問題解消）
- 環境変数の一元管理
- デプロイの簡素化

### オプション2: ハイブリッド構成（現状維持）

1. **GitHub Pages + Vercel API**
   - フロントエンド: GitHub Pages
   - API: Vercel サーバーレス関数

**必要な修正**:
- CORS設定の調整
- API URLのハードコード

## ⚠️ 削除すべきファイル

以下のRailway関連ファイルは不要：
```bash
rm Dockerfile
rm .dockerignore
rm nixpacks.toml
rm .railwayignore
rm backend/api_server.py  # Vercel移行後は不要
```

## ✅ チェックリスト

- [ ] Vercel環境変数（REDIS_*）設定確認
- [ ] API エンドポイントの疎通確認
- [ ] CORS設定の更新
- [ ] フロントエンドのAPI URL更新
- [ ] 不要ファイルの削除
- [ ] デプロイメント実行

## 📝 結論

**根本原因**: Railway デプロイの問題ではなく、**Vercel サーバーレス環境の設定問題**

**対策**:
1. 環境変数の確認と設定
2. API URLの正しい設定
3. CORS設定の調整

**テストURL問題の真の解決策**:
- GitHub Pages (`https://pj0201.github.io/pachinko-lawtest/`) が
- Vercel API (`https://patshinko-exam-app.vercel.app/api`) を正しく呼び出せるように設定

---

**作成日時**: 2025-11-17 20:45
**作成者**: Claude Opus (Worker3)
**ステータス**: 待機中（オーナーの指示待ち）
**重要**: Railway関連の修正は不要。Vercel環境の設定確認が必要。