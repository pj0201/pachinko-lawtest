/**
 * Problem Quality Checker
 *
 * 1200問の品質をチェック
 * 基準: 運転免許試験の生成ロジック + RAG ソース品質
 */

class ProblemQualityChecker {
  constructor() {
    // 文法エラーパターン
    this.grammarErrors = [
      /(.+)\1{1,}/, // 単語重複: "営業許可営業許可"
      /のについて/, // 文法エラー: "のについて"
      /のは～/, // プレースホルダー残存
      /～/, // その他プレースホルダー
      /\s{2,}/, // 複数の空白
    ];

    // 質問文の最小・最大文字数
    this.statementLengthRange = [20, 200];

    // 有効な難易度
    this.validDifficulties = ['easy', 'medium', 'hard'];

    // 有効なカテゴリ
    this.validCategories = [
      '営業許可・申請手続き',
      '建物・設備基準',
      '従業員・管理者要件',
      '営業時間・休業',
      '景品・景慮基準',
      '法律・規制違反',
      '実務・業務管理'
    ];
  }

  /**
   * 単一の問題をチェック
   */
  checkProblem(problem, index) {
    const issues = [];
    const warnings = [];
    let score = 100;

    // 1. 必須フィールドチェック
    if (!problem.id) {
      issues.push(`[${index}] Missing 'id'`);
      score -= 10;
    }
    if (!problem.statement) {
      issues.push(`[${index}] Missing 'statement'`);
      score -= 10;
    }
    if (problem.answer === undefined && problem.answer !== false) {
      issues.push(`[${index}] Missing or invalid 'answer'`);
      score -= 10;
    }
    if (!problem.difficulty) {
      issues.push(`[${index}] Missing 'difficulty'`);
      score -= 10;
    }
    if (!problem.category) {
      issues.push(`[${index}] Missing 'category'`);
      score -= 10;
    }

    // 2. 文法エラーチェック
    if (problem.statement) {
      for (const pattern of this.grammarErrors) {
        if (pattern.test(problem.statement)) {
          issues.push(`[${index}] Grammar error: "${pattern}" detected in statement`);
          score -= 15;
          break;
        }
      }
    }

    // 3. 文の長さチェック
    if (problem.statement) {
      const length = problem.statement.length;
      if (length < this.statementLengthRange[0]) {
        warnings.push(`[${index}] Statement too short (${length} chars)`);
        score -= 5;
      }
      if (length > this.statementLengthRange[1]) {
        warnings.push(`[${index}] Statement too long (${length} chars)`);
        score -= 5;
      }
    }

    // 4. 難易度チェック
    if (problem.difficulty && !this.validDifficulties.includes(problem.difficulty)) {
      issues.push(`[${index}] Invalid difficulty: "${problem.difficulty}"`);
      score -= 10;
    }

    // 5. カテゴリチェック
    if (problem.category && !this.validCategories.includes(problem.category)) {
      warnings.push(`[${index}] Unknown category: "${problem.category}"`);
      score -= 5;
    }

    // 6. 解説の存在チェック
    if (!problem.explanation) {
      warnings.push(`[${index}] Missing explanation`);
      score -= 5;
    } else if (problem.explanation.length < 10) {
      warnings.push(`[${index}] Explanation too short (${problem.explanation.length} chars)`);
      score -= 5;
    }

    // 7. 出典チェック
    if (!problem.source) {
      warnings.push(`[${index}] Missing 'source'`);
      score -= 3;
    }

    return {
      index,
      id: problem.id,
      score: Math.max(0, score),
      issues,
      warnings,
      problemData: problem
    };
  }

