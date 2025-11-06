# 問題文具体性チェックロジック設計書
作成日: 2025-10-23
目的: 曖昧・抽象的な問題文を具体化

---

## 🎯 目標

- **具体性スコア**: 平均80点以上/100点
- **指示語使用率**: 0%（完全除去）
- **主語・述語明確率**: 100%
- **短文問題の説明充足率**: 100%

---

## 📊 具体性評価の7つの観点

### 1. 指示語の使用（減点対象）
```javascript
const DEMONSTRATIVES = {
    // これ系
    this: ['これ', 'この', 'それ', 'その', 'あれ', 'あの', 'どれ', 'どの'],
    // そこ系
    location: ['ここ', 'そこ', 'あそこ', 'どこ'],
    // penalty: -20点/個
};
```

### 2. 主語の明確性（必須）
```javascript
const SUBJECT_PATTERNS = {
    // 明示的な主語
    explicit: [
        /^遊技機/,
        /^営業者/,
        /^取扱主任者/,
        /^公安委員会/,
        /^型式検定/
    ],
    // 暗黙の主語（減点）
    implicit: [
        /^設置/,    // 誰が設置？
        /^届出/,    // 誰が届出？
        /^必要/     // 何が必要？
    ]
};
```

### 3. 述語の具体性
```javascript
const PREDICATE_PATTERNS = {
    // 具体的な述語
    specific: [
        '届出が必要である',
        '検定を受けなければならない',
        '選任しなければならない',
        '記録を保存する義務がある'
    ],
    // 曖昧な述語（減点）
    vague: [
        '必要である',       // 何が必要？
        'できる',           // 何ができる？
        'してはいけない',   // 何をしてはいけない？
        '行う'              // 何を行う？
    ]
};
```

### 4. 数値の明示性
```javascript
const NUMERIC_SPECIFICITY = {
    // 具体的な数値
    specific: /\d+年|\d+ヶ月|\d+日|\d+円|\d+%/,
    // 曖昧な表現（減点）
    vague: [
        '一定期間',
        '所定の',
        '適切な',
        '相当の'
    ]
};
```

### 5. 対象の明確性
```javascript
const TARGET_SPECIFICITY = {
    // 明確な対象
    specific: [
        '遊技機を営業所に設置する場合',
        '型式検定の有効期限が経過した遊技機',
        '遊技機取扱主任者を選任するとき'
    ],
    // 曖昧な対象（減点）
    vague: [
        '設置する場合',    // 何を設置？
        '変更するとき',    // 何を変更？
        '行う場合'         // 何を行う？
    ]
};
```

### 6. 条件の具体性
```javascript
const CONDITION_SPECIFICITY = {
    // 明確な条件
    specific: [
        '営業開始前に',
        '届出から30日以内に',
        '型式検定の有効期限が経過する前に'
    ],
    // 曖昧な条件（減点）
    vague: [
        'あらかじめ',
        '事前に',
        '速やかに',
        '遅滞なく'
    ]
};
```

### 7. 文の長さ
```javascript
const LENGTH_CRITERIA = {
    too_short: 20,      // 20文字未満 → 説明不足の可能性
    optimal_min: 30,    // 30文字以上
    optimal_max: 60,    // 60文字以下
    too_long: 80        // 80文字超 → 複雑すぎ
};
```

---

## 🔍 具体性スコア計算

```javascript
function calculateSpecificityScore(problemText) {
    let score = 100;
    const issues = [];

    // 1. 指示語チェック（-20点/個）
    let demonstrativeCount = 0;
    [...DEMONSTRATIVES.this, ...DEMONSTRATIVES.location].forEach(dem => {
        const count = (problemText.match(new RegExp(dem, 'g')) || []).length;
        demonstrativeCount += count;
    });
    score -= demonstrativeCount * 20;
    if (demonstrativeCount > 0) {
        issues.push({
            type: 'demonstrative',
            severity: 'error',
            count: demonstrativeCount,
            penalty: demonstrativeCount * 20,
            message: `指示語が${demonstrativeCount}個使用されています`
        });
    }

    // 2. 主語の明確性チェック
    const hasExplicitSubject = SUBJECT_PATTERNS.explicit.some(p => p.test(problemText));
    const hasImplicitSubject = SUBJECT_PATTERNS.implicit.some(p => p.test(problemText));

    if (!hasExplicitSubject && hasImplicitSubject) {
        score -= 15;
        issues.push({
            type: 'implicit_subject',
            severity: 'warning',
            penalty: 15,
            message: '主語が明示されていません'
        });
    }

    // 3. 述語の具体性チェック
    const hasVaguePredicate = PREDICATE_PATTERNS.vague.some(vague => problemText.includes(vague));
    if (hasVaguePredicate) {
        score -= 10;
        issues.push({
            type: 'vague_predicate',
            severity: 'warning',
            penalty: 10,
            message: '述語が曖昧です'
        });
    }

    // 4. 数値の明示性チェック
    const hasNumeric = NUMERIC_SPECIFICITY.specific.test(problemText);
    const hasVagueNumeric = NUMERIC_SPECIFICITY.vague.some(vague => problemText.includes(vague));

    if (hasVagueNumeric && !hasNumeric) {
        score -= 15;
        issues.push({
            type: 'vague_numeric',
            severity: 'warning',
            penalty: 15,
            message: '数値が曖昧です（「一定期間」等）'
        });
    }

    // 5. 文の長さチェック
    const length = problemText.length;

    if (length < LENGTH_CRITERIA.too_short) {
        score -= 20;
        issues.push({
            type: 'too_short',
            severity: 'error',
            penalty: 20,
            actual_length: length,
            message: `文が短すぎます（${length}文字 < 20文字）`
        });
    } else if (length > LENGTH_CRITERIA.too_long) {
        score -= 10;
        issues.push({
            type: 'too_long',
            severity: 'warning',
            penalty: 10,
            actual_length: length,
            message: `文が長すぎます（${length}文字 > 80文字）`
        });
    }

    // 最終スコアは0-100に制限
    score = Math.max(0, Math.min(100, score));

    return {
        score,
        issues,
        evaluation: score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'acceptable' : 'poor'
    };
}
```

