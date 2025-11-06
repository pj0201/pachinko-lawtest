/**
 * マスターレビュー・修正システム
 * 全モジュールを統合して900問を一括レビュー
 */

const fs = require('fs').promises;
const path = require('path');
const ProblemDuplicateDetector = require('./problem-duplicate-detector.cjs');
const CategoryValidator = require('./category-validator.cjs');

class MasterReviewSystem {
    constructor() {
        this.duplicateDetector = new ProblemDuplicateDetector();
        this.categoryValidator = new CategoryValidator();
    }

    // 法的根拠の分析と補完（簡易版）
    analyzeLegalReference(problem) {
        const refText = problem.legal_reference || problem.explanation || '';
        const hasArticle = /第\d+条/.test(refText);
        const hasParagraph = /第\d+条第\d+項/.test(refText);
        const hasItem = /第\d+条第\d+項第\d+号/.test(refText);

        let score = 0;
        if (hasItem) score = 100;
        else if (hasParagraph) score = 80;
        else if (hasArticle) score = 60;

        return {
            has_reference: score > 0,
            specificity_score: score,
            needs_improvement: score < 60
        };
    }

    // 問題文の具体性スコア計算（簡易版）
    calculateSpecificityScore(problemText) {
        let score = 100;
        const issues = [];

        // 指示語チェック
        const demonstratives = ['これ', 'この', 'それ', 'その', 'あれ', 'あの'];
        let demonCount = 0;
        demonstratives.forEach(dem => {
            const count = (problemText.match(new RegExp(dem, 'g')) || []).length;
            demonCount += count;
        });
        score -= demonCount * 20;
        if (demonCount > 0) {
            issues.push({
                type: 'demonstrative',
                count: demonCount,
                penalty: demonCount * 20
            });
        }

        // 文の長さチェック
        const length = problemText.length;
        if (length < 20) {
            score -= 20;
            issues.push({ type: 'too_short', penalty: 20, length });
        } else if (length > 80) {
            score -= 10;
            issues.push({ type: 'too_long', penalty: 10, length });
        }

        // 曖昧な表現チェック
        const vagueTerms = ['一定期間', '所定の', '適切な', '相当の'];
        let vagueCount = 0;
        vagueTerms.forEach(term => {
            if (problemText.includes(term)) vagueCount++;
        });
        score -= vagueCount * 10;
        if (vagueCount > 0) {
            issues.push({ type: 'vague_terms', count: vagueCount, penalty: vagueCount * 10 });
        }

        score = Math.max(0, Math.min(100, score));

        return {
            score,
            issues,
            evaluation: score >= 80 ? 'excellent' : score >= 60 ? 'good' : 'poor'
        };
    }

    // バックアップ作成
    async createBackup(originalPath) {
        const backupPath = originalPath.replace('.json', '_original_backup.json');
        await fs.copyFile(originalPath, backupPath);
        console.log(`バックアップ作成: ${backupPath}`);
        return backupPath;
    }

