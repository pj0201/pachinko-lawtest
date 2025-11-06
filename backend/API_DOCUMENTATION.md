# 🎓 遊技機取扱主任者試験 1491問API - 完全ドキュメント

**バージョン**: 1.0
**ベース URL**: `http://localhost:5000`
**データソース**: `CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json`

---

## 📋 クイックスタート

### インストールと起動

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. サーバーを起動
python app.py

# 3. ヘルスチェック
curl http://localhost:5000/api/health
```

---

## 🔌 APIエンドポイント一覧

### 1. ヘルスチェック

**エンドポイント**: `GET /api/health`

**説明**: サーバーの状態と読み込まれた問題数を確認

**レスポンス例**:
```json
{
  "status": "ok",
  "problems_loaded": true,
  "total_problems": 1491
}
```

---

### 2. 統計情報を取得

**エンドポイント**: `GET /api/problems/stats`

**説明**: 総問題数、難易度分布、カテゴリ分布などの統計情報

**レスポンス例**:
```json
{
  "total_problems": 1491,
  "completion_rate": "100.0%",
  "problem_format": "true_false (〇×形式)",
  "statistics": {
    "total_problems": 1491,
    "difficulty_distribution": {
      "★": 250,
      "★★": 375,
      "★★★": 744,
      "★★★★": 122
    },
    "category_distribution": {
      "遊技機管理": 540,
      "不正対策": 240,
      ...
    },
    "pattern_distribution": {
      "基本知識": 125,
      "ひっかけ": 125,
      ...
    }
  }
}
```

---

### 3. カテゴリ一覧を取得

**エンドポイント**: `GET /api/problems/categories`

**説明**: すべてのカテゴリを取得

**レスポンス例**:
```json
{
  "categories": [
    "営業許可関連",
    "営業時間・規制",
    "型式検定関連",
    "不正対策",
    "景品規制",
    "遊技機管理"
  ]
}
```

---

### 4. パターン一覧を取得

**エンドポイント**: `GET /api/problems/patterns`

**説明**: すべての12パターンを取得

**レスポンス例**:
```json
{
  "patterns": [
    "基本知識",
    "ひっかけ",
    "用語比較",
    "優先順位",
    "時系列理解",
    "シナリオ判定",
    "複合違反",
    "数値正確性",
    "理由理解",
    "経験陥阱",
    "改正対応",
    "複合応用"
  ]
}
```

---

### 5. 難易度一覧を取得

**エンドポイント**: `GET /api/problems/difficulties`

**説明**: すべての難易度を取得

**レスポンス例**:
```json
{
  "difficulties": ["★", "★★", "★★★", "★★★★"]
}
```

---

### 6. テーマ一覧を取得

**エンドポイント**: `GET /api/problems/themes`

**説明**: すべての89テーマを取得

**レスポンス例**:
```json
{
  "themes": [
    "営業許可は無期限有効",
    "営業許可と型式検定の違い",
    "営業許可取得の要件",
    ...
  ]
}
```

---

### 7. 問題IDで問題を取得

**エンドポイント**: `GET /api/problems/<problem_id>`

**説明**: 特定の問題IDで問題を取得

**例**: `GET /api/problems/1`

**レスポンス例**:
```json
{
  "problem_id": 1,
  "theme_name": "新台設置の手続き",
  "category": "遊技機管理",
  "pattern_name": "基本知識",
  "difficulty": "★",
  "problem_text": "新台設置の手続きは、講習テキストで述べられている重要な知識である。",
  "correct_answer": "○",
  "explanation": "新台設置について正確に理解することは、営業管理の基本です。",
  "legal_reference": {
    "law": "風営法",
    "article": "第6条の2",
    "section": "（遊技機の設置）",
    "detail": "新台設置には遊技機の設置に関する規定を遵守する必要がある。"
  }
}
```

---

### 8. ランダムに問題を取得

**エンドポイント**: `GET /api/problems/random`

**説明**: ランダムに1問以上の問題を取得

**クエリパラメータ**:
- `count` (int, optional): 取得する問題数（デフォルト: 1, 最大: 100）
- `difficulty` (string, optional): 難易度（★, ★★, ★★★, ★★★★）
- `category` (string, optional): カテゴリ
- `pattern` (string, optional): パターン

**例**: `GET /api/problems/random?count=3&difficulty=★★&category=営業許可関連`

**レスポンス例**:
```json
{
  "count": 3,
  "problems": [
    { ... },
    { ... },
    { ... }
  ]
}
```

---

### 9. クイズ形式で複数問を取得

**エンドポイント**: `POST /api/problems/quiz`

**説明**: 複数の問題をクイズ形式で取得

**リクエストボディ**:
```json
{
  "count": 10,
  "difficulty": "★★★",
  "category": "遊技機管理",
  "pattern": "基本知識"
}
```

**レスポンス例**:
```json
{
  "quiz_count": 10,
  "total_problems": 10,
  "problems": [ ... ]
}
```

---

### 10. 問題を検索

**エンドポイント**: `GET /api/problems/search`

**説明**: 複数の条件で問題を検索

**クエリパラメータ**:
- `difficulty` (string, optional): 難易度
- `category` (string, optional): カテゴリ
- `pattern` (string, optional): パターン
- `theme` (string, optional): テーマ
- `limit` (int, optional): 最大件数（デフォルト: 50）

**例**: `GET /api/problems/search?category=営業許可関連&difficulty=★&limit=20`

**レスポンス例**:
```json
{
  "total_found": 15,
  "returned": 15,
  "problems": [ ... ]
}
```

---

### 11. テーマで問題を取得

**エンドポイント**: `GET /api/problems/by-theme/<theme_name>`

**説明**: 特定のテーマで全パターンの問題を取得

**例**: `GET /api/problems/by-theme/営業許可は無期限有効`

**レスポンス例**:
```json
{
  "theme": "営業許可は無期限有効",
  "total": 12,
  "problems": [
    { "pattern_name": "基本知識", ... },
    { "pattern_name": "ひっかけ", ... },
    ...
  ]
}
```

---

### 12. 問題一覧を取得（ページング）

**エンドポイント**: `GET /api/problems/list`

**説明**: すべての問題をページング形式で取得

**クエリパラメータ**:
- `page` (int, optional): ページ番号（デフォルト: 1）
- `per_page` (int, optional): 1ページあたりの件数（デフォルト: 20, 最大: 100）

**例**: `GET /api/problems/list?page=2&per_page=30`

**レスポンス例**:
```json
{
  "total": 1491,
  "page": 2,
  "per_page": 30,
  "total_pages": 50,
  "count": 30,
  "problems": [ ... ]
}
```

---

## 📊 問題データ構造

### 各問題が含むフィールド

```json
{
  "problem_id": 1,                    // 問題ID (1-1491)
  "theme_id": 1000,                   // テーマID
  "theme_name": "新台設置の手続き",    // テーマ名
  "category": "遊技機管理",            // カテゴリ (6種類)
  "is_subtheme_based": false,         // サブテーマ基付きかどうか
  "problem_type": "true_false",       // 問題タイプ (○×形式)
  "format": "○×",                     // フォーマット
  "source_pdf": 1,                    // ソース PDF番号
  "source_page": 0,                   // ソースページ番号
  "generated_at": "...",              // 生成日時
  "pattern_id": 1,                    // パターンID (1-12)
  "pattern_name": "基本知識",          // パターン名
  "difficulty": "★",                  // 難易度 (★～★★★★)
  "problem_text": "...",              // 問題文（具体的な〇×形式）
  "correct_answer": "○",              // 正解 (○または×)
  "explanation": "...",               // 解説
  "legal_reference": {                // 法律根拠
    "law": "風営法",
    "article": "第6条の2",
    "section": "（遊技機の設置）",
    "detail": "新台設置には..."
  }
}
```

---

## 🎯 使用例

### 例1: ★★難易度の営業許可関連の問題を3問ランダムに取得

```bash
curl "http://localhost:5000/api/problems/random?count=3&difficulty=★★&category=営業許可関連"
```

### 例2: 「営業許可は無期限有効」というテーマの全12パターンを取得

```bash
curl "http://localhost:5000/api/problems/by-theme/営業許可は無期限有効"
```

### 例3: 10問のクイズを取得（★★★難易度、遊技機管理）

```bash
curl -X POST http://localhost:5000/api/problems/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "count": 10,
    "difficulty": "★★★",
    "category": "遊技機管理"
  }'
