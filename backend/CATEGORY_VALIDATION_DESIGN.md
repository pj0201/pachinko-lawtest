# カテゴリ適切性チェックロジック設計書
作成日: 2025-10-23
目的: 風営法関連以外の問題を除外・修正

---

## 🎯 目標

- **カテゴリ適合率**: 100%（風営法関連のみ）
- **誤検出率**: 0%（適切な問題を除外しない）
- **処理時間**: 900問で1分以内

---

## 📋 許容される法令（ホワイトリスト）

### 風営法関連法令
```javascript
const ALLOWED_LAWS = {
    // 主要法令
    primary: [
        {
            name: '風営法',
            fullName: '風俗営業等の規制及び業務の適正化等に関する法律',
            aliases: ['風俗営業法', '風適法'],
            pattern: /風営法|風俗営業等の規制及び業務の適正化等に関する法律|風俗営業法|風適法/
        },
        {
            name: '風営法施行令',
            fullName: '風俗営業等の規制及び業務の適正化等に関する法律施行令',
            aliases: ['風営法令'],
            pattern: /風営法施行令|風営法令|風俗営業等の規制及び業務の適正化等に関する法律施行令/
        },
        {
            name: '風営法施行規則',
            fullName: '風俗営業等の規制及び業務の適正化等に関する法律施行規則',
            aliases: ['風営法規則'],
            pattern: /風営法施行規則|風営法規則|風俗営業等の規制及び業務の適正化等に関する法律施行規則/
        }
    ],

    // 遊技機関連
    gaming_machine: [
        {
            name: '遊技機規則',
            fullName: '遊技機の認定及び型式の検定等に関する規則',
            aliases: ['検定規則', '認定規則'],
            pattern: /遊技機の認定及び型式の検定等に関する規則|検定規則|認定規則|遊技機規則/
        }
    ],

    // 地方条例
    local_ordinances: [
        {
            name: '都道府県条例',
            fullName: '各都道府県の風営法施行条例',
            aliases: ['風営法条例', '施行条例'],
            pattern: /都道府県.*条例|風営法.*条例|施行条例/
        }
    ]
};
```

---

## ❌ 除外すべき法令（ブラックリスト）

```javascript
const EXCLUDED_LAWS = {
    // 一般法
    general: [
        {
            name: '民法',
            reason: '契約一般は主任者試験の範囲外',
            pattern: /^民法$|民法第/,
            exceptions: [] // 例外なし
        },
        {
            name: '商法',
            reason: '商行為一般は主任者試験の範囲外',
            pattern: /^商法$|商法第/,
            exceptions: []
        },
        {
            name: '会社法',
            reason: '会社設立・運営は主任者試験の範囲外',
            pattern: /^会社法$|会社法第/,
            exceptions: []
        }
    ],

    // 刑事法
    criminal: [
        {
            name: '刑法',
            reason: '刑法は風営法で言及される範囲以外は対象外',
            pattern: /^刑法$|刑法第/,
            exceptions: ['風営法で準用される場合']
        },
        {
            name: '刑事訴訟法',
            reason: '刑事手続きは主任者試験の範囲外',
            pattern: /刑事訴訟法|刑訴法/,
            exceptions: []
        }
    ],

    // 行政法
    administrative: [
        {
            name: '行政手続法',
            reason: '一般的な行政手続きは範囲外（風営法で特定されたものを除く）',
            pattern: /行政手続法/,
            exceptions: ['風営法で明示的に適用される場合']
        }
    ],

    // 労働法
    labor: [
        {
            name: '労働基準法',
            reason: '労働法全般は主任者試験の範囲外',
            pattern: /労働基準法|労基法/,
            exceptions: []
        }
    ]
};
```

---

## 🗂️ カテゴリと法令の対応表

