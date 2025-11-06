/**
 * 問題の品質セルフレビューシステム
 *
 * レビュー観点：
 * 1. 日本語の表現の正しさ
 * 2. 何を指すかの具体的記述
 * 3. 抽象的で解釈が分かれる表現
 */

const fs = require('fs');

class SelfReviewSystem {
  constructor() {
    // 問題のある表現パターン
    this.problematicPatterns = {
      // 指示語（何を指すか不明確）
      demonstratives: {
        patterns: ['これ', 'それ', 'あれ', 'この', 'その', 'あの', 'こう', 'そう', 'ああ'],
        severity: 'high',
        message: '指示語が使用されています。具体的な名詞に置き換えてください。'
      },

      // 抽象的な表現
      vague_terms: {
        patterns: [
          '適切な', '所定の', '相当の', '一定の', '適正な',
          '必要な', '十分な', 'ある程度', '若干の', 'やや',
          '概ね', 'ほぼ', '大体', '約', '前後'
        ],
        severity: 'medium',
        message: '抽象的な表現です。具体的な数値や基準に置き換えてください。'
      },

      // 曖昧な主語
      unclear_subject: {
        patterns: [
          /^[^。、]*が[^。、]{0,5}[。、]/,  // 短すぎる主語
          /である。$/,  // 主語不明の断定
          /できる。$/,  // 主語不明の可能表現
        ],
        severity: 'high',
        message: '主語が不明確です。'
      },

      // 二重否定
      double_negative: {
        patterns: [
          /ない.*ない/,
          /なくて.*ない/,
          /なければ.*ない/
        ],
        severity: 'medium',
        message: '二重否定は理解しにくいです。肯定表現に書き換えてください。'
      },

      // 長すぎる文（80字以上）
      too_long: {
        threshold: 80,
        severity: 'low',
        message: '文が長すぎます。2文に分割してください。'
      },

      // 短すぎる文（20字未満）
      too_short: {
        threshold: 20,
        severity: 'medium',
        message: '文が短すぎます。説明が不足している可能性があります。'
      },

      // 修飾語が多すぎる
      too_many_modifiers: {
        patterns: [
          /の.*の.*の.*の/,  // 「の」が4回以上
        ],
        severity: 'medium',
        message: '修飾語が多すぎて理解しにくいです。'
      },

      // カタカナ英語の多用
      excessive_katakana: {
        patterns: [
          /[ァ-ヴ]{6,}/  // 6文字以上の連続カタカナ
        ],
        severity: 'low',
        message: '長いカタカナ語は避け、日本語に置き換えてください。'
      }
    };
  }

  // 複合語の一部でないかチェック
  isPartOfCompoundWord(text, pattern) {
    const compoundWords = [
      'おそれ', 'それぞれ', 'それほど', 'それ以外', 'それ以上', 'それ以下',
      'それなり', 'それでも', 'それから', 'それとも', 'それだけ',
      'これら', 'それら', 'あれら', 'これまで', 'それまで'
    ];
    return compoundWords.some(word => text.includes(word) && word.includes(pattern));
  }

