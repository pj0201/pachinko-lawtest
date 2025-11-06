# 重複検出アルゴリズム設計書
作成日: 2025-10-23
目的: 900問から重複・類似問題を完全除去

---

## 🎯 目標

- **重複問題**: 0件（完全除去）
- **検出精度**: 95%以上
- **処理時間**: 900問で5分以内
- **誤検出率**: 5%以下

---

## 📊 重複の定義

### Level 1: 完全重複（100%一致）
同一の問題文・解答

### Level 2: セマンティック重複（85%以上類似）
**例**:
```
問題A: 遊技機購入には正規の契約が必要である。 → ○
問題B: 遊技機購入には正規の契約が不要である。 → ×
```
→ 正誤が逆なだけで実質同じ内容

### Level 3: 部分重複（70-85%類似）
**例**:
```
問題A: 型式検定の有効期限は3年である。
問題B: 型式検定の有効期限は3年間と定められている。
```
→ 表現が異なるだけで同じ内容（要レビュー）

---

## 🔧 検出アルゴリズム（3層構造）

### Layer 1: キーワードベース高速検出
**処理時間**: 900問で10秒

**手順**:
1. 各問題からキーワード抽出（名詞・動詞）
2. キーワードセットの一致度計算（Jaccard係数）
3. 一致度80%以上 → 重複候補

**実装**:
```javascript
function extractKeywords(problemText) {
    // TinySegmenterで形態素解析（日本語）
    const segmenter = new TinySegmenter();
    const tokens = segmenter.segment(problemText);

    // 名詞・動詞のみ抽出
    const keywords = tokens.filter(token =>
        isNoun(token) || isVerb(token)
    );

    return new Set(keywords);
}

function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter(x => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function detectKeywordDuplicates(problems) {
    const duplicates = [];

    for (let i = 0; i < problems.length; i++) {
        const keywordsA = extractKeywords(problems[i].problem_text);

        for (let j = i + 1; j < problems.length; j++) {
            const keywordsB = extractKeywords(problems[j].problem_text);
            const similarity = jaccardSimilarity(keywordsA, keywordsB);

            if (similarity >= 0.80) {
                duplicates.push({
                    problem1: problems[i].problem_id,
                    problem2: problems[j].problem_id,
                    similarity_score: similarity,
                    detection_method: 'keyword'
                });
            }
        }
    }

    return duplicates;
}
```

---

### Layer 2: 編集距離（Levenshtein距離）
**処理時間**: 重複候補のみ処理（1分）

**手順**:
1. Layer 1で検出された候補のみ処理
2. 文字列の編集距離を計算
3. 類似度85%以上 → 高確率重複

**実装**:
```javascript
function levenshteinDistance(str1, str2) {
    const m = str1.length;
    const n = str2.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (str1[i - 1] === str2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = Math.min(
                    dp[i - 1][j] + 1,     // 削除
                    dp[i][j - 1] + 1,     // 挿入
                    dp[i - 1][j - 1] + 1  // 置換
                );
            }
        }
    }

    return dp[m][n];
}

function calculateTextSimilarity(text1, text2) {
    const distance = levenshteinDistance(text1, text2);
    const maxLength = Math.max(text1.length, text2.length);
    return 1 - (distance / maxLength);
}

function detectEditDistanceDuplicates(candidates, problems) {
    const confirmed = [];

    for (const candidate of candidates) {
        const problem1 = problems.find(p => p.problem_id === candidate.problem1);
        const problem2 = problems.find(p => p.problem_id === candidate.problem2);

        const similarity = calculateTextSimilarity(
            problem1.problem_text,
            problem2.problem_text
        );

        if (similarity >= 0.85) {
            confirmed.push({
                ...candidate,
                text_similarity: similarity,
                detection_method: 'edit_distance'
            });
        }
    }

    return confirmed;
}
```

---

### Layer 3: 正誤逆転パターン検出
**処理時間**: 全問題対象（2分）

**手順**:
1. 問題文を正規化（否定語を除去）
2. 正規化後の一致度を確認
3. 正誤が逆 → 重複と判定

