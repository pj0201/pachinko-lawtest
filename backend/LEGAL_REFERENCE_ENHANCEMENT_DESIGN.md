# 法的根拠具体化ロジック設計書
作成日: 2025-10-23
目的: 法的根拠を具体的かつ検証可能にする

---

## 🎯 目標

- **法的根拠明記率**: 100%（条文番号付き）
- **検証可能性**: 100%（実在する条文のみ）
- **フォーマット統一率**: 100%

---

## 📋 法的根拠のフォーマット定義

### 標準フォーマット
```
[法令名]第○条第○項第○号
```

### 許容されるバリエーション
```javascript
const LEGAL_REFERENCE_PATTERNS = {
    // 完全形式
    full: /^(.+?)第(\d+)条第(\d+)項第(\d+)号$/,
    // 例: 風営法第20条第8項第1号

    // 項・号なし
    article_only: /^(.+?)第(\d+)条$/,
    // 例: 風営法第4条

    // 号なし
    article_paragraph: /^(.+?)第(\d+)条第(\d+)項$/,
    // 例: 風営法第20条第8項

    // 施行令・施行規則
    enforcement: /^(.+?)(施行令|施行規則)第(\d+)条/,
    // 例: 風営法施行令第7条

    // 条例
    ordinance: /^(.+?)条例第(\d+)条$/
    // 例: 東京都風営法施行条例第5条
};
```

---

## 🔍 検出ロジック

### Step 1: 現在の法的根拠の抽出と評価

```javascript
function analyzeLegalReference(problem) {
    const analysis = {
        has_reference: false,
        format: null,
        specificity_score: 0,  // 0-100点
        issues: []
    };

    const refText = problem.legal_reference || problem.explanation || '';

    // パターンマッチング
    for (const [formatName, pattern] of Object.entries(LEGAL_REFERENCE_PATTERNS)) {
        const match = refText.match(pattern);
        if (match) {
            analysis.has_reference = true;
            analysis.format = formatName;
            break;
        }
    }

    // 具体性スコア計算
    if (!analysis.has_reference) {
        analysis.specificity_score = 0;
        analysis.issues.push({
            type: 'no_reference',
            severity: 'error',
            message: '法的根拠が記載されていません'
        });
    } else {
        // フォーマットごとのスコア
        const scores = {
            full: 100,              // 第○条第○項第○号
            article_paragraph: 80,  // 第○条第○項
            article_only: 60,       // 第○条
            enforcement: 70,
            ordinance: 70
        };
        analysis.specificity_score = scores[analysis.format] || 50;

        // 曖昧な表現のチェック
        const vaguePatterns = [
            /に規定されて/,
            /に定めて/,
            /を確認/,
            /参照/
        ];

        if (vaguePatterns.some(p => p.test(refText))) {
            analysis.issues.push({
                type: 'vague_reference',
                severity: 'warning',
                message: '曖昧な表現が含まれています'
            });
            analysis.specificity_score -= 10;
        }
    }

    return analysis;
}
```

---

### Step 2: 条文データベースの構築

