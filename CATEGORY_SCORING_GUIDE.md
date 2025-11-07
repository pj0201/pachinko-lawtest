# 項目別採点機能（カテゴリスコアリング）ガイド

## 概要

230問の遊技機取扱主任者試験問題を以下の4つの項目に分類し、項目別の採点・分析を提供します。

## 4つの主要項目

| ID | 項目名 | 問題範囲 | 説明 |
|----|--------|---------|------|
| `system_and_test` | 制度・試験・資格認定 | 問1-30 | 試験制度、資格認定、講習関連の規程 |
| `business_law` | 風営法規制と義務 | 問31-60, 151-180 | 風営法に基づく営業者の義務と規制 |
| `game_machine_standards` | 遊技機規制基準 | 問61-90, 121-150 | 遊技機の技術基準と射幸性基準 |
| `supervisor_duties` | 主任者実務と業界要綱 | 問91-120, 181-230 | 取扱主任者の業務と実務スキル |

## 使用方法

### 1. モジュールのインポート

```javascript
import {
  recordCategoryScore,
  getCategoryScores,
  getOverallScore,
  generateCategoryReport,
  getWeakCategories,
  getProgressData
} from '@/utils/categoryScoring.js';
```

### 2. 試験終了時のスコア記録

問題に解答した後、結果をカテゴリに基づいて記録します。

```javascript
// ユーザーが問題を解答した時
const userId = getCurrentUserId();
const problemId = 15; // 問題番号
const isCorrect = true; // 正解/不正解

recordCategoryScore(userId, problemId, isCorrect);
```

### 3. カテゴリ別成績の取得

```javascript
const userId = getCurrentUserId();
const scores = getCategoryScores(userId);

// 出力例
{
  "system_and_test": {
    "categoryId": "system_and_test",
    "categoryName": "制度・試験・資格認定",
    "totalAttempts": 25,
    "correctAnswers": 20,
    "accuracy": "80.0",
    "lastUpdated": "2025-11-07T12:30:00Z"
  },
  // ... その他のカテゴリ
}
```

### 4. 全体成績の取得

```javascript
const overallScore = getOverallScore(userId);

// 出力例
{
  "totalAttempts": 100,
  "totalCorrect": 82,
  "overallAccuracy": "82.0",
  "categories": [
    {
      "name": "制度・試験・資格認定",
      "accuracy": 80.0,
      "total": 25,
      "correct": 20
    },
    // ... その他のカテゴリ
  ],
  "passedCategories": 3,
  "totalCategories": 4
}
```

### 5. 分析レポートの生成

```javascript
const report = generateCategoryReport(userId);

// 詳細な分析レポートが生成されます
// レポートには以下が含まれます：
// - 全体の成績
// - 各カテゴリの詳細成績
// - 進捗状況
// - 合格/要学習の判定
```

### 6. 弱点カテゴリの特定

正答率80%未満のカテゴリを自動的に特定します。

```javascript
const weakCategories = getWeakCategories(userId, 80);

// 出力例
[
  {
    "categoryName": "遊技機規制基準",
    "accuracy": 75.0,
    "correctAnswers": 15,
    "totalAttempts": 20,
    "recommendedProblems": [61, 62, 63, ...]
  }
]
```

### 7. 進捗データの可視化

グラフ表示用のデータを取得します。

```javascript
const progressData = getProgressData(userId);

// 出力例
{
  "labels": [
    "制度・試験・資格認定",
    "風営法規制と義務",
    "遊技機規制基準",
    "主任者実務と業界要綱"
  ],
  "datasets": {
    "accuracy": [80.0, 85.0, 75.0, 90.0],
    "completion": [83.3, 60.0, 50.0, 40.0]
  }
}
```

## アプリへの統合例

### Vue コンポーネントでの使用

```vue
<template>
  <div class="exam-result">
    <h2>試験結果</h2>

    <!-- 全体成績 -->
    <div class="overall-score">
      <p>総合成績: {{ overallScore.overallAccuracy }}%</p>
      <p>合格: {{ overallScore.passedCategories }}/{{ overallScore.totalCategories }} カテゴリ</p>
    </div>

    <!-- カテゴリ別成績 -->
    <div class="category-scores">
      <div v-for="category in categoryResults" :key="category.id" class="category">
        <h3>{{ category.categoryName }}</h3>
        <p>正答率: {{ category.accuracy }}%</p>
        <p>{{ category.correctAnswers }}/{{ category.totalAttempts }} 問正解</p>
        <div v-if="category.accuracy >= 80" class="passed">✅ 合格</div>
        <div v-else class="needs-study">⚠️ 要学習</div>
      </div>
    </div>

    <!-- 弱点カテゴリ -->
    <div v-if="weakCategories.length > 0" class="weak-categories">
      <h3>学習が必要な項目</h3>
      <ul>
        <li v-for="weak in weakCategories" :key="weak.categoryName">
          {{ weak.categoryName }}: {{ weak.accuracy }}%
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import {
  recordCategoryScore,
  getCategoryScores,
  getOverallScore,
  getWeakCategories
} from '@/utils/categoryScoring.js';

export default {
  data() {
    return {
      categoryResults: [],
      overallScore: {},
      weakCategories: []
    };
  },
  mounted() {
    const userId = this.$store.state.userId;

    // スコアを取得
    const scores = getCategoryScores(userId);
    this.categoryResults = Object.values(scores);

    // 全体成績を取得
    this.overallScore = getOverallScore(userId);

    // 弱点を特定
    this.weakCategories = getWeakCategories(userId);
  }
};
</script>

<style scoped>
.category {
  border: 1px solid #ddd;
  padding: 10px;
  margin: 10px 0;
}

.passed {
  color: green;
  font-weight: bold;
}

.needs-study {
  color: red;
  font-weight: bold;
}
</style>
```

## データストレージ

### LocalStorage キー形式

```
category_scores_{userId}: JSON
```

### 保存されるデータ構造

```json
{
  "system_and_test": {
    "categoryId": "system_and_test",
    "categoryName": "制度・試験・資格認定",
    "totalAttempts": 25,
    "correctAnswers": 20,
    "accuracy": "80.0",
    "lastUpdated": "2025-11-07T12:30:00Z"
  }
}
```

## 機能一覧

| 関数 | 説明 | 戻り値 |
|------|------|--------|
| `getCategoryByProblemId(problemId)` | 問題番号からカテゴリを判定 | Category object |
| `recordCategoryScore(userId, problemId, isCorrect)` | スコアを記録 | void |
| `getCategoryScores(userId)` | すべてのカテゴリスコアを取得 | Object |
| `getOverallScore(userId)` | 全体成績を取得 | Object |
| `generateCategoryReport(userId)` | 詳細レポートを生成 | Object |
| `getCategoryProblems(category)` | カテゴリの問題一覧を取得 | Array |
| `getWeakCategories(userId, threshold)` | 弱点カテゴリを取得 | Array |
| `getProgressData(userId)` | グラフ表示用データを取得 | Object |
| `clearCategoryScores(userId)` | スコア履歴をクリア | void |

## 合格基準

- **各カテゴリ**: 正答率 80% 以上
- **全体**: 230問中184問以上の正解（80%）

## 今後の拡張

1. **難易度別分析**: 各カテゴリ内での難易度別の成績追跡
2. **学習推奨**: 弱点カテゴリの関連問題を自動推奨
3. **進捗通知**: 目標達成度に基づいた学習通知
4. **比較分析**: 他のユーザーとの成績比較（匿名）
5. **エクスポート**: レポートのPDF出力機能
