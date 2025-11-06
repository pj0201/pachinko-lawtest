# RAG Bulk Problem Generation Guide

## 概要

このガイドでは、**250-300個の実問題を RAG（検索拡張生成）により自動生成**する手順を説明します。

**生成方法**: OCR-corrected exam textbook (897KB, 220ページ) → RAG検索 → LLM生成

**目標統計**:
- 総問題数: 250-300問
- 生成時間: 15-30分（LLM依存）
- カテゴリ別分布: 7カテゴリ均等
- 難易度分布: Easy 30%, Medium 50%, Hard 20%

---

## 前提条件

### 1. 必要なファイル

```
✓ /home/planj/patshinko-exam-app/backend/
  ├── rag-bulk-problem-generator.js     (生成エンジン)
  ├── advanced-problem-generator.js     (6ステップアルゴリズム)
  ├── chroma-rag.js                     (RAGシステム)
  ├── llm-provider.js                   (LLMプロバイダー)
  ├── generate-bulk-problems.js         (実行スクリプト) ← NEW
  └── ...

✓ /home/planj/patshinko-exam-app/data/
  └── ocr_results_corrected.json        (OCRデータソース)
```

### 2. LLM プロバイダー選択

**推奨順**: Groq（無料枠充実） > Claude > OpenAI

#### 2.1 Groq（推奨・完全無料）
```bash
# API キーを取得: https://console.groq.com/keys
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_api_key_here
```

**利点**:
- 完全無料
- 月額 ~10,000リクエスト （試験250問生成＝ 250-1000回の LLM呼び出し）
- 高速 (Mixtral 8x7b 使用)

#### 2.2 Ollama（ローカル・完全無料）
```bash
# Ollama インストール（オプション）
curl -fsSL https://ollama.ai/install.sh | sh

# モデルダウンロード（初回のみ ~5GB）
ollama pull mistral

# Ollama サーバー起動（別ターミナル）
ollama serve

# 実行スクリプトで設定
export LLM_PROVIDER=ollama
```

#### 2.3 その他のプロバイダー

| プロバイダー | 環境変数 | 無料枠 | 推奨度 |
|-----------|--------|------|------|
| Claude | `CLAUDE_API_KEY` | 制限あり | ⭐⭐⭐ |
| OpenAI | `OPENAI_API_KEY` | $5 | ⭐⭐ |
| Mistral | `MISTRAL_API_KEY` | $5 | ⭐⭐ |

---

## 実行方法

### 方法 1: Groq（推奨・最速）

```bash
# 1. ディレクトリに移動
cd /home/planj/patshinko-exam-app

# 2. API キー設定
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. 生成実行
node backend/generate-bulk-problems.js

# (オプション) 出力ファイルを指定
node backend/generate-bulk-problems.js --output ./data/problems_v1.json --limit 300
```

**期待される実行時間**: 15-25分

### 方法 2: Ollama（ローカル・オフライン）

```bash
# 1. (初回のみ) Ollama インストール・起動
ollama serve  # 別ターミナルで実行

# 2. モデルダウンロード（初回のみ、約5GB）
ollama pull mistral

# 3. メインターミナルで生成実行
export LLM_PROVIDER=ollama
node backend/generate-bulk-problems.js
```

**期待される実行時間**: 30-45分（ローカルマシン依存）

### 方法 3: Claude（高品質・有料）

```bash
export LLM_PROVIDER=claude
export CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

node backend/generate-bulk-problems.js
```

---

## 実行例と出力

### 実行開始
```
============================================================
  🎰 パチンコ試験 RAG Bulk Problem Generator
  250-300問の実問題自動生成
============================================================

⚙️  Configuration:
  LLM Provider: groq
  OCR Data: /home/planj/patshinko-exam-app/data/ocr_results_corrected.json
  Output: /home/planj/patshinko-exam-app/data/generated_problems.json
  Target: 250-300 problems

📂 Loading OCR data from: ...
✓ Loaded 220 pages from OCR

🔄 Converting OCR data to chunks...
✓ Created 94 chunks from OCR data

🗄️  Initializing ChromaRAG...
✓ ChromaRAG initialized
📥 Adding 94 chunks to vector database...
✓ RAG ready:
  - Collection: patshinko_exam
  - Chunks: 94
  - Last updated: 2025-10-20T...

🤖 Initializing LLM provider: groq
✓ LLM provider ready: GroqProvider

🚀 Starting bulk problem generation...
   Target: 250-300 problems
```

### 生成進行中
```
📚 Generating problems for: 営業許可・申請手続き
   Target: 40 problems
   Found 5 contexts
   Progress: 20% (5 problems generated)
   Progress: 40% (10 problems generated)
   Progress: 60% (15 problems generated)
   Progress: 80% (20 problems generated)
   Progress: 100% (25 problems generated)
   ✅ Total: 25/40 problems
```