**実装**:
```javascript
function normalizeText(text) {
    // 否定語を除去
    const negations = ['不要', 'ない', '禁止', 'できない', '違反', '不適切'];
    let normalized = text;

    negations.forEach(neg => {
        normalized = normalized.replace(neg, '');
    });

    // 句読点・記号を除去
    normalized = normalized.replace(/[、。！？]/g, '');

    return normalized.trim();
}

function detectOppositeAnswerDuplicates(problems) {
    const duplicates = [];

    for (let i = 0; i < problems.length; i++) {
        const normalizedA = normalizeText(problems[i].problem_text);
        const answerA = problems[i].correct_answer;

        for (let j = i + 1; j < problems.length; j++) {
            const normalizedB = normalizeText(problems[j].problem_text);
            const answerB = problems[j].correct_answer;

            // 正規化後のテキスト類似度
            const similarity = calculateTextSimilarity(normalizedA, normalizedB);

            // 高い類似度 + 正誤が逆 → 重複
            if (similarity >= 0.85 && answerA !== answerB) {
                duplicates.push({
                    problem1: problems[i].problem_id,
                    problem2: problems[j].problem_id,
                    similarity_score: similarity,
                    detection_method: 'opposite_answer',
                    answer1: answerA,
                    answer2: answerB
                });
            }
        }
    }

    return duplicates;
}
```

---

## 🚀 統合検出フロー

```javascript
async function detectAllDuplicates(problems) {
    console.log(`重複検出開始: ${problems.length}問`);

    // Layer 1: キーワードベース検出
    console.log('Layer 1: キーワードベース検出中...');
    const keywordCandidates = detectKeywordDuplicates(problems);
    console.log(`  → ${keywordCandidates.length}件の候補検出`);

    // Layer 2: 編集距離確認
    console.log('Layer 2: 編集距離確認中...');
    const editDistanceConfirmed = detectEditDistanceDuplicates(keywordCandidates, problems);
    console.log(`  → ${editDistanceConfirmed.length}件を確定`);

    // Layer 3: 正誤逆転パターン検出
    console.log('Layer 3: 正誤逆転パターン検出中...');
    const oppositeDuplicates = detectOppositeAnswerDuplicates(problems);
    console.log(`  → ${oppositeDuplicates.length}件の正誤逆転重複検出`);

    // 統合
    const allDuplicates = [
        ...editDistanceConfirmed,
        ...oppositeDuplicates
    ];

    // 重複除去（同じペアが複数の方法で検出される場合）
    const uniqueDuplicates = deduplicatePairs(allDuplicates);

    console.log(`\n重複検出完了: ${uniqueDuplicates.length}件の重複を検出`);

    return uniqueDuplicates;
}

function deduplicatePairs(duplicates) {
    const seen = new Set();
    const unique = [];

    for (const dup of duplicates) {
        const key = [dup.problem1, dup.problem2].sort().join('-');

        if (!seen.has(key)) {
            seen.add(key);
            unique.push(dup);
        }
    }

    return unique;
}
```

---

## 📋 重複レポート生成

```javascript
function generateDuplicateReport(duplicates, problems) {
    const report = {
        total_duplicates: duplicates.length,
        by_method: {
            keyword: 0,
            edit_distance: 0,
            opposite_answer: 0
        },
        details: []
    };

    for (const dup of duplicates) {
        report.by_method[dup.detection_method]++;

        const problem1 = problems.find(p => p.problem_id === dup.problem1);
        const problem2 = problems.find(p => p.problem_id === dup.problem2);

        report.details.push({
            pair: [dup.problem1, dup.problem2],
            similarity_score: dup.similarity_score,
            method: dup.detection_method,
            problem1_text: problem1.problem_text,
            problem2_text: problem2.problem_text,
            problem1_answer: problem1.correct_answer,
            problem2_answer: problem2.correct_answer
        });
    }

    return report;
}
```

---

## 🔄 自動除去ロジック

