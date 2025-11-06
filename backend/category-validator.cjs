/**
 * カテゴリ適切性検証システム
 * 風営法関連以外の問題を検出・除外
 */

const fs = require('fs').promises;
const path = require('path');

class CategoryValidator {
    constructor() {
        // 許容される法令（ホワイトリスト）
        this.allowedLaws = {
            '風営法': /風営法|風俗営業等の規制及び業務の適正化等に関する法律|風俗営業法|風適法/,
            '風営法施行令': /風営法施行令|風営法令|風俗営業等の規制及び業務の適正化等に関する法律施行令/,
            '風営法施行規則': /風営法施行規則|風営法規則|風俗営業等の規制及び業務の適正化等に関する法律施行規則/,
            '遊技機規則': /遊技機の認定及び型式の検定等に関する規則|検定規則|認定規則|遊技機規則/,
            '都道府県条例': /都道府県.*条例|風営法.*条例|施行条例/
        };

        // 除外すべき法令（ブラックリスト）
        this.excludedLaws = {
            '民法': { pattern: /^民法$|民法第/, reason: '契約一般は主任者試験の範囲外' },
            '商法': { pattern: /^商法$|商法第/, reason: '商行為一般は主任者試験の範囲外' },
            '会社法': { pattern: /^会社法$|会社法第/, reason: '会社設立・運営は主任者試験の範囲外' },
            '刑法': { pattern: /^刑法$|刑法第/, reason: '刑法は風営法で言及される範囲以外は対象外' },
            '刑事訴訟法': { pattern: /刑事訴訟法|刑訴法/, reason: '刑事手続きは主任者試験の範囲外' },
            '行政手続法': { pattern: /行政手続法/, reason: '一般的な行政手続きは範囲外' },
            '労働基準法': { pattern: /労働基準法|労基法/, reason: '労働法全般は主任者試験の範囲外' }
        };

        // カテゴリと法令の対応
        this.categoryMapping = {
            '営業許可・申請手続き': {
                primary_laws: ['風営法', '風営法施行令', '風営法施行規則'],
                explicitly_excluded: []
            },
            '遊技機管理': {
                primary_laws: ['風営法', '遊技機規則', '風営法施行規則'],
                explicitly_excluded: ['民法', '商法']
            },
            '不正対策': {
                primary_laws: ['風営法', '風営法施行令'],
                explicitly_excluded: []
            },
            '営業時間・規制': {
                primary_laws: ['風営法', '都道府県条例'],
                explicitly_excluded: []
            },
            '型式検定': {
                primary_laws: ['風営法', '遊技機規則'],
                explicitly_excluded: []
            },
            '景品規制': {
                primary_laws: ['風営法', '風営法施行規則', '都道府県条例'],
                explicitly_excluded: []
            },
            '取扱主任者': {
                primary_laws: ['風営法', '風営法施行規則'],
                explicitly_excluded: []
            }
        };
    }

    extractLawReferences(problem) {
        const references = [];
        const text = `${problem.problem_text} ${problem.explanation} ${problem.legal_reference || ''}`;

        // 許容される法令をチェック
        for (const [lawName, pattern] of Object.entries(this.allowedLaws)) {
            if (pattern.test(text)) {
                references.push({
                    law: lawName,
                    type: 'allowed'
                });
            }
        }

        // 除外すべき法令をチェック
        for (const [lawName, config] of Object.entries(this.excludedLaws)) {
            if (config.pattern.test(text)) {
                references.push({
                    law: lawName,
                    type: 'excluded',
                    reason: config.reason
                });
            }
        }

        return references;
    }

