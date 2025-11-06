# 🚀 バックエンドアプリケーション - セットアップガイド

**アプリケーション**: 遊技機取扱主任者試験 1491問アプリ
**フレームワーク**: Flask
**バージョン**: Python 3.8+

---

## 📁 ファイル構成

```
backend/
├─ app.py                           # メインアプリケーション
├─ requirements.txt                  # 依存パッケージリスト
├─ SETUP_GUIDE.md                   # このファイル
├─ API_DOCUMENTATION.md              # API仕様書
└─ (その他のスクリプト)
```

---

## 🔧 セットアップ手順

### 方法1: 直接実行（開発環境）

```bash
# 1. ディレクトリに移動
cd /home/planj/patshinko-exam-app/backend

# 2. Flaskをインストール
python3 -m pip install --break-system-packages Flask Flask-CORS

# 3. アプリケーションを実行
python3 app.py
```

**アクセス**: `http://localhost:5000`

### 方法2: 仮想環境を使用（推奨）

```bash
# 1. 仮想環境を作成
python3 -m venv venv

# 2. 仮想環境を有効化
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. アプリケーションを実行
python3 app.py
```

### 方法3: Docker を使用

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
```

**ビルドと実行**:
```bash
docker build -t patshinko-app .
docker run -p 5000:5000 patshinko-app
```

---

## 📊 データソース

**ファイル**: `/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json`

**内容**:
- 1,491問の問題
- すべての問題に風営法の条項引用付き
- 難易度★～★★★★
- 6大カテゴリ
- 12パターン
- 89テーマ

---

## 🎯 主要な機能

### 1. 問題の取得

```python
# ランダムに1問を取得
GET /api/problems/random

# 難易度★★の営業許可関連の問題を3問取得
GET /api/problems/random?count=3&difficulty=★★&category=営業許可関連

# 特定の問題IDで取得
GET /api/problems/1
```

### 2. クイズ形式

```python
# 10問のクイズを取得
POST /api/problems/quiz
{
  "count": 10,
  "difficulty": "★★★",
  "category": "遊技機管理"
}
```

### 3. 問題の検索

```python
# テーマで検索
GET /api/problems/by-theme/営業許可は無期限有効

# 複合条件で検索
GET /api/problems/search?difficulty=★&category=営業許可関連&limit=20
```

### 4. メタデータ取得

```python
# 統計情報
GET /api/problems/stats

# カテゴリ一覧
GET /api/problems/categories

# パターン一覧
GET /api/problems/patterns

# 難易度一覧
GET /api/problems/difficulties

# テーマ一覧
GET /api/problems/themes
```

---

## 🧪 動作確認

### ヘルスチェック

```bash
curl http://localhost:5000/api/health
```

**期待される応答**:
```json
{
  "status": "ok",
  "problems_loaded": true,
  "total_problems": 1491
}
```

### 統計情報確認

```bash
curl http://localhost:5000/api/problems/stats
```

### ランダムな問題を取得

```bash
curl "http://localhost:5000/api/problems/random?count=1"
```

---

## 🔌 CORS設定

アプリケーションはCORS有効で、すべてのオリジンからのリクエストを受け付けます。

```python
from flask_cors import CORS
CORS(app)
```

本番環境では以下のように制限してください：

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 📈 パフォーマンス最適化

### キャッシング

問題データはアプリケーション起動時に一度ロードされ、メモリにキャッシュされます。

```python
_problems_cache = None

def load_problems():
    global _problems_cache
    if _problems_cache is None:
        # JSONをロード
        _problems_cache = json.load(f)
    return _problems_cache
```

### ページング

大量の問題を取得する場合はページングを使用してください：

```bash
curl "http://localhost:5000/api/problems/list?page=1&per_page=30"
```

---

## 🔒 セキュリティ

### 本番環境での推奨設定

```python
# デバッグモードを無効化
app.run(debug=False)

# SECRET_KEYを設定
app.config['SECRET_KEY'] = 'your-secret-key'

# HTTPS を強制
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

---

## 🚀 本番デプロイ

### Gunicorn を使用

```bash
# インストール
pip install gunicorn

# 起動（4ワーカー）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx リバースプロキシ設定

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd サービス設定

```ini
# /etc/systemd/system/patshinko-app.service
[Unit]
Description=Patshinko Exam App
After=network.target

[Service]
Type=notify
User=planj
WorkingDirectory=/home/planj/patshinko-exam-app/backend
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 📝 ログ設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🐛 トラブルシューティング

### 問題: JSONファイルが見つからない

**原因**: ファイルパスが正しくない

**解決**:
```bash
ls -lh /home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json
```

### 問題: ポート5000が既に使用されている

**解決**:
```bash
# ポート8000で実行
python3 app.py --port 8000
```

または `app.py` の最後を修正：
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
```

### 問題: CORS エラー

**原因**: クロスオリジンリクエストがブロックされている

**確認**:
```bash
curl -H "Origin: http://example.com" -H "Access-Control-Request-Method: GET" \
  http://localhost:5000/api/health
```

---

## 📞 サポート

### ログを確認

```bash
# アプリケーションログ
tail -f app.log

# システムログ（Systemd使用時）
journalctl -u patshinko-app -f
```

### ディバッグモード

```python
# app.py の最後を以下に変更
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 📊 API使用統計

### 呼び出し追跡

```python
import time
from functools import wraps

def track_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        elapsed_time = time.time() - start_time
        app.logger.info(f"{f.__name__} - {elapsed_time:.3f}s")
        return result
    return decorated_function
```

---

## ✅ チェックリスト

本番デプロイ前に確認：

- [ ] Flaskがインストールされている
- [ ] JSONファイルが正しい場所にある
- [ ] すべてのエンドポイントが動作している
- [ ] CORS設定が適切か確認
- [ ] ログ出力が設定されている
- [ ] エラーハンドリングが実装されている
- [ ] パフォーマンステストを実施
- [ ] セキュリティ設定を確認

---

**最終更新**: 2025年10月22日
**ステータス**: ✅ 本番投入準備完了