```javascript
const CATEGORY_LAW_MAPPING = {
    '営業許可・申請手続き': {
        primary_laws: ['風営法', '風営法施行令', '風営法施行規則'],
        allowed_topics: [
            '営業許可の申請',
            '営業許可の更新',
            '承継手続き',
            '変更届出',
            '廃止届出'
        ]
    },

    '遊技機管理': {
        primary_laws: ['風営法', '遊技機規則', '風営法施行規則'],
        allowed_topics: [
            '型式検定',
            '遊技機の認定',
            '遊技機の設置',
            '遊技機の変更',
            '遊技機の廃棄',
            '遊技機台帳',
            '保守・点検'
        ],
        // 民法・商法は明示的に除外
        explicitly_excluded: ['民法', '商法']
    },

    '不正対策': {
        primary_laws: ['風営法', '風営法施行令', '刑法（風営法で準用）'],
        allowed_topics: [
            '不正改造の禁止',
            '不正機器の発見',
            '不正防止措置',
            '不正行為の罰則',
            '報告義務'
        ]
    },

    '営業時間・規制': {
        primary_laws: ['風営法', '都道府県条例'],
        allowed_topics: [
            '営業時間',
            '年少者の立入制限',
            '騒音規制',
            '照度規制',
            '広告規制'
        ]
    },

    '型式検定': {
        primary_laws: ['風営法', '遊技機規則'],
        allowed_topics: [
            '型式検定の申請',
            '型式検定の有効期限',
            '型式検定の更新',
            '検定機関',
            '検定基準'
        ]
    },

    '景品規制': {
        primary_laws: ['風営法', '風営法施行規則', '都道府県条例'],
        allowed_topics: [
            '景品の上限',
            '特殊景品',
            '景品交換の記録',
            '景品の表示',
            '三店方式'
        ]
    },

    '取扱主任者': {
        primary_laws: ['風営法', '風営法施行規則'],
        allowed_topics: [
            '選任義務',
            '職務内容',
            '講習受講',
            '証の携帯',
            '変更届出'
        ]
    }
};
```

---

## 🔍 検出ロジック

### Step 1: 法令名の抽出

```javascript
function extractLawReferences(problem) {
    const references = [];

    // 問題文から抽出
    const text = `${problem.problem_text} ${problem.explanation} ${problem.legal_reference || ''}`;

    // 許容される法令をチェック
    ALLOWED_LAWS.primary.forEach(law => {
        if (law.pattern.test(text)) {
            references.push({
                law: law.name,
                type: 'allowed',
                source: 'primary'
            });
        }
    });

    ALLOWED_LAWS.gaming_machine.forEach(law => {
        if (law.pattern.test(text)) {
            references.push({
                law: law.name,
                type: 'allowed',
                source: 'gaming_machine'
            });
        }
    });

    // 除外すべき法令をチェック
    [...EXCLUDED_LAWS.general, ...EXCLUDED_LAWS.criminal, ...EXCLUDED_LAWS.administrative, ...EXCLUDED_LAWS.labor]
        .forEach(law => {
            if (law.pattern.test(text)) {
                references.push({
                    law: law.name,
                    type: 'excluded',
                    reason: law.reason
                });
            }
        });

    return references;
}
```

---

### Step 2: カテゴリ適合性チェック

```javascript
function validateCategoryLawAlignment(problem) {
    const category = problem.category;
    const lawRefs = extractLawReferences(problem);

    const issues = [];

    // カテゴリに対応する法令マッピングを取得
    const mapping = CATEGORY_LAW_MAPPING[category];

    if (!mapping) {
        issues.push({
            type: 'unknown_category',
            severity: 'error',
            message: `カテゴリ「${category}」は定義されていません`
        });
        return { valid: false, issues };
    }

    // 除外すべき法令が含まれているかチェック
    const excludedRefs = lawRefs.filter(ref => ref.type === 'excluded');

    if (excludedRefs.length > 0) {
        excludedRefs.forEach(ref => {
            issues.push({
                type: 'excluded_law_used',
                severity: 'error',
                law: ref.law,
                reason: ref.reason,
                message: `「${ref.law}」は主任者試験の範囲外です: ${ref.reason}`
            });
        });
    }

    // 明示的に除外されている法令がカテゴリで使われていないかチェック
    if (mapping.explicitly_excluded) {
        mapping.explicitly_excluded.forEach(excludedLaw => {
            const found = lawRefs.find(ref => ref.law === excludedLaw);
            if (found) {
                issues.push({
                    type: 'category_law_mismatch',
                    severity: 'error',
                    law: excludedLaw,
                    category: category,
                    message: `「${category}」カテゴリでは「${excludedLaw}」は使用できません`
                });
            }
        });
    }

    // 許容される法令のみが使われているかチェック
    const allowedRefs = lawRefs.filter(ref => ref.type === 'allowed');

    if (allowedRefs.length === 0 && excludedRefs.length > 0) {
        issues.push({
            type: 'no_allowed_law',
            severity: 'warning',
            message: '風営法関連の法令が見つかりません'
        });
    }

    const valid = issues.filter(i => i.severity === 'error').length === 0;

    return { valid, issues, law_refs: lawRefs };
}
```