```

### 例4: 営業許可関連で難易度★の問題を検索（最大20件）

```bash
curl "http://localhost:5000/api/problems/search?category=営業許可関連&difficulty=★&limit=20"
```

---

## ✅ HTTP ステータスコード

| コード | 説明 |
|--------|------|
| 200 | リクエスト成功 |
| 400 | リクエスト不正 |
| 404 | リソースが見つからない |
| 500 | サーバーエラー |

---

## 🔒 エラーレスポンス

エラーが発生した場合、以下の形式でレスポンスされます：

```json
{
  "error": "エラーメッセージ"
}
```

---

## 📦 データソース

- **ファイル**: `CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json`
- **総問題数**: 1,491問
- **テーマ**: 89個（ベース12 + サブ77）
- **パターン**: 12パターン
- **難易度**: 4段階（★～★★★★）
- **カテゴリ**: 6個
- **品質**: すべて風営法条項付き

---

## 🚀 本番環境デプロイ

### Gunicornを使用した本番サーバー起動

```bash
# Gunicornをインストール
pip install gunicorn

# サーバー起動（マルチワーカー）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📝 ライセンス

このAPIは遊技機取扱主任者試験対策システムの一部です。

---

**最終更新**: 2025年10月22日
**ステータス**: ✅ 本番投入準備完了