```javascript
// 風営法条文データベース（簡易版）
const LAW_DATABASE = {
    '風営法': {
        fullName: '風俗営業等の規制及び業務の適正化等に関する法律',
        articles: {
            '4': {
                title: '営業の許可',
                paragraphs: {
                    '1': {
                        items: ['1', '2', '3', '4', '5'],
                        summary: '第1項第5号: 遊技機に関する規定'
                    }
                }
            },
            '20': {
                title: '遊技機の検定等',
                paragraphs: {
                    '8': {
                        summary: '型式検定の有効期限'
                    }
                }
            },
            '22': {
                title: '遊技機の取扱主任者',
                paragraphs: {
                    '1': {
                        summary: '選任義務'
                    }
                }
            }
            // ... その他の条文
        }
    },
    '風営法施行規則': {
        fullName: '風俗営業等の規制及び業務の適正化等に関する法律施行規則',
        articles: {
            '7': {
                title: '遊技機の届出',
                paragraphs: {}
            }
            // ... その他の条文
        }
    },
    '遊技機規則': {
        fullName: '遊技機の認定及び型式の検定等に関する規則',
        articles: {
            '3': {
                title: '型式検定の申請',
                paragraphs: {}
            }
            // ... その他の条文
        }
    }
};

// 条文の存在確認
function verifyLegalReference(lawName, article, paragraph = null, item = null) {
    const law = LAW_DATABASE[lawName];

    if (!law) {
        return {
            exists: false,
            error: '法令が見つかりません'
        };
    }

    const articleData = law.articles[article];
    if (!articleData) {
        return {
            exists: false,
            error: `第${article}条が見つかりません`
        };
    }

    if (paragraph) {
        const paragraphData = articleData.paragraphs[paragraph];
        if (!paragraphData) {
            return {
                exists: false,
                error: `第${article}条第${paragraph}項が見つかりません`
            };
        }

        if (item && paragraphData.items) {
            if (!paragraphData.items.includes(item)) {
                return {
                    exists: false,
                    error: `第${article}条第${paragraph}項第${item}号が見つかりません`
                };
            }
        }
    }

    return {
        exists: true,
        article_title: articleData.title,
        summary: paragraph ? articleData.paragraphs[paragraph].summary : articleData.title
    };
}
```

---

## 🔧 自動補完ロジック

### Step 3: キーワードから条文を推測