  // 個別問題のレビュー
  reviewProblem(problem) {
    const issues = [];
    const text = problem.problem_text;
    const explanation = problem.explanation || '';

    // 1. 指示語チェック
    this.problematicPatterns.demonstratives.patterns.forEach(pattern => {
      if (text.includes(pattern) && !this.isPartOfCompoundWord(text, pattern)) {
        issues.push({
          type: 'demonstrative',
          severity: 'high',
          pattern: pattern,
          message: `指示語「${pattern}」が使用されています。具体的な名詞に置き換えてください。`,
          location: 'problem_text'
        });
      }
      if (explanation.includes(pattern) && !this.isPartOfCompoundWord(explanation, pattern)) {
        issues.push({
          type: 'demonstrative',
          severity: 'high',
          pattern: pattern,
          message: `解説に指示語「${pattern}」が使用されています。`,
          location: 'explanation'
        });
      }
    });

    // 2. 抽象的表現チェック
    this.problematicPatterns.vague_terms.patterns.forEach(pattern => {
      if (text.includes(pattern)) {
        issues.push({
          type: 'vague_term',
          severity: 'medium',
          pattern: pattern,
          message: `抽象的表現「${pattern}」が使用されています。具体的な数値や基準に置き換えてください。`,
          location: 'problem_text'
        });
      }
    });

    // 3. 文の長さチェック
    if (text.length > this.problematicPatterns.too_long.threshold) {
      issues.push({
        type: 'too_long',
        severity: 'low',
        length: text.length,
        message: `問題文が${text.length}字で長すぎます（推奨: 20-70字）。2文に分割してください。`,
        location: 'problem_text'
      });
    }

    if (text.length < this.problematicPatterns.too_short.threshold) {
      issues.push({
        type: 'too_short',
        severity: 'medium',
        length: text.length,
        message: `問題文が${text.length}字で短すぎます（推奨: 20-70字）。説明が不足している可能性があります。`,
        location: 'problem_text'
      });
    }

    // 4. 二重否定チェック
    this.problematicPatterns.double_negative.patterns.forEach(pattern => {
      if (pattern.test(text)) {
        issues.push({
          type: 'double_negative',
          severity: 'medium',
          message: '二重否定が使用されています。肯定表現に書き換えてください。',
          location: 'problem_text'
        });
      }
    });

    // 5. 修飾語過多チェック
    this.problematicPatterns.too_many_modifiers.patterns.forEach(pattern => {
      if (pattern.test(text)) {
        issues.push({
          type: 'too_many_modifiers',
          severity: 'medium',
          message: '「の」による修飾が多すぎて理解しにくいです。',
          location: 'problem_text'
        });
      }
    });

    // 6. 主語の明確性チェック
    if (!text.includes('は') && !text.includes('が') && text.length > 15) {
      issues.push({
        type: 'unclear_subject',
        severity: 'high',
        message: '主語が明示されていません。「～は」または「～が」で主語を明確にしてください。',
        location: 'problem_text'
      });
    }

    // 7. 法的根拠の明確性チェック
    const legalRef = problem.legal_reference || '';
    if (!legalRef || !/第\d+条/.test(legalRef)) {
      issues.push({
        type: 'no_legal_reference',
        severity: 'medium',
        message: '法的根拠が明記されていません。具体的な条文番号を追加してください。',
        location: 'legal_reference'
      });
    }

    // 8. 数値の具体性チェック
    const hasNumber = /\d+/.test(text);
    const hasVagueQuantity = /多く|少な|何|いくつ|数/.test(text);
    if (hasVagueQuantity && !hasNumber) {
      issues.push({
        type: 'vague_quantity',
        severity: 'medium',
        message: '数量が曖昧です。具体的な数値を記載してください。',
        location: 'problem_text'
      });
    }

    // スコア計算（100点満点）
    let score = 100;
    issues.forEach(issue => {
      if (issue.severity === 'high') score -= 20;
      else if (issue.severity === 'medium') score -= 10;
      else if (issue.severity === 'low') score -= 5;
    });
    score = Math.max(0, score);

    return {
      problem_id: problem.problem_id,
      problem_text: text,
      score: score,
      issues_count: issues.length,
      issues: issues,
      needs_improvement: score < 70
    };
  }

