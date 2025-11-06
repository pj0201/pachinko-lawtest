# Scaled RAG Bulk Generator - 1491問生成実装ガイド

## 📋 概要

`ScaledRAGBulkGenerator` は、元々の RAG Bulk Generator を拡張し、**1491問を安全に生成** するためのクラスです。

**特徴:**
- ✅ Advanced Generator（6段階パイプライン）を活用
- ✅ チェックポイント機構で途中中断に対応
- ✅ レート制限付き遅延でシステム安定性確保
- ✅ 進捗状況をリアルタイムで記録

---

## 🚀 使用方法

### 基本的な使用方法

```javascript
import { ScaledRAGBulkGenerator } from './scaled-rag-bulk-generator-1491.js';
import { ChromaRAG } from './chroma-rag.js';
import { LLMProviderFactory } from './llm-provider.js';

// RAG初期化
const rag = new ChromaRAG();
await rag.initialize();

// ソースデータを追加
const { TextChunker } = await import('./text-chunker.js');
const chunker = new TextChunker();
const chunks = await chunker.chunkMultipleSources({
  ocr: '/home/planj/patshinko-exam-app/data/ocr_results_corrected.json',
  markdown: ['/home/planj/Claude-Code-Communication/resources/legal/wind_eikyo_law/wind_eikyo_law_v1.0.md']
});
await rag.addChunks([...chunks.ocrChunks, ...chunks.mdChunks]);

// LLM プロバイダー初期化
const llmProvider = LLMProviderFactory.create('openai', {
  apiKey: process.env.OPENAI_API_KEY
});

// スケール済みジェネレータ初期化
const generator = new ScaledRAGBulkGenerator(rag, llmProvider, {
  targetTotal: 1491,
  checkpointDir: '/tmp/generation_checkpoint',
  batchSize: 10
});

// 全1491問を生成
const result = await generator.generateAllProblems();

// 結果を保存
await generator.saveResults(
  result,
  '/home/planj/patshinko-exam-app/data/ultimate_problems_scaled_1491.json'
);
```

### カスタム設定

```javascript
const generator = new ScaledRAGBulkGenerator(rag, llmProvider, {
  targetTotal: 1491,              // 総問数（デフォルト: 1491）
  checkpointDir: '/tmp/checkpoint', // チェックポイント保存先
  batchSize: 10                   // バッチサイズ
});
```

---

## 🔄 チェックポイント機構

### 自動保存

生成中、定期的に進捗が自動保存されます：

```
/tmp/generation_checkpoint/
├── permits_checkpoint.json          # 営業許可
├── business_hours_checkpoint.json   # 営業時間
├── gaming_machines_checkpoint.json  # 遊技機規制
├── employees_checkpoint.json        # 従業者要件
├── customer_protection_checkpoint.json
├── violations_checkpoint.json
└── practical_checkpoint.json
```

### 中断・再開

システムが落ちた場合でも、再実行時に：
1. 既存チェックポイントを読み込む
2. 完了したカテゴリはスキップ
3. 未完了のカテゴリから再開

```javascript
// 同じコマンドで再実行するだけで自動再開
const result = await generator.generateAllProblems();
```

### チェックポイント削除（リセット）

```javascript
import fs from 'fs';
import { execSync } from 'child_process';

// 全チェックポイントを削除してリセット
execSync('rm -f /tmp/generation_checkpoint/*.json');
```

---

## 📊 実行結果の構造

### 出力ファイル例

```json
{
  "metadata": {
    "generated_at": "2025-10-22T12:00:00.000Z",
    "generation_time_minutes": "45.2",
    "total_problems": 1491,
    "total_categories": 7,
    "target_count": 1491,
    "success_rate": "100%",
    "stats": {
      "generated": 1491,
      "failed": 0
    }
  },
  "category_results": {
    "permits": {
      "name": "営業許可・申請手続き",
      "target": 213,
      "generated": 213,
      "success": true
    },
    ...
  },
  "problems": [
    {
      "category": "営業許可・申請手続き",
      "statement": "風営法に基づいて...",
      "answer": true,
      "explanation": { ... },
      "pattern": 1,
      "difficulty": "medium",
      "difficulty_score": 0.45,
      "estimated_correct_rate": 0.55,
      "validation": { ... },
      ...
    },
    ...
  ]
}
```

---

