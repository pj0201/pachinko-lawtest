# Railway デプロイ修正計画書

## 📋 調査結果サマリー

### 現状の問題点

#### 1. **ビルドシステムの競合**
- **Dockerfile** と **nixpacks.toml** の両方が存在
- Railwayがどちらを使うべきか混乱している状態
- 結果として、不適切なビルドコマンドが実行されている

#### 2. **設定の不一致**
| ファイル | Python環境 | 起動コマンド |
|---------|-----------|------------|
| **Dockerfile** | システムPython3 (`pip3 --break-system-packages`) | `python3 -u backend/api_server.py` |
| **nixpacks.toml** | venv使用 (`source .venv/bin/activate`) | `source .venv/bin/activate && python3 backend/api_server.py` |
| **package.json** | システムPython3 | `python3 backend/api_server.py` |

#### 3. **エラーの根本原因**
- DEPLOYMENT_LOG.mdによると、ビルドは成功するがデプロイ時にクラッシュ
- Railpackが `python` コマンドを使用（Python3環境では `python3`）
- Dockerfileが実際には無視されている可能性大

## 🎯 推奨対策（優先度順）

### 対策1: **Dockerfileのみを使用する（推奨）**

#### 実装手順：

1. **nixpacks.tomlを削除**
```bash
rm nixpacks.toml
```

2. **Railway設定ファイル（railway.toml）を作成**
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "./Dockerfile"

[deploy]
startCommand = "python3 -u backend/api_server.py"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

3. **Dockerfileを最適化**
```dockerfile
FROM node:22-slim

# Python3とpipをインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# Node.js依存関係をインストール
RUN npm ci --only=production

# アプリケーションコードをコピー
COPY . .

# React アプリをビルド
RUN npm run build

# Python依存関係をインストール（venv使用に変更）
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r backend/requirements.txt

# ポート公開
EXPOSE ${PORT:-5000}

# サーバー起動（venv内のPythonを使用）
CMD ["/app/venv/bin/python", "-u", "backend/api_server.py"]
```

### 対策2: **nixpacks.tomlのみを使用する（代替案）**

#### 実装手順：

1. **Dockerfileを削除**
```bash
rm Dockerfile
```

2. **nixpacks.tomlを修正**
```toml
[phases.setup]
nixPkgs = ["nodejs_22", "python311", "python311Packages.pip"]

[phases.install]
cmds = [
  "npm ci --only=production",
  "pip install --user -r backend/requirements.txt"
]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "python3 -u backend/api_server.py"

[variables]
PORT = "5000"
```

### 対策3: **Railway.yamlで明示的にDockerを指定（緊急対策）**

#### 実装手順：

1. **railway.yaml を作成**
```yaml
version: 1
build:
  builder: dockerfile
  dockerfilePath: ./Dockerfile
deploy:
  startCommand: python3 -u backend/api_server.py
  healthcheckPath: /api/health
  restartPolicyType: ON_FAILURE
  restartPolicyMaxRetries: 3
```

## 🔧 追加の修正点

### api_server.py の改善
```python
# ポート設定をより堅牢に
port = int(os.environ.get('PORT', os.environ.get('RAILWAY_PORT', 5000)))

# ヘルスチェックエンドポイントを確実に
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'problems_loaded': len(problems_data) > 0
    })
```

### package.json の修正
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "echo 'Starting Python server...' && python3 -u backend/api_server.py",
    "start:prod": "python3 -u backend/api_server.py"
  }
}
```

## 📊 実装優先度

| 優先度 | タスク | 理由 | 推定作業時間 |
|--------|--------|------|-------------|
| **1** | nixpacks.toml削除 | 競合解消が最優先 | 1分 |
| **2** | railway.toml作成 | Railway側で明示的にDockerを指定 | 5分 |
| **3** | Dockerfile最適化 | venv使用で環境を隔離 | 10分 |
| **4** | api_server.py改善 | ヘルスチェック強化 | 5分 |
| **5** | デプロイ実行 | 修正確認 | 10分 |

## ✅ テスト手順

1. **ローカル確認（WSLの場合はスキップ可）**
```bash
# ビルド
docker build -t patshinko-test .

# 実行
docker run -e PORT=5000 -p 5000:5000 patshinko-test
```

2. **Railway デプロイ**
```bash
git add -A
git commit -m "fix: Railway deployment configuration - use Docker only"
git push origin main
```

3. **確認項目**
- Railway ダッシュボードでビルドログ確認
- デプロイステータスが "Active" になるか
- `/api/health` エンドポイントが応答するか
- テストURLでアプリが動作するか

## 🚨 リスクと対策

| リスク | 影響度 | 対策 |
|--------|--------|------|
| Dockerビルド失敗 | 高 | nixpacks.tomlをバックアップしておく |
| PORT環境変数の不一致 | 中 | Railway側で明示的に設定 |
| ヘルスチェック失敗 | 中 | タイムアウトを300秒に延長 |

## 📝 結論

**推奨アプローチ**: **対策1（Dockerfileのみ使用）** を実装

### 理由：
1. Dockerfileは既に存在し、構文も正しい
2. Node.js + Pythonの複雑な環境をDockerで完全制御できる
3. ローカル開発環境と本番環境の一致を保証
4. Railwayの新しい標準はDocker優先

### 次のアクション：
1. nixpacks.toml を削除
2. railway.toml を作成
3. コミット＆プッシュ
4. Railway ダッシュボードで結果確認

---

**作成日時**: 2025-11-17 20:45
**作成者**: Claude Opus (Worker3)
**ステータス**: レビュー待ち