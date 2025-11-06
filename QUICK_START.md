# 🎰 RAG 問題生成 - クイックスタート

## 3ステップで 250-300問を自動生成

### ステップ 1️⃣: LLM API キーを取得

**Groq（推奨・最速・無料）**
```bash
# https://console.groq.com/keys から API キーを取得
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**または Ollama（ローカル・完全無料）**
```bash
# 別ターミナルで Ollama サーバーを起動
ollama serve
```

### ステップ 2️⃣: 生成スクリプトを実行

```bash
cd /home/planj/patshinko-exam-app
./generate-problems.sh groq
```

**または Node.js で直接実行**
```bash
node backend/generate-bulk-problems.js
```

### ステップ 3️⃣: 完了を待つ

```
🚀 Generation Starting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Generating problems for: 営業許可・申請手続き
   Progress: 25% | 50% | 75% | 100% ✅

...（15-25分）...

✅ Generation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Generation Statistics:
  Total problems: 267
  Generation time: 18.5 minutes
  Target coverage: 95%

💾 Saving results to: /home/planj/patshinko-exam-app/data/generated_problems.json
✓ Saved: 523.45 KB
```

---

## 📊 生成結果の確認

```bash
# 生成されたファイルを確認
cat /home/planj/patshinko-exam-app/data/generated_problems.json | jq '.metadata'

# 問題数を表示
cat /home/planj/patshinko-exam-app/data/generated_problems.json | \
  jq '.problems | length'

# カテゴリ別統計
cat /home/planj/patshinko-exam-app/data/generated_problems.json | \
  jq '.category_results'

# 最初の問題を表示
cat /home/planj/patshinko-exam-app/data/generated_problems.json | \
  jq '.problems[0]'
```

---

## 🔧 LLM プロバイダー別ガイド

| プロバイダー | 設定 | 実行時間 | コスト | 推奨度 |
|-----------|------|--------|------|------|
| **Groq** | `export GROQ_API_KEY=...` | 15-20分 | 無料 | ⭐⭐⭐⭐⭐ |
| **Claude** | `export CLAUDE_API_KEY=...` | 20-30分 | ~$1 | ⭐⭐⭐ |
| **OpenAI** | `export OPENAI_API_KEY=...` | 25-35分 | ~$2 | ⭐⭐ |
| **Ollama** | （ローカル） | 30-45分 | 無料 | ⭐⭐⭐⭐ |

---

## 📋 トラブルシューティング

### メモリ不足エラー
```bash
node --max-old-space-size=4096 backend/generate-bulk-problems.js
```

### API キーエラー
```bash
# API キーが正しく設定されているか確認
echo $GROQ_API_KEY
echo $CLAUDE_API_KEY
```

### Chroma DB エラー
```bash
rm -rf ~/.chroma
node backend/generate-bulk-problems.js
```

---

## 📚 詳細ドキュメント

- **完全ガイド**: [RAG_BULK_GENERATION_GUIDE.md](./RAG_BULK_GENERATION_GUIDE.md)
- **実装レポート**: [RAG_GENERATION_SUMMARY.md](./RAG_GENERATION_SUMMARY.md)

---

## 🎯 期待される結果

✅ **250-300問の実問題が生成される**

- 📊 7カテゴリに分類
- 📈 難易度バランス（Easy 30%, Medium 50%, Hard 20%）
- 🎯 6パターンのトラップ問題
- 💾 JSON形式で出力（500-600KB）

---

**準備完了**: 即座に実行可能 ✅