```javascript
// テーマ・キーワードから条文を推測
const KEYWORD_TO_ARTICLE_MAP = {
    '型式検定': [
        { law: '風営法', article: '20', paragraph: '8', summary: '型式検定の有効期限' },
        { law: '風営法', article: '20', paragraph: '1', summary: '型式検定の義務' },
        { law: '遊技機規則', article: '3', summary: '型式検定の申請' }
    ],
    '営業許可': [
        { law: '風営法', article: '4', paragraph: '1', summary: '営業許可の申請' },
        { law: '風営法', article: '7', summary: '営業許可の承継' }
    ],
    '取扱主任者': [
        { law: '風営法', article: '22', paragraph: '1', summary: '取扱主任者の選任' },
        { law: '風営法施行規則', article: '30', summary: '取扱主任者の職務' }
    ],
    '遊技機設置': [
        { law: '風営法施行規則', article: '7', summary: '遊技機の届出' }
    ],
    '不正改造': [
        { law: '風営法', article: '20', paragraph: '9', summary: '不正改造の禁止' }
    ],
    '営業時間': [
        { law: '風営法', article: '13', summary: '営業時間の制限' }
    ],
    '年少者': [
        { law: '風営法', article: '22', paragraph: '1', item: '4', summary: '年少者の立入禁止' }
    ],
    '景品': [
        { law: '風営法', article: '23', paragraph: '1', summary: '景品の制限' }
    ]
};

function suggestLegalReferences(problem) {
    const suggestions = [];
    const text = problem.problem_text + ' ' + problem.explanation;

    // キーワードマッチング
    for (const [keyword, articles] of Object.entries(KEYWORD_TO_ARTICLE_MAP)) {
        if (text.includes(keyword)) {
            suggestions.push(...articles);
        }
    }

    // カテゴリベースの推測
    const categoryKeywords = {
        '型式検定': ['型式検定', '検定'],
        '営業許可・申請手続き': ['営業許可', '申請'],
        '遊技機管理': ['遊技機設置', '遊技機'],
        '不正対策': ['不正改造', '不正'],
        '営業時間・規制': ['営業時間', '年少者'],
        '景品規制': ['景品'],
        '取扱主任者': ['取扱主任者', '主任者']
    };

    const categoryKeyword = categoryKeywords[problem.category];
    if (categoryKeyword) {
        categoryKeyword.forEach(kw => {
            if (KEYWORD_TO_ARTICLE_MAP[kw]) {
                suggestions.push(...KEYWORD_TO_ARTICLE_MAP[kw]);
            }
        });
    }

    // 重複除去
    const uniqueSuggestions = [];
    const seen = new Set();

    for (const sugg of suggestions) {
        const key = `${sugg.law}-${sugg.article}-${sugg.paragraph || ''}-${sugg.item || ''}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueSuggestions.push(sugg);
        }
    }

    return uniqueSuggestions;
}
```

---

### Step 4: 自動補完の実行

```javascript
function enhanceLegalReferences(problems) {
    const results = {
        total: problems.length,
        enhanced: 0,
        failed: 0,
        details: []
    };

    problems.forEach(problem => {
        const analysis = analyzeLegalReference(problem);

        if (analysis.specificity_score < 60) {
            // 法的根拠が不十分 → 自動補完を試みる
            const suggestions = suggestLegalReferences(problem);

            if (suggestions.length > 0) {
                // 最も関連性の高い条文を選択（最初のもの）
                const bestMatch = suggestions[0];

                // 法的根拠を構築
                let reference = `${bestMatch.law}第${bestMatch.article}条`;
                if (bestMatch.paragraph) {
                    reference += `第${bestMatch.paragraph}項`;
                }
                if (bestMatch.item) {
                    reference += `第${bestMatch.item}号`;
                }

                // 条文の存在を確認
                const verification = verifyLegalReference(
                    bestMatch.law,
                    bestMatch.article,
                    bestMatch.paragraph,
                    bestMatch.item
                );

                if (verification.exists) {
                    // 解説を更新
                    const oldExplanation = problem.explanation;
                    problem.legal_reference = reference;

                    // 解説に法的根拠を追加（まだ含まれていない場合）
                    if (!oldExplanation.includes(reference)) {
                        problem.explanation = `${oldExplanation}\n\n法的根拠: ${reference}（${verification.summary}）に規定されています。`;
                    }

                    results.enhanced++;
                    results.details.push({
                        problem_id: problem.problem_id,
                        action: 'enhanced',
                        old_reference: problem.legal_reference || '（なし）',
                        new_reference: reference,
                        confidence: suggestions.length === 1 ? 'high' : 'medium'
                    });
                } else {
                    results.failed++;
                    results.details.push({
                        problem_id: problem.problem_id,
                        action: 'failed',
                        reason: verification.error,
                        suggestions: suggestions.map(s => `${s.law}第${s.article}条`)
                    });
                }
            } else {
                results.failed++;
                results.details.push({
                    problem_id: problem.problem_id,
                    action: 'no_suggestion',
                    reason: '適切な条文が見つかりませんでした'
                });
            }
        }
    });

    console.log(`法的根拠補完完了: ${results.enhanced}件を補完、${results.failed}件は手動確認が必要`);

    return results;
}
```

---

## 📊 フォーマット統一

```javascript
function standardizeLegalReferenceFormat(problem) {
    const refText = problem.legal_reference || '';

    // 既存のフォーマットを検出
    for (const [formatName, pattern] of Object.entries(LEGAL_REFERENCE_PATTERNS)) {
        const match = refText.match(pattern);
        if (match) {
            // 標準フォーマットに変換
            let standardized = '';

            if (formatName === 'full') {
                standardized = `${match[1]}第${match[2]}条第${match[3]}項第${match[4]}号`;
            } else if (formatName === 'article_paragraph') {
                standardized = `${match[1]}第${match[2]}条第${match[3]}項`;
            } else if (formatName === 'article_only') {
                standardized = `${match[1]}第${match[2]}条`;
            } else if (formatName === 'enforcement') {
                standardized = `${match[1]}${match[2]}第${match[3]}条`;
            } else if (formatName === 'ordinance') {
                standardized = `${match[1]}条例第${match[2]}条`;
            }

            problem.legal_reference = standardized;
            return {
                changed: refText !== standardized,
                old_format: refText,
                new_format: standardized
            };
        }
    }

    return {
        changed: false,
        old_format: refText,
        new_format: refText
    };
}
```

---

## 📋 レポート生成

```javascript
function generateLegalReferenceReport(enhancementResults, problems) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total: enhancementResults.total,
            enhanced: enhancementResults.enhanced,
            failed: enhancementResults.failed,
            success_rate: (enhancementResults.enhanced / enhancementResults.total * 100).toFixed(1) + '%'
        },
        by_confidence: {
            high: enhancementResults.details.filter(d => d.confidence === 'high').length,
            medium: enhancementResults.details.filter(d => d.confidence === 'medium').length,
            low: enhancementResults.details.filter(d => d.confidence === 'low').length
        },
        needs_manual_review: enhancementResults.details.filter(d => d.action === 'failed' || d.action === 'no_suggestion'),
        enhanced_problems: enhancementResults.details.filter(d => d.action === 'enhanced')
    };

    return report;
}