    // 統合レビュー実行
    async runMasterReview(inputPath, outputDir) {
        console.log('='.repeat(60));
        console.log('マスターレビューシステム開始');
        console.log('='.repeat(60));

        // データ読み込み
        console.log(`\nデータ読み込み: ${inputPath}`);
        const rawData = await fs.readFile(inputPath, 'utf8');
        const data = JSON.parse(rawData);
        let problems = data.problems || data;

        console.log(`読み込み完了: ${problems.length}問\n`);

        const masterReport = {
            original_count: problems.length,
            phases: []
        };

        // Phase 1: 重複検出・除去
        console.log('='.repeat(60));
        console.log('Phase 1: 重複検出・除去');
        console.log('='.repeat(60));

        const duplicates = await this.duplicateDetector.detectAllDuplicates(problems);
        const dupReport = this.duplicateDetector.generateReport(duplicates, problems);
        await this.duplicateDetector.saveReport(dupReport, outputDir);

        const dupRemoval = this.duplicateDetector.removeDuplicates(problems, duplicates);
        problems = dupRemoval.filtered_problems;

        masterReport.phases.push({
            phase: 1,
            name: '重複検出・除去',
            detected: duplicates.length,
            removed: dupRemoval.removed_count,
            remaining: problems.length
        });

        // Phase 2: カテゴリ適切性チェック
        console.log('\n' + '='.repeat(60));
        console.log('Phase 2: カテゴリ適切性チェック');
        console.log('='.repeat(60));

        const catValidation = this.categoryValidator.validateAllProblems(problems);
        const catFix = this.categoryValidator.autoFixCategoryIssues(problems, catValidation);
        const catReport = this.categoryValidator.generateReport(catValidation, catFix);
        await this.categoryValidator.saveReport(catReport, outputDir);

        const catRemoval = this.categoryValidator.removeFlaggedProblems(problems, catFix);
        problems = catRemoval.filtered_problems;

        masterReport.phases.push({
            phase: 2,
            name: 'カテゴリ適切性チェック',
            invalid: catValidation.invalid,
            fixed: catFix.fixed_problems.length,
            removed: catRemoval.removed_count,
            remaining: problems.length
        });

        // Phase 3: 法的根拠・具体性分析
        console.log('\n' + '='.repeat(60));
        console.log('Phase 3: 法的根拠・具体性分析');
        console.log('='.repeat(60));

        let legalImprovements = 0;
        let specificityImprovements = 0;
        let totalSpecificityBefore = 0;
        let totalSpecificityAfter = 0;

        problems.forEach(problem => {
            // 法的根拠分析
            const legalAnalysis = this.analyzeLegalReference(problem);
            if (legalAnalysis.needs_improvement) {
                legalImprovements++;
            }

            // 具体性分析
            const specBefore = this.calculateSpecificityScore(problem.problem_text);
            totalSpecificityBefore += specBefore.score;

            // 簡易的な改善（指示語の警告）
            if (specBefore.score < 80) {
                specificityImprovements++;
            }

            totalSpecificityAfter += specBefore.score; // 実際の改善は行わないので同じ
        });

        const avgSpecBefore = (totalSpecificityBefore / problems.length).toFixed(1);
        const avgSpecAfter = (totalSpecificityAfter / problems.length).toFixed(1);

        console.log(`\n法的根拠分析:`);
        console.log(`  → 改善必要: ${legalImprovements}問`);
        console.log(`\n具体性分析:`);
        console.log(`  → 改善必要: ${specificityImprovements}問`);
        console.log(`  → 平均スコア: ${avgSpecBefore}点`);

        masterReport.phases.push({
            phase: 3,
            name: '法的根拠・具体性分析',
            legal_needs_improvement: legalImprovements,
            specificity_needs_improvement: specificityImprovements,
            avg_specificity_score: parseFloat(avgSpecBefore)
        });

        // 最終結果出力
        console.log('\n' + '='.repeat(60));
        console.log('最終結果');
        console.log('='.repeat(60));
        console.log(`元の問題数: ${masterReport.original_count}問`);
        console.log(`最終問題数: ${problems.length}問`);
        console.log(`削除合計: ${masterReport.original_count - problems.length}問`);

        // 最終データ保存
        const timestamp = Date.now();
        const finalData = {
            metadata: {
                review_date: new Date().toISOString(),
                original_count: masterReport.original_count,
                final_count: problems.length,
                removed_count: masterReport.original_count - problems.length
            },
            problems: problems
        };

        const outputPath = path.join(outputDir, `opus_${problems.length}_reviewed_${timestamp}.json`);
        await fs.writeFile(outputPath, JSON.stringify(finalData, null, 2));
        console.log(`\n最終データ保存: ${outputPath}`);

        // マスターレポート保存
        masterReport.final_count = problems.length;
        masterReport.removed_total = masterReport.original_count - problems.length;
        masterReport.output_path = outputPath;

        const masterReportPath = path.join(outputDir, `master_review_report_${timestamp}.json`);
        await fs.writeFile(masterReportPath, JSON.stringify(masterReport, null, 2));

        const masterMdPath = path.join(outputDir, `master_review_report_${timestamp}.md`);
        const markdown = this.generateMasterMarkdown(masterReport);
        await fs.writeFile(masterMdPath, markdown);

        console.log(`\nマスターレポート保存: ${masterReportPath}`);
        console.log(`Markdownレポート保存: ${masterMdPath}`);

        console.log('\n' + '='.repeat(60));
        console.log('マスターレビュー完了');
        console.log('='.repeat(60));

        return {
            original_count: masterReport.original_count,
            final_count: masterReport.final_count,
            removed_count: masterReport.removed_total,
            output_path: outputPath,
            report_path: masterReportPath
        };
    }

    generateMasterMarkdown(report) {
        let md = `# マスターレビューレポート\n\n`;
        md += `- 実行日時: ${new Date().toLocaleString('ja-JP')}\n`;
        md += `- 元の問題数: ${report.original_count}問\n`;
        md += `- 最終問題数: ${report.final_count}問\n`;
        md += `- 削除合計: ${report.removed_total}問\n\n`;

        md += `## フェーズ別結果\n\n`;

        report.phases.forEach(phase => {
            md += `### Phase ${phase.phase}: ${phase.name}\n\n`;

            if (phase.phase === 1) {
                md += `- 検出: ${phase.detected}件\n`;
                md += `- 除去: ${phase.removed}問\n`;
                md += `- 残り: ${phase.remaining}問\n\n`;
            } else if (phase.phase === 2) {
                md += `- 不適合: ${phase.invalid}問\n`;
                md += `- 自動修正: ${phase.fixed}問\n`;
                md += `- 除去: ${phase.removed}問\n`;
                md += `- 残り: ${phase.remaining}問\n\n`;
            } else if (phase.phase === 3) {
                md += `- 法的根拠改善必要: ${phase.legal_needs_improvement}問\n`;
                md += `- 具体性改善必要: ${phase.specificity_needs_improvement}問\n`;
                md += `- 平均具体性スコア: ${phase.avg_specificity_score}点\n\n`;
            }
        });

        md += `## 最終出力\n\n`;
        md += `- ファイルパス: ${report.output_path}\n`;

        return md;
    }
}

// CLI実行
if (require.main === module) {
    const inputPath = process.argv[2] || '/home/planj/patshinko-exam-app/data/opus_900_expanded_20251023_114422.json';
    const outputDir = process.argv[3] || '/home/planj/patshinko-exam-app/reports';

    const system = new MasterReviewSystem();

    system.runMasterReview(inputPath, outputDir)
        .then(result => {
            console.log('\n✅ 完了しました');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ エラー発生:', error);
            process.exit(1);
        });
}

module.exports = MasterReviewSystem;