  /**
   * 全問題をチェック
   */
  checkAllProblems(problems) {
    console.log(`\n🔍 チェック開始: ${problems.length}問`);
    console.log('=' .repeat(70));

    const results = problems.map((p, idx) => this.checkProblem(p, idx));

    // 統計情報
    const criticalIssues = results.filter(r => r.issues.length > 0);
    const hasWarnings = results.filter(r => r.warnings.length > 0);
    const avgScore = (results.reduce((sum, r) => sum + r.score, 0) / results.length).toFixed(2);
    const criticalRate = ((criticalIssues.length / results.length) * 100).toFixed(1);

    return {
      totalProblems: problems.length,
      averageScore: parseFloat(avgScore),
      criticalIssueCount: criticalIssues.length,
      criticalIssueRate: parseFloat(criticalRate),
      warningCount: hasWarnings.length,
      problemResults: results,
      summary: {
        criticalProblems: criticalIssues,
        warningProblems: hasWarnings.filter(r => r.warnings.length > 0 && r.issues.length === 0),
        healthyProblems: results.filter(r => r.score === 100)
      }
    };
  }

  /**
   * エラーの分類と集計
   */
  analyzeErrors(checkResult) {
    const errorTypes = {};
    const errorByCategory = {};

    for (const result of checkResult.problemResults) {
      // エラーの種類を分類
      for (const issue of result.issues) {
        const errorType = issue.match(/\[.+?\]\s(.+?):/)?.[1] || 'Unknown';
        errorTypes[errorType] = (errorTypes[errorType] || 0) + 1;
      }

      // カテゴリ別エラー
      const category = result.problemData.category || 'Unknown';
      if (!errorByCategory[category]) {
        errorByCategory[category] = { total: 0, critical: 0 };
      }
      errorByCategory[category].total++;
      if (result.issues.length > 0) {
        errorByCategory[category].critical++;
      }
    }

    return {
      errorTypeDistribution: errorTypes,
      errorByCategory,
      summary: {
        grammarErrors: (errorTypes['Grammar error'] || 0),
        missingFields: (errorTypes['Missing'] || 0),
        invalidValues: (errorTypes['Invalid'] || 0),
      }
    };
  }

  /**
   * レポートを生成
   */
  generateReport(checkResult) {
    const analysis = this.analyzeErrors(checkResult);

    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalProblems: checkResult.totalProblems,
        averageQualityScore: checkResult.averageScore,
        criticalIssueRate: checkResult.criticalIssueRate + '%',
        healthyProblemsCount: checkResult.summary.healthyProblems.length,
        healthyProblemsRate: ((checkResult.summary.healthyProblems.length / checkResult.totalProblems) * 100).toFixed(1) + '%'
      },
      errorAnalysis: analysis.summary,
      errorDistribution: analysis.errorTypeDistribution,
      categoryAnalysis: analysis.errorByCategory,
      criticalProblems: checkResult.summary.criticalProblems.slice(0, 10).map(p => ({
        id: p.id,
        issues: p.issues,
        statement: p.problemData.statement
      })),
      recommendations: this.generateRecommendations(checkResult, analysis)
    };

    return report;
  }

  /**
   * 改善提案を生成
   */
  generateRecommendations(checkResult, analysis) {
    const recommendations = [];

    if (analysis.summary.grammarErrors > 0) {
      recommendations.push({
        priority: 'CRITICAL',
        category: '文法エラー',
        count: analysis.summary.grammarErrors,
        action: 'LLM で自動修正または手動レビュー',
        example: '「のについて」「営業許可営業許可」などのパターンマッチング'
      });
    }

    if (analysis.summary.missingFields > 0) {
      recommendations.push({
        priority: 'CRITICAL',
        category: '必須フィールド不足',
        count: analysis.summary.missingFields,
        action: 'データソースを確認、生成ロジックを修正'
      });
    }

    if (checkResult.criticalIssueRate > 20) {
      recommendations.push({
        priority: 'HIGH',
        category: '全体品質',
        rate: checkResult.criticalIssueRate + '%',
        action: 'RAG ジェネレーター、生成プロンプトの見直し'
      });
    }

    return recommendations;
  }
}

export { ProblemQualityChecker };