```javascript
function removeDuplicates(problems, duplicates) {
    const toRemove = new Set();

    for (const dup of duplicates) {
        // 以下の優先順位で保持する問題を決定
        const problem1 = problems.find(p => p.problem_id === dup.problem1);
        const problem2 = problems.find(p => p.problem_id === dup.problem2);

        // 優先順位:
        // 1. 法的根拠が具体的（条文番号あり）
        // 2. 問題文が長い（より詳細）
        // 3. 解説が充実している
        // 4. problem_idが小さい（早く生成された方）

        let keepProblem, removeProblem;

        if (hasLegalReference(problem1) && !hasLegalReference(problem2)) {
            keepProblem = problem1;
            removeProblem = problem2;
        } else if (!hasLegalReference(problem1) && hasLegalReference(problem2)) {
            keepProblem = problem2;
            removeProblem = problem1;
        } else if (problem1.problem_text.length > problem2.problem_text.length) {
            keepProblem = problem1;
            removeProblem = problem2;
        } else {
            keepProblem = problem1;
            removeProblem = problem2;
        }

        toRemove.add(removeProblem.problem_id);
    }

    const filtered = problems.filter(p => !toRemove.has(p.problem_id));

    console.log(`重複除去完了: ${problems.length}問 → ${filtered.length}問`);
    console.log(`除去数: ${toRemove.size}問`);

    return {
        filtered_problems: filtered,
        removed_count: toRemove.size,
        removed_ids: Array.from(toRemove)
    };
}

function hasLegalReference(problem) {
    const legalRefPattern = /第\d+条第?\d*項?/;
    return legalRefPattern.test(problem.explanation) ||
           legalRefPattern.test(problem.legal_reference || '');
}
```

---

## 💾 データ保存

```javascript
async function saveDuplicateReport(report, outputPath) {
    const fs = require('fs').promises;

    // JSON形式で保存
    await fs.writeFile(
        `${outputPath}/duplicate_report_${Date.now()}.json`,
        JSON.stringify(report, null, 2)
    );

    // 人間が読みやすいMarkdown形式でも保存
    const markdown = generateMarkdownReport(report);
    await fs.writeFile(
        `${outputPath}/duplicate_report_${Date.now()}.md`,
        markdown
    );
}

function generateMarkdownReport(report) {
    let md = `# 重複検出レポート\n\n`;
    md += `- 検出日時: ${new Date().toLocaleString('ja-JP')}\n`;
    md += `- 検出件数: ${report.total_duplicates}件\n\n`;
    md += `## 検出方法別内訳\n\n`;
    md += `- キーワードベース: ${report.by_method.keyword}件\n`;
    md += `- 編集距離: ${report.by_method.edit_distance}件\n`;
    md += `- 正誤逆転: ${report.by_method.opposite_answer}件\n\n`;
    md += `## 詳細\n\n`;

    for (const detail of report.details) {
        md += `### 重複ペア: ${detail.pair[0]} ⇔ ${detail.pair[1]}\n\n`;
        md += `- **類似度**: ${(detail.similarity_score * 100).toFixed(1)}%\n`;
        md += `- **検出方法**: ${detail.method}\n\n`;
        md += `**問題1**:\n`;
        md += `- テキスト: ${detail.problem1_text}\n`;
        md += `- 正解: ${detail.problem1_answer ? '○' : '×'}\n\n`;
        md += `**問題2**:\n`;
        md += `- テキスト: ${detail.problem2_text}\n`;
        md += `- 正解: ${detail.problem2_answer ? '○' : '×'}\n\n`;
        md += `---\n\n`;
    }

    return md;
}
```

---

## 🎯 実装手順

### Phase 1: 基本実装（1時間）
1. TinySegmenterのインストール（日本語形態素解析）
2. Layer 1: キーワードベース検出の実装
3. Layer 2: 編集距離計算の実装

### Phase 2: 高度な検出（1時間）
1. Layer 3: 正誤逆転パターン検出の実装
2. 統合検出フローの実装
3. レポート生成機能の実装

### Phase 3: テストと調整（30分）
1. 900問への適用
2. 結果の検証
3. 閾値の調整

---

## 📊 期待される結果

実行例:
```
重複検出開始: 900問
Layer 1: キーワードベース検出中...
  → 45件の候補検出
Layer 2: 編集距離確認中...
  → 28件を確定
Layer 3: 正誤逆転パターン検出中...
  → 15件の正誤逆転重複検出

重複検出完了: 35件の重複を検出（重複ペア削除後）

重複除去完了: 900問 → 865問
除去数: 35問
```

---

## 🔗 次のステップ

1. ✅ 重複検出アルゴリズム設計完了
2. → カテゴリ適切性チェックロジックの設計
3. → 法的根拠具体化ロジックの設計
4. → 問題文具体性チェックロジックの設計
5. → 統合レビュー・修正システムの実装