---

### Step 3: 一括チェック

```javascript
function validateAllProblems(problems) {
    const results = {
        total: problems.length,
        valid: 0,
        invalid: 0,
        warnings: 0,
        details: []
    };

    problems.forEach(problem => {
        const validation = validateCategoryLawAlignment(problem);

        if (validation.valid) {
            results.valid++;
        } else {
            results.invalid++;
        }

        const warningCount = validation.issues.filter(i => i.severity === 'warning').length;
        results.warnings += warningCount;

        if (!validation.valid || warningCount > 0) {
            results.details.push({
                problem_id: problem.problem_id,
                category: problem.category,
                problem_text: problem.problem_text,
                validation: validation
            });
        }
    });

    return results;
}
```

---

## 🔧 自動修正・削除ロジック

```javascript
function autoFixCategoryIssues(problems, validationResults) {
    const fixed = [];
    const toRemove = [];
    const manualReview = [];

    validationResults.details.forEach(detail => {
        const problem = problems.find(p => p.problem_id === detail.problem_id);
        const issues = detail.validation.issues;

        // エラーの種類によって処理を分岐
        const hasExcludedLaw = issues.some(i => i.type === 'excluded_law_used');
        const hasCategoryMismatch = issues.some(i => i.type === 'category_law_mismatch');

        if (hasExcludedLaw) {
            // 除外すべき法令が使われている → 削除候補
            toRemove.push({
                problem_id: problem.problem_id,
                reason: '主任者試験の範囲外の法令を使用',
                details: issues.filter(i => i.type === 'excluded_law_used')
            });
        } else if (hasCategoryMismatch) {
            // カテゴリと法令のミスマッチ → 適切なカテゴリを提案
            const suggestedCategory = suggestCorrectCategory(problem, detail.validation.law_refs);

            if (suggestedCategory) {
                fixed.push({
                    problem_id: problem.problem_id,
                    old_category: problem.category,
                    new_category: suggestedCategory,
                    auto_fix: true
                });

                // 実際に修正
                problem.category = suggestedCategory;
            } else {
                // 適切なカテゴリが見つからない → 手動レビュー
                manualReview.push({
                    problem_id: problem.problem_id,
                    reason: '適切なカテゴリが自動判定できません',
                    current_category: problem.category,
                    issues: issues
                });
            }
        } else {
            // その他の警告 → 手動レビュー
            manualReview.push({
                problem_id: problem.problem_id,
                reason: '警告あり - 手動確認推奨',
                issues: issues
            });
        }
    });

    return {
        fixed_problems: fixed,
        removed_problems: toRemove,
        manual_review_needed: manualReview
    };
}

function suggestCorrectCategory(problem, lawRefs) {
    // 法令から適切なカテゴリを推測
    const allowedLaws = lawRefs.filter(ref => ref.type === 'allowed').map(ref => ref.law);

    // キーワードベースでカテゴリを推測
    const text = problem.problem_text.toLowerCase();

    if (text.includes('型式検定') || text.includes('検定')) {
        return '型式検定';
    } else if (text.includes('遊技機') && text.includes('設置')) {
        return '遊技機管理';
    } else if (text.includes('営業許可') || text.includes('申請')) {
        return '営業許可・申請手続き';
    } else if (text.includes('不正') || text.includes('改造')) {
        return '不正対策';
    } else if (text.includes('景品') || text.includes('交換')) {
        return '景品規制';
    } else if (text.includes('営業時間') || text.includes('年少者')) {
        return '営業時間・規制';
    } else if (text.includes('取扱主任者') || text.includes('主任者')) {
        return '取扱主任者';
    }

    return null; // 推測できない
}
```

---

## 📊 レポート生成