  // 全問題のレビュー
  reviewAll(problems) {
    console.log('='.repeat(60));
    console.log('セルフレビューシステム実行');
    console.log('='.repeat(60));
    console.log(`\n総問題数: ${problems.length}問\n`);

    const results = problems.map(p => this.reviewProblem(p));

    // 統計
    const stats = {
      total: results.length,
      perfect: results.filter(r => r.score === 100).length,
      good: results.filter(r => r.score >= 80 && r.score < 100).length,
      fair: results.filter(r => r.score >= 60 && r.score < 80).length,
      poor: results.filter(r => r.score < 60).length,
      avg_score: (results.reduce((sum, r) => sum + r.score, 0) / results.length).toFixed(1),
      needs_improvement: results.filter(r => r.needs_improvement).length
    };

    // 問題タイプ別集計
    const issueTypes = {};
    results.forEach(r => {
      r.issues.forEach(issue => {
        const key = issue.type;
        if (!issueTypes[key]) {
          issueTypes[key] = {
            count: 0,
            problems: []
          };
        }
        issueTypes[key].count++;
        if (issueTypes[key].problems.length < 5) {
          issueTypes[key].problems.push({
            problem_id: r.problem_id,
            problem_text: r.problem_text.substring(0, 50) + '...',
            message: issue.message
          });
        }
      });
    });

    console.log('■ セルフレビュー結果:');
    console.log(`  - 平均スコア: ${stats.avg_score}点`);
    console.log(`  - 完璧（100点）: ${stats.perfect}問`);
    console.log(`  - 良好（80-99点）: ${stats.good}問`);
    console.log(`  - 要改善（60-79点）: ${stats.fair}問`);
    console.log(`  - 要修正（60点未満）: ${stats.poor}問`);
    console.log('');

    console.log('■ 主な問題点:');
    Object.entries(issueTypes)
      .sort((a, b) => b[1].count - a[1].count)
      .forEach(([type, data]) => {
        console.log(`  - ${type}: ${data.count}件`);
      });
    console.log('');

    return {
      stats: stats,
      issue_types: issueTypes,
      results: results,
      problems_needing_improvement: results.filter(r => r.needs_improvement)
    };
  }

  // レポート生成
  generateReport(reviewResults) {
    let md = `# セルフレビューレポート\n\n`;
    md += `- 実行日時: ${new Date().toLocaleString('ja-JP')}\n`;
    md += `- 総問題数: ${reviewResults.stats.total}問\n`;
    md += `- 平均スコア: ${reviewResults.stats.avg_score}点\n\n`;

    md += `## スコア分布\n\n`;
    md += `- 完璧（100点）: ${reviewResults.stats.perfect}問\n`;
    md += `- 良好（80-99点）: ${reviewResults.stats.good}問\n`;
    md += `- 要改善（60-79点）: ${reviewResults.stats.fair}問\n`;
    md += `- 要修正（60点未満）: ${reviewResults.stats.poor}問\n\n`;

    md += `## 問題タイプ別集計\n\n`;
    Object.entries(reviewResults.issue_types)
      .sort((a, b) => b[1].count - a[1].count)
      .forEach(([type, data]) => {
        md += `### ${type} (${data.count}件)\n\n`;
        md += `**サンプル問題:**\n\n`;
        data.problems.forEach((p, i) => {
          md += `${i + 1}. 問題ID ${p.problem_id}\n`;
          md += `   - 問題文: ${p.problem_text}\n`;
          md += `   - 指摘: ${p.message}\n\n`;
        });
      });

    md += `## 要改善問題一覧（スコア70点未満）\n\n`;
    reviewResults.problems_needing_improvement.slice(0, 50).forEach(p => {
      md += `### 問題ID: ${p.problem_id} (スコア: ${p.score}点)\n\n`;
      md += `**問題文**: ${p.problem_text}\n\n`;
      md += `**指摘事項:**\n\n`;
      p.issues.forEach(issue => {
        md += `- [${issue.severity.toUpperCase()}] ${issue.message}\n`;
      });
      md += `\n`;
    });

    return md;
  }
}

// 実行
if (require.main === module) {
  const inputPath = process.argv[2] || './data/opus_634_final_20251023.json';
  const outputDir = process.argv[3] || './reports';

  const data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const problems = data.problems;

  const reviewer = new SelfReviewSystem();
  const results = reviewer.reviewAll(problems);

  // レポート保存
  const timestamp = Date.now();
  const jsonPath = `${outputDir}/self_review_results_${timestamp}.json`;
  const mdPath = `${outputDir}/self_review_report_${timestamp}.md`;

  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2));
  console.log(`✅ レビュー結果保存: ${jsonPath}`);

  const markdown = reviewer.generateReport(results);
  fs.writeFileSync(mdPath, markdown);
  console.log(`✅ レポート保存: ${mdPath}`);

  console.log('\n' + '='.repeat(60));
  console.log('セルフレビュー完了');
  console.log('='.repeat(60));
}

module.exports = SelfReviewSystem;
