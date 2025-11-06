/**
 * 問題重複検出システム
 * 3層検出アルゴリズム：キーワードベース + 編集距離 + 正誤逆転パターン
 */

const TinySegmenter = require('tiny-segmenter');
const stringSimilarity = require('string-similarity');
const fs = require('fs').promises;
const path = require('path');

class ProblemDuplicateDetector {
    constructor() {
        this.segmenter = new TinySegmenter();
    }

    // ===== Layer 1: キーワードベース検出 =====

    extractKeywords(text) {
        const tokens = this.segmenter.segment(text);

        // 名詞・動詞のみ抽出（簡易版）
        const keywords = tokens.filter(token => {
            return token.length >= 2 && // 2文字以上
                   !/^[ぁ-ん]+$/.test(token) && // ひらがなのみは除外
                   !/^[、。！？]$/.test(token); // 句読点除外
        });

        return new Set(keywords);
    }

    jaccardSimilarity(setA, setB) {
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return union.size > 0 ? intersection.size / union.size : 0;
    }

    detectKeywordDuplicates(problems) {
        console.log('Layer 1: キーワードベース検出中...');
        const duplicates = [];
        const total = problems.length;

        for (let i = 0; i < total; i++) {
            if (i % 100 === 0) {
                console.log(`  進捗: ${i}/${total}`);
            }

            const keywordsA = this.extractKeywords(problems[i].problem_text);

            for (let j = i + 1; j < total; j++) {
                const keywordsB = this.extractKeywords(problems[j].problem_text);
                const similarity = this.jaccardSimilarity(keywordsA, keywordsB);

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

        console.log(`  → ${duplicates.length}件の候補検出`);
        return duplicates;
    }

    // ===== Layer 2: 編集距離 =====

    levenshteinDistance(str1, str2) {
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
                        dp[i - 1][j] + 1,
                        dp[i][j - 1] + 1,
                        dp[i - 1][j - 1] + 1
                    );
                }
            }
        }

        return dp[m][n];
    }

    calculateTextSimilarity(text1, text2) {
        const distance = this.levenshteinDistance(text1, text2);
        const maxLength = Math.max(text1.length, text2.length);
        return maxLength > 0 ? 1 - (distance / maxLength) : 0;
    }

    detectEditDistanceDuplicates(candidates, problems) {
        console.log('Layer 2: 編集距離確認中...');
        const confirmed = [];

        const problemMap = new Map();
        problems.forEach(p => problemMap.set(p.problem_id, p));

        for (const candidate of candidates) {
            const problem1 = problemMap.get(candidate.problem1);
            const problem2 = problemMap.get(candidate.problem2);

            if (!problem1 || !problem2) continue;

            const similarity = this.calculateTextSimilarity(
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

        console.log(`  → ${confirmed.length}件を確定`);
        return confirmed;
    }

    // ===== Layer 3: 正誤逆転パターン検出 =====

    normalizeText(text) {
        const negations = ['不要', 'ない', '禁止', 'できない', '違反', '不適切', '誤り', '間違い'];
        let normalized = text;

        negations.forEach(neg => {
            normalized = normalized.replace(new RegExp(neg, 'g'), '');
        });

        normalized = normalized.replace(/[、。！？]/g, '');
        return normalized.trim();
    }

    detectOppositeAnswerDuplicates(problems) {
        console.log('Layer 3: 正誤逆転パターン検出中...');
        const duplicates = [];
        const total = problems.length;

        for (let i = 0; i < total; i++) {
            if (i % 100 === 0) {
                console.log(`  進捗: ${i}/${total}`);
            }

            const normalizedA = this.normalizeText(problems[i].problem_text);
            const answerA = problems[i].correct_answer;

            for (let j = i + 1; j < total; j++) {
                const normalizedB = this.normalizeText(problems[j].problem_text);
                const answerB = problems[j].correct_answer;

                const similarity = this.calculateTextSimilarity(normalizedA, normalizedB);

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

        console.log(`  → ${duplicates.length}件の正誤逆転重複検出`);
        return duplicates;
    }

    // ===== 統合検出 =====

    deduplicatePairs(duplicates) {
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

    async detectAllDuplicates(problems) {
        console.log(`\n重複検出開始: ${problems.length}問\n`);

        const keywordCandidates = this.detectKeywordDuplicates(problems);

        const editDistanceConfirmed = this.detectEditDistanceDuplicates(keywordCandidates, problems);

        const oppositeDuplicates = this.detectOppositeAnswerDuplicates(problems);

        const allDuplicates = [
            ...editDistanceConfirmed,
            ...oppositeDuplicates
        ];

        const uniqueDuplicates = this.deduplicatePairs(allDuplicates);

        console.log(`\n重複検出完了: ${uniqueDuplicates.length}件の重複を検出\n`);

        return uniqueDuplicates;
    }

    // ===== 重複除去 =====

    hasLegalReference(problem) {
        const legalRefPattern = /第\d+条第?\d*項?/;
        return legalRefPattern.test(problem.explanation || '') ||
               legalRefPattern.test(problem.legal_reference || '');
    }

    removeDuplicates(problems, duplicates) {
        console.log('\n重複除去処理中...');
        const toRemove = new Set();
        const problemMap = new Map();
        problems.forEach(p => problemMap.set(p.problem_id, p));

        for (const dup of duplicates) {
            const problem1 = problemMap.get(dup.problem1);
            const problem2 = problemMap.get(dup.problem2);

            if (!problem1 || !problem2) continue;

            let removeProblem;

            // 優先順位で保持する問題を決定
            if (this.hasLegalReference(problem1) && !this.hasLegalReference(problem2)) {
                removeProblem = problem2;
            } else if (!this.hasLegalReference(problem1) && this.hasLegalReference(problem2)) {
                removeProblem = problem1;
            } else if (problem1.problem_text.length > problem2.problem_text.length) {
                removeProblem = problem2;
            } else {
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

    // ===== レポート生成 =====

    generateReport(duplicates, problems) {
        const problemMap = new Map();
        problems.forEach(p => problemMap.set(p.problem_id, p));

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

            const problem1 = problemMap.get(dup.problem1);
            const problem2 = problemMap.get(dup.problem2);

            if (problem1 && problem2) {
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
        }

        return report;
    }

    generateMarkdownReport(report) {
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

    async saveReport(report, outputDir) {
        await fs.mkdir(outputDir, { recursive: true });

        const timestamp = Date.now();
        const jsonPath = path.join(outputDir, `duplicate_report_${timestamp}.json`);
        const mdPath = path.join(outputDir, `duplicate_report_${timestamp}.md`);

        await fs.writeFile(jsonPath, JSON.stringify(report, null, 2));

        const markdown = this.generateMarkdownReport(report);
        await fs.writeFile(mdPath, markdown);

        console.log(`\nレポート保存完了:`);
        console.log(`  - JSON: ${jsonPath}`);
        console.log(`  - Markdown: ${mdPath}`);

        return { jsonPath, mdPath };
    }
}

module.exports = ProblemDuplicateDetector;