    validateCategoryLawAlignment(problem) {
        const category = problem.category;
        const lawRefs = this.extractLawReferences(problem);
        const issues = [];

        const mapping = this.categoryMapping[category];

        if (!mapping) {
            issues.push({
                type: 'unknown_category',
                severity: 'error',
                message: `カテゴリ「${category}」は定義されていません`
            });
            return { valid: false, issues, law_refs: lawRefs };
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
        if (mapping.explicitly_excluded && mapping.explicitly_excluded.length > 0) {
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

        const valid = issues.filter(i => i.severity === 'error').length === 0;

        return { valid, issues, law_refs: lawRefs };
    }

    validateAllProblems(problems) {
        console.log('\nカテゴリ適合性チェック開始...');

        const results = {
            total: problems.length,
            valid: 0,
            invalid: 0,
            warnings: 0,
            details: []
        };

        problems.forEach(problem => {
            const validation = this.validateCategoryLawAlignment(problem);

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

        console.log(`  → 適合: ${results.valid}問`);
        console.log(`  → 不適合: ${results.invalid}問`);
        console.log(`  → 警告: ${results.warnings}件`);

        return results;
    }

    suggestCorrectCategory(problem) {
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

        return null;
    }

    autoFixCategoryIssues(problems, validationResults) {
        console.log('\n自動修正処理中...');

        const fixed = [];
        const toRemove = [];
        const manualReview = [];

        validationResults.details.forEach(detail => {
            const problem = problems.find(p => p.problem_id === detail.problem_id);
            if (!problem) return;

            const issues = detail.validation.issues;

            const hasExcludedLaw = issues.some(i => i.type === 'excluded_law_used');
            const hasCategoryMismatch = issues.some(i => i.type === 'category_law_mismatch');

            if (hasExcludedLaw) {
                toRemove.push({
                    problem_id: problem.problem_id,
                    reason: '主任者試験の範囲外の法令を使用',
                    details: issues.filter(i => i.type === 'excluded_law_used')
                });
            } else if (hasCategoryMismatch) {
                const suggestedCategory = this.suggestCorrectCategory(problem);

                if (suggestedCategory) {
                    fixed.push({
                        problem_id: problem.problem_id,
                        old_category: problem.category,
                        new_category: suggestedCategory,
                        auto_fix: true
                    });
                    problem.category = suggestedCategory;
                } else {
                    manualReview.push({
                        problem_id: problem.problem_id,
                        reason: '適切なカテゴリが自動判定できません',
                        current_category: problem.category,
                        issues: issues
                    });
                }
            } else {
                manualReview.push({
                    problem_id: problem.problem_id,
                    reason: '警告あり - 手動確認推奨',
                    issues: issues
                });
            }
        });

        console.log(`  → 自動修正: ${fixed.length}問`);
        console.log(`  → 削除推奨: ${toRemove.length}問`);
        console.log(`  → 手動レビュー必要: ${manualReview.length}問`);

        return {
            fixed_problems: fixed,
            removed_problems: toRemove,
            manual_review_needed: manualReview
        };
    }

    removeFlaggedProblems(problems, fixResults) {
        const toRemoveIds = new Set(fixResults.removed_problems.map(r => r.problem_id));
        const filtered = problems.filter(p => !toRemoveIds.has(p.problem_id));

        console.log(`カテゴリ検証による除去: ${problems.length}問 → ${filtered.length}問`);

        return {
            filtered_problems: filtered,
            removed_count: toRemoveIds.size,
            removed_ids: Array.from(toRemoveIds)
        };
    }

    generateReport(validationResults, fixResults) {
        return {
            timestamp: new Date().toISOString(),
            summary: {
                total_problems: validationResults.total,
                valid_problems: validationResults.valid,
                invalid_problems: validationResults.invalid,
                warnings: validationResults.warnings,
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
    }

    generateMarkdownReport(report) {
        let md = `# カテゴリ適合性チェックレポート\n\n`;
        md += `- 実行日時: ${new Date(report.timestamp).toLocaleString('ja-JP')}\n\n`;
        md += `## サマリー\n\n`;
        md += `- 総問題数: ${report.summary.total_problems}\n`;
        md += `- 適合: ${report.summary.valid_problems}\n`;
        md += `- 不適合: ${report.summary.invalid_problems}\n`;
        md += `- 自動修正: ${report.summary.auto_fixed}\n`;
        md += `- 削除推奨: ${report.summary.removed}\n`;
        md += `- 手動レビュー必要: ${report.summary.manual_review}\n\n`;

        if (report.details.removed.length > 0) {
            md += `## 削除推奨問題（${report.details.removed.length}件）\n\n`;
            report.details.removed.forEach((item, index) => {
                md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
                md += `- **理由**: ${item.reason}\n`;
                if (item.details) {
                    item.details.forEach(detail => {
                        md += `  - ${detail.law}: ${detail.message}\n`;
                    });
                }
                md += `\n`;
            });
        }

        if (report.details.fixed.length > 0) {
            md += `## 自動修正問題（${report.details.fixed.length}件）\n\n`;
            report.details.fixed.forEach((item, index) => {
                md += `### ${index + 1}. 問題ID: ${item.problem_id}\n`;
                md += `- **旧カテゴリ**: ${item.old_category}\n`;
                md += `- **新カテゴリ**: ${item.new_category}\n\n`;
            });
        }

        return md;
    }

    async saveReport(report, outputDir) {
        await fs.mkdir(outputDir, { recursive: true });

        const timestamp = Date.now();
        const jsonPath = path.join(outputDir, `category_validation_${timestamp}.json`);
        const mdPath = path.join(outputDir, `category_validation_${timestamp}.md`);

        await fs.writeFile(jsonPath, JSON.stringify(report, null, 2));

        const markdown = this.generateMarkdownReport(report);
        await fs.writeFile(mdPath, markdown);

        console.log(`\nレポート保存完了:`);
        console.log(`  - JSON: ${jsonPath}`);
        console.log(`  - Markdown: ${mdPath}`);

        return { jsonPath, mdPath };
    }
}

module.exports = CategoryValidator;