---

## 🔧 自動具体化ロジック

### Step 1: 指示語の置換

```javascript
function replaceDemons tratives(problemText, context) {
    let improved = problemText;
    const replacements = [];

    // コンテキストから名詞を抽出
    const nouns = extractNouns(context || problemText);

    // 「これ」「それ」を具体的な名詞に置換
    DEMONSTRATIVES.this.forEach(dem => {
        if (improved.includes(dem)) {
            // 最も関連性の高い名詞を選択
            const replacement = selectBestNoun(nouns, dem, improved);

            if (replacement) {
                improved = improved.replace(new RegExp(dem, 'g'), replacement);
                replacements.push({
                    from: dem,
                    to: replacement
                });
            }
        }
    });

    return {
        improved_text: improved,
        replacements
    };
}

function extractNouns(text) {
    // 形態素解析で名詞を抽出（簡易版）
    const nounPatterns = [
        /遊技機/g,
        /営業許可/g,
        /型式検定/g,
        /取扱主任者/g,
        /公安委員会/g,
        /届出/g,
        /申請/g
    ];

    const nouns = [];
    nounPatterns.forEach(pattern => {
        const matches = text.match(pattern);
        if (matches) {
            nouns.push(...matches);
        }
    });

    return [...new Set(nouns)]; // 重複除去
}

function selectBestNoun(nouns, demonstrative, context) {
    // 指示語の直前・直後の文脈から最適な名詞を選択
    // （簡易版：最初に見つかった名詞を返す）
    return nouns.length > 0 ? nouns[0] : null;
}
```

---

### Step 2: 主語の補完

```javascript
function addExplicitSubject(problemText, category) {
    let improved = problemText;

    // 暗黙の主語を検出
    if (SUBJECT_PATTERNS.implicit.some(p => p.test(problemText))) {
        // カテゴリから主語を推測
        const subject = inferSubject(problemText, category);

        if (subject) {
            // 文頭に主語を追加
            improved = `${subject}は${problemText}`;
        }
    }

    return improved;
}

function inferSubject(problemText, category) {
    // カテゴリとキーワードから主語を推測
    const subjectMap = {
        '営業許可・申請手続き': {
            keywords: ['申請', '届出', '変更'],
            subject: '営業者'
        },
        '遊技機管理': {
            keywords: ['設置', '変更', '廃棄', '保守'],
            subject: '営業者'
        },
        '型式検定': {
            keywords: ['検定', '認定', '申請'],
            subject: '型式検定'
        },
        '取扱主任者': {
            keywords: ['選任', '届出', '講習'],
            subject: '取扱主任者'
        }
    };

    const mapping = subjectMap[category];
    if (mapping) {
        const hasKeyword = mapping.keywords.some(kw => problemText.includes(kw));
        if (hasKeyword) {
            return mapping.subject;
        }
    }

    return null;
}
```

---

### Step 3: 述語の具体化

```javascript
function makePredicateSpecific(problemText) {
    let improved = problemText;
    const modifications = [];

    // 曖昧な述語を具体的に置換
    const replacementRules = [
        {
            vague: '必要である',
            specific: '届出が必要である',
            condition: text => text.includes('届出') || text.includes('申請')
        },
        {
            vague: 'できる',
            specific: '営業することができる',
            condition: text => text.includes('営業')
        },
        {
            vague: 'してはいけない',
            specific: '使用してはいけない',
            condition: text => text.includes('遊技機')
        }
    ];

    replacementRules.forEach(rule => {
        if (improved.includes(rule.vague) && rule.condition(improved)) {
            improved = improved.replace(rule.vague, rule.specific);
            modifications.push({
                from: rule.vague,
                to: rule.specific
            });
        }
    });

    return {
        improved_text: improved,
        modifications
    };
}
```

---

### Step 4: 数値の具体化