```javascript
function generateCategoryValidationReport(results, fixResults) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total_problems: results.total,
            valid_problems: results.valid,
            invalid_problems: results.invalid,
            warnings: results.warnings,
            auto_fixed: fixResults.fixed_problems.length,
            removed: fixResults.removed_problems.length,
            manual_review: fixResults.manual_review_needed.length
        },
        details: {
            fixed: fixResults.fixed_problems,
            removed: fixResults.removed_problems,
            manual_review: fixResults.manual_review_needed
        }
    };

    return report;
}

async function saveCategoryReport(report, outputPath) {
    const fs = require('fs').promises;

    // JSON保存
    await fs.writeFile(
        `${outputPath}/category_validation_${Date.now()}.json`,
        JSON.stringify(report, null, 2)
    );

    // Markdown保存
    const markdown = generateCategoryMarkdownReport(report);
    await fs.writeFile(
        `${outputPath}/category_validation_${Date.now()}.md`,
        markdown
    );
}

function generateCategoryMarkdownReport(report) {
    let md = `# カテゴリ適合性チェックレポート\n\n`;
    md += `- 実行日時: ${new Date(report.timestamp).toLocaleString('ja-JP')}\n\n`;
    md += `## サマリー\n\n`;
    md += `- 総問題数: ${report.summary.total_problems}\n`;
    md += `- 適合: ${report.summary.valid_problems}\n`;
    md += `- 不適合: ${report.summary.invalid_problems}\n`;
    md += `- 警告: ${report.summary.warnings}\n`;
    md += `- 自動修正: ${report.summary.auto_fixed}\n`;
    md += `- 削除推奨: ${report.summary.removed}\n`;
    md += `- 手動レビュー必要: ${report.summary.manual_review}\n\n`;

    // 削除推奨問題
    if (report.details.removed.length > 0) {
        md += `## 削除推奨問題（${report.details.removed.length}件）\n\n`;
        report.details.removed.forEach((item, index) => {
            md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
            md += `- **理由**: ${item.reason}\n`;
            item.details.forEach(detail => {
                md += `  - ${detail.law}: ${detail.message}\n`;
            });
            md += `\n`;
        });
    }

    // 自動修正問題
    if (report.details.fixed.length > 0) {
        md += `## 自動修正問題（${report.details.fixed.length}件）\n\n`;
        report.details.fixed.forEach((item, index) => {
            md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
            md += `- **旧カテゴリ**: ${item.old_category}\n`;
            md += `- **新カテゴリ**: ${item.new_category}\n\n`;
        });
    }

    // 手動レビュー必要
    if (report.details.manual_review.length > 0) {
        md += `## 手動レビュー必要（${report.details.manual_review.length}件）\n\n`;
        report.details.manual_review.forEach((item, index) => {
            md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
            md += `- **理由**: ${item.reason}\n`;
            md += `- **現在のカテゴリ**: ${item.current_category}\n`;
            md += `- **詳細**:\n`;
            item.issues.forEach(issue => {
                md += `  - [${issue.severity}] ${issue.message}\n`;
            });
            md += `\n`;
        });
    }

    return md;
}
```

---

## 🎯 実装手順

### Phase 1: 定義ファイルの作成（30分）
1. 許容される法令のホワイトリスト作成
2. 除外すべき法令のブラックリスト作成
3. カテゴリと法令の対応表作成

### Phase 2: 検出ロジックの実装（1時間）
1. 法令名抽出関数の実装
2. カテゴリ適合性チェック関数の実装
3. 一括チェック関数の実装

### Phase 3: 修正ロジックの実装（1時間）
1. 自動修正ロジックの実装
2. カテゴリ推測ロジックの実装
3. レポート生成機能の実装

---

## 📊 期待される結果

実行例:
```
カテゴリ適合性チェック開始: 900問

法令抽出中...
  → 許容される法令: 850問
  → 除外すべき法令: 50問

カテゴリ適合性チェック中...
  → 適合: 850問
  → 不適合: 50問
  → 警告: 20問

自動修正処理中...
  → 自動修正: 15問
  → 削除推奨: 35問
  → 手動レビュー必要: 20問

カテゴリ適合性チェック完了
```

---

## 🔗 次のステップ

1. ✅ カテゴリ適切性チェックロジック設計完了
2. → 法的根拠具体化ロジックの設計
3. → 問題文具体性チェックロジックの設計
4. → 統合レビュー・修正システムの実装