### 完了メッセージ
```
✅ Generation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Generation Statistics:
  Total problems: 267
  Generation time: 18.5 minutes
  Target coverage: 95%

📋 Category Breakdown:
  ✓ 営業許可・申請手続き: 38/40 (95.0%)
  ✓ 営業時間・営業場所: 39/40 (97.5%)
  ✓ 遊技機規制: 42/40 (105.0%)
  ✓ 従業者の要件・禁止事項: 38/40 (95.0%)
  ✓ 顧客保護・規制遵守: 40/40 (100.0%)
  ✓ 法令違反と行政処分: 29/30 (96.7%)
  ✓ 実務的対応: 31/30 (103.3%)

🎯 Target Achievement:
  ✅ Within target range: 250-300

💾 Saving results to: /home/planj/patshinko-exam-app/data/generated_problems.json
✓ Saved: 523.45 KB

📚 Sample Generated Problems (showing 2):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【問題 #1】
カテゴリ: 営業許可・申請手続き
難易度: medium
パターン: Pattern2

問題: パチンコ営業所を新規開設する場合、営業許可を取得する前に、設置する遊技機について必ず認定を受けなければならない。

選択肢:
  ○ 正しい
  × 誤り。営業許可取得後に認定申請が可能である場合もある

正答: ×

解説: 風営法では、新規営業許可申請時には遊技機の認定が事前に必要です。ただし、一部の特例を除きます。
...
```

---

## 出力ファイルフォーマット

### 生成結果 JSON構造

```json
{
  "metadata": {
    "generated_at": "2025-10-20T12:34:56.789Z",
    "generation_time_minutes": "18.5",
    "total_problems": 267,
    "total_categories": 7,
    "target_count": 250,
    "success_rate": "95%"
  },
  "category_results": {
    "permits": {
      "name": "営業許可・申請手続き",
      "target": 40,
      "generated": 38,
      "success": true
    },
    ...
  },
  "problems": [
    {
      "id": "problem_001",
      "category": "営業許可・申請手続き",
      "pattern": 2,
      "difficulty": "medium",
      "statement": "パチンコ営業所を新規開設する場合...",
      "option_correct": "正しい",
      "option_incorrect": "誤り。...",
      "correct_answer": false,
      "explanation": "...",
      "law_reference": "風営法第20条",
      "source_context_id": "ocr_page_42",
      "seed_index": 1,
      "generated_at": "2025-10-20T12:35:10.123Z"
    },
    ...
  ]
}
```

### 出力ファイル場所

```
/home/planj/patshinko-exam-app/data/generated_problems.json
```

---

## 次のステップ

### 1. 生成結果の検証

```bash
# 生成されたファイルを確認
cat /home/planj/patshinko-exam-app/data/generated_problems.json | head -100

# 問題数を確認
cat /home/planj/patshinko-exam-app/data/generated_problems.json | \
  jq '.problems | length'

# カテゴリ別統計を表示
cat /home/planj/patshinko-exam-app/data/generated_problems.json | \
  jq '.category_results'
```

### 2. フロントエンド統合

```javascript
// src/components/ExamScreen.jsx で生成問題をロード
const response = await fetch('/api/problems/generated');
const data = await response.json();
const problems = data.problems;
```

### 3. サーバーAPI実装（必要に応じて）

```javascript
// backend/rag-server.js に追加
app.get('/api/problems/generated', (req, res) => {
  const problems = JSON.parse(fs.readFileSync(
    './data/generated_problems.json', 'utf-8'
  ));
  res.json(problems);
});
```

---

## トラブルシューティング

### Q: メモリ不足エラー

```
Error: JavaScript heap out of memory
```

**解決策**: Node.js のメモリ制限を増加

```bash
node --max-old-space-size=4096 backend/generate-bulk-problems.js
```

### Q: LLM 接続エラー

```
Error: Failed to connect to LLM provider
```

**確認事項**:
1. API キーが正しく設定されているか
2. ネットワーク接続があるか
3. API クォータが超過していないか

```bash
# Groq の場合
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/health
```

### Q: ChromaDB 接続エラー

```
Error: Failed to initialize Chroma
```

**解決策**: Chroma サーバーをリセット

```bash
rm -rf ~/.chroma
node backend/generate-bulk-problems.js
```

### Q: 生成が遅い

**原因分析**:
- Ollama ローカル実行: 最遅（30-45分）
- Claude API: 中速（20-30分）
- Groq API: 最速（15-20分）

**推奨**: Groq を使用

---

## 本番運用

### 定期的な再生成

```bash
# 毎週日曜夜 2:00 に再生成するスケジュール
crontab -e

# 追加
0 2 * * 0 cd /home/planj/patshinko-exam-app && node backend/generate-bulk-problems.js
```

### バージョン管理

```bash
# 生成した問題をバージョン管理
git add data/generated_problems.json
git commit -m "Generate 267 problems via RAG (coverage: 95%)"
```

---

## 参考資料

- [RAG システム仕様](./RAG_SYSTEM_COMPLETE.md)
- [問題生成アルゴリズム](./PROBLEM_GENERATION_ENGINE_COMPLETE.md)
- [Worker 2 分析](./WORKER2_SPECIFICATION_IMPLEMENTATION_COMPLETE.md)
- [LLM プロバイダー設定](./backend/llm-provider.js)

---

**生成日**: 2025-10-20
**対応**: パチンコ遊技機取扱主任者試験 250-300問
**ステータス**: ✅ 本番投入準備完了