```javascript
function specifyNumericValues(problemText, context) {
    let improved = problemText;
    const replacements = [];

    // 曖昧な数値表現を具体化
    const numericMap = {
        '一定期間': {
            context_keywords: ['型式検定', '有効期限'],
            replacement: '3年間'
        },
        '所定の期間': {
            context_keywords: ['届出', '申請'],
            replacement: '30日以内'
        },
        '適切な': {
            context_keywords: ['景品', '上限'],
            replacement: '等価物の範囲内の'
        }
    };

    Object.entries(numericMap).forEach(([vague, spec]) => {
        if (improved.includes(vague)) {
            const hasContext = spec.context_keywords.some(kw => improved.includes(kw) || (context && context.includes(kw)));

            if (hasContext) {
                improved = improved.replace(vague, spec.replacement);
                replacements.push({
                    from: vague,
                    to: spec.replacement
                });
            }
        }
    });

    return {
        improved_text: improved,
        replacements
    };
}
```

---

## 📊 統合処理

```javascript
function improveSpecificity(problem) {
    const original = problem.problem_text;
    let improved = original;
    const allModifications = [];

    // Step 1: 指示語の置換
    const step1 = replaceDemonstratives(improved, problem.category);
    improved = step1.improved_text;
    allModifications.push(...step1.replacements.map(r => ({ step: 1, ...r })));

    // Step 2: 主語の補完
    improved = addExplicitSubject(improved, problem.category);

    // Step 3: 述語の具体化
    const step3 = makePredicateSpecific(improved);
    improved = step3.improved_text;
    allModifications.push(...step3.modifications.map(m => ({ step: 3, ...m })));

    // Step 4: 数値の具体化
    const step4 = specifyNumericValues(improved, problem.explanation);
    improved = step4.improved_text;
    allModifications.push(...step4.replacements.map(r => ({ step: 4, ...r })));

    // スコアの再計算
    const beforeScore = calculateSpecificityScore(original);
    const afterScore = calculateSpecificityScore(improved);

    return {
        original_text: original,
        improved_text: improved,
        before_score: beforeScore.score,
        after_score: afterScore.score,
        improvement: afterScore.score - beforeScore.score,
        modifications: allModifications,
        changed: original !== improved
    };
}
```

---

## 📋 一括処理とレポート

```javascript
function improveAllProblems(problems) {
    const results = {
        total: problems.length,
        improved: 0,
        no_change: 0,
        average_improvement: 0,
        details: []
    };

    let totalImprovement = 0;

    problems.forEach(problem => {
        const result = improveSpecificity(problem);

        if (result.changed) {
            results.improved++;
            totalImprovement += result.improvement;

            // 問題文を更新
            problem.problem_text = result.improved_text;

            results.details.push({
                problem_id: problem.problem_id,
                before_score: result.before_score,
                after_score: result.after_score,
                improvement: result.improvement,
                modifications: result.modifications
            });
        } else {
            results.no_change++;
        }
    });

    results.average_improvement = results.improved > 0 ? (totalImprovement / results.improved).toFixed(1) : 0;

    return results;
}

function generateSpecificityReport(results) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total: results.total,
            improved: results.improved,
            no_change: results.no_change,
            improvement_rate: ((results.improved / results.total) * 100).toFixed(1) + '%',
            average_improvement: results.average_improvement + '点'
        },
        top_improvements: results.details
            .sort((a, b) => b.improvement - a.improvement)
            .slice(0, 20),
        by_modification_type: groupByModificationType(results.details)
    };

    return report;
}

function groupByModificationType(details) {
    const grouped = {
        demonstrative_replacement: 0,
        subject_addition: 0,
        predicate_specification: 0,
        numeric_specification: 0
    };

    details.forEach(detail => {
        detail.modifications.forEach(mod => {
            if (mod.step === 1) grouped.demonstrative_replacement++;
            if (mod.step === 2) grouped.subject_addition++;
            if (mod.step === 3) grouped.predicate_specification++;
            if (mod.step === 4) grouped.numeric_specification++;
        });
    });

    return grouped;
}
```

---

## 🎯 実装手順

### Phase 1: スコア計算ロジック（1時間）
1. 具体性スコア計算関数の実装
2. 7つの観点のチェックロジックの実装
3. 問題検出機能の実装

### Phase 2: 自動具体化ロジック（2時間）
1. 指示語置換ロジックの実装
2. 主語補完ロジックの実装
3. 述語・数値具体化ロジックの実装

### Phase 3: 統合と最適化（30分）
1. 統合処理フローの実装
2. レポート生成機能の実装

---

## 📊 期待される結果

実行例:
```
問題文具体性チェック開始: 900問

具体性スコア計算中...
  → 優秀（80点以上）: 450問
  → 良好（60-79点）: 300問
  → 要改善（60点未満）: 150問

自動具体化処理中...
  → 指示語置換: 85件
  → 主語補完: 62件
  → 述語具体化: 48件
  → 数値具体化: 35件

改善後の平均スコア:
  → 改善前: 68.5点
  → 改善後: 82.3点
  → 平均改善: +13.8点

具体性チェック完了
```

---

## 🔗 次のステップ

1. ✅ 問題文具体性チェックロジック設計完了
2. → 統合レビュー・修正システムの実装（全機能統合）
3. → 900問への一括適用とテスト