## ⏱️ 実行時間の目安

### 3つのアプローチ別

| アプローチ | 実行時間 | システム負荷 | 推奨 |
|----------|--------|-----------|------|
| **案A: 単純拡張** | 26分 | 高 | ❌ |
| **案B: バッチ分割** | 3-4時間 | 中 | ✅ |
| **案C: 並列実行** | 15-20分 | 非常に高い | ⚠️ 高リスク |

### 案A（単純拡張）の実行

```bash
node generate-scaled-1491.js
```

結果: 26分の連続実行

### 案B（バッチ分割）の実行例

```bash
# スクリプト内でバッチ間に遅延を追加
const BATCH_DELAY = 5000; // 5秒
const CATEGORY_DELAY = 10000; // 10秒
```

---

## 🔍 トラブルシューティング

### 1. メモリ不足エラー

**症状**: `FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed`

**対処:**
```javascript
// Node.js のメモリ上限を増やす
// コマンド実行時:
node --max-old-space-size=4096 generate-scaled-1491.js
```

### 2. LLM API エラー

**症状**: `429 Too Many Requests`

**対処:**
```javascript
// レート制限時の遅延を増やす
generator._delay(2000); // デフォルト 800ms → 2000ms
```

### 3. チェックポイント破損

**症状**: チェックポイントが読み込めない

**対処:**
```bash
# 破損したチェックポイントを削除
rm /tmp/generation_checkpoint/[category]_checkpoint.json
# 該当カテゴリのみ再生成
```

---

## 📈 監視・ログ出力

### 生成中の進捗確認

```bash
# ログファイルをリアルタイム監視
tail -f generation_1491.log | grep "進捗\|✅\|❌"
```

### 統計情報の取得

```javascript
// 生成後の統計
console.log('生成数:', result.metadata.stats.generated);
console.log('失敗数:', result.metadata.stats.failed);
console.log('成功率:', result.metadata.success_rate);
console.log('所要時間:', result.metadata.generation_time_minutes, '分');
```

---

## 💾 品質レビュー用データ準備

### サンプル抽出（カテゴリごと10問）

```javascript
function extractReviewSamples(result, samplesPerCategory = 10) {
  const samples = {};

  for (const category of Object.keys(result.category_results)) {
    const categoryProblems = result.problems.filter(p => p.category === category);
    samples[category] = categoryProblems.slice(0, samplesPerCategory);
  }

  return samples;
}

const reviewSamples = extractReviewSamples(result, 10);
fs.writeFileSync(
  '/home/planj/patshinko-exam-app/data/review_samples_1491.json',
  JSON.stringify(reviewSamples, null, 2)
);
```

### LINE への送信準備

```javascript
function prepareLineMessages(reviewSamples) {
  const messages = [];

  for (const [category, problems] of Object.entries(reviewSamples)) {
    const categoryName = problems[0].category || category;
    const message = {
      type: 'REVIEW_REQUEST',
      category: categoryName,
      problem_count: problems.length,
      sample_problems: problems,
      timestamp: new Date().toISOString()
    };
    messages.push(message);
  }

  return messages;
}
```

---

## 🎯 推奨される実行フロー

```
1. チェックポイント削除（新規実行の場合）
   ↓
2. Scaled Generator 初期化
   ↓
3. generateAllProblems() 実行
   ↓
4. 進捗確認（ログ監視）
   ↓
5. 完了後、結果ファイル保存
   ↓
6. レビューサンプル抽出
   ↓
7. LINE へレビューリクエスト送信
   ↓
8. レビュー合格後、全問題を LINE に送信
```

---

## 📝 実装チェックリスト

- [ ] `ScaledRAGBulkGenerator` クラスが正しくインポートされている
- [ ] RAG ソースが正しく読み込まれている
- [ ] LLM プロバイダーが設定されている
- [ ] チェックポイントディレクトリのパーミッションが正しい
- [ ] ディスク空き容量が十分（最低1GB）
- [ ] メモリが十分（最低2GB推奨、4GB推奨）
- [ ] API キーが正しく設定されている

---

## 📞 サポート

問題が発生した場合は、以下のファイルを確認してください：

- `RAG_SCALING_ANALYSIS_20251022.md` - スケーリング技術分析
- チェックポイント JSON ファイル - 進捗状況
- 生成ログ - エラー詳細