async function saveLegalReferenceReport(report, outputPath) {
    const fs = require('fs').promises;

    // JSON保存
    await fs.writeFile(
        `${outputPath}/legal_reference_report_${Date.now()}.json`,
        JSON.stringify(report, null, 2)
    );

    // Markdown保存
    const markdown = generateLegalReferenceMarkdown(report);
    await fs.writeFile(
        `${outputPath}/legal_reference_report_${Date.now()}.md`,
        markdown
    );
}

function generateLegalReferenceMarkdown(report) {
    let md = `# 法的根拠補完レポート\n\n`;
    md += `- 実行日時: ${new Date(report.timestamp).toLocaleString('ja-JP')}\n\n`;
    md += `## サマリー\n\n`;
    md += `- 総問題数: ${report.summary.total}\n`;
    md += `- 補完成功: ${report.summary.enhanced}（${report.summary.success_rate}）\n`;
    md += `- 補完失敗: ${report.summary.failed}\n\n`;
    md += `## 信頼度別内訳\n\n`;
    md += `- 高信頼度: ${report.by_confidence.high}件\n`;
    md += `- 中信頼度: ${report.by_confidence.medium}件\n`;
    md += `- 低信頼度: ${report.by_confidence.low}件\n\n`;

    // 手動レビュー必要
    if (report.needs_manual_review.length > 0) {
        md += `## 手動レビュー必要（${report.needs_manual_review.length}件）\n\n`;
        report.needs_manual_review.forEach((item, index) => {
            md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
            md += `- **理由**: ${item.reason}\n`;
            if (item.suggestions) {
                md += `- **候補**: ${item.suggestions.join(', ')}\n`;
            }
            md += `\n`;
        });
    }

    // 補完成功問題
    if (report.enhanced_problems.length > 0) {
        md += `## 補完成功問題（${report.enhanced_problems.length}件）\n\n`;
        report.enhanced_problems.slice(0, 20).forEach((item, index) => {
            md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
            md += `- **旧**: ${item.old_reference}\n`;
            md += `- **新**: ${item.new_reference}\n`;
            md += `- **信頼度**: ${item.confidence}\n\n`;
        });

        if (report.enhanced_problems.length > 20) {
            md += `*（残り${report.enhanced_problems.length - 20}件は省略）*\n\n`;
        }
    }

    return md;
}
```

---

## 🎯 実装手順

### Phase 1: データベース準備（1時間）
1. 風営法条文データベースの構築
2. キーワード→条文マッピングの作成
3. 条文検証ロジックの実装

### Phase 2: 分析・補完ロジック（1時間）
1. 法的根拠の分析関数の実装
2. 条文推測ロジックの実装
3. 自動補完ロジックの実装

### Phase 3: フォーマット統一（30分）
1. フォーマット標準化ロジックの実装
2. レポート生成機能の実装

---

## 📊 期待される結果

実行例:
```
法的根拠補完開始: 900問

分析中...
  → 法的根拠あり（60点以上）: 500問
  → 補完必要（60点未満）: 400問

補完処理中...
  → 高信頼度補完: 280問
  → 中信頼度補完: 80問
  → 補完失敗: 40問

フォーマット統一中...
  → 統一完了: 860問

法的根拠補完完了
  - 補完成功率: 90%
  - 手動レビュー必要: 40問
```

---

## 🔗 次のステップ

1. ✅ 法的根拠具体化ロジック設計完了
2. → 問題文具体性チェックロジックの設計
3. → 統合レビュー・修正システムの実装
