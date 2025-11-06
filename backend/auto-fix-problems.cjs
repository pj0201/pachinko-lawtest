/**
 * 問題の自動修正システム
 * セルフレビュー結果に基づいて自動修正を試みる
 */

const fs = require('fs');

class AutoFixSystem {
  constructor() {
    // 抽象的表現の具体化マップ
    this.abstractToConcreteMap = {
      '一定の間隔': '適切な間隔（都道府県条例で定める基準）',
      '適切な': '風営法で定める',
      '所定の': '風営法施行規則で定める',
      '適正な': '国家公安委員会規則で定める',
      '相当の': '合理的な',
      '必要な': '法令で定める'
    };
  }

  // 解説から指示語を削除
  removeDemonstrativesFromExplanation(explanation) {
    if (!explanation) return explanation;

    // 「これは」「それは」「あれは」→「この規定は」「その条項は」など
    let fixed = explanation;

    // 「これは」→削除または「この規定は」
    fixed = fixed.replace(/これは/g, '');
    fixed = fixed.replace(/それは/g, '');
    fixed = fixed.replace(/あれは/g, '');

    // 「これ」単独→削除
    fixed = fixed.replace(/これ/g, '本規定');
    fixed = fixed.replace(/それ/g, '当該事項');
    fixed = fixed.replace(/あれ/g, '上記事項');

    // 「その」「この」「あの」
    fixed = fixed.replace(/その/g, '当該');
    fixed = fixed.replace(/この/g, '本');

    return fixed;
  }

  // 主語を追加
  addSubject(problemText) {
    // 主語がない場合の候補
    const subjectCandidates = {
      '営業': 'パチンコ営業は',
      '許可': '営業許可は',
      '遊技機': '遊技機は',
      '申請': '許可申請は',
      '届出': '変更届出は',
      '検定': '型式検定は',
      '景品': '景品提供は',
      '主任者': '取扱主任者は',
      '設置': '遊技機の設置は',
      '変更': '構造設備の変更は'
    };

    // 主語がない場合（「は」「が」がない）
    if (!problemText.includes('は') && !problemText.includes('が')) {
      // キーワードから主語を推測
      for (const [keyword, subject] of Object.entries(subjectCandidates)) {
        if (problemText.includes(keyword)) {
          return subject + problemText;
        }
      }
    }

    return problemText;
  }

  // 短い文を拡張
  expandShortText(problem) {
    const text = problem.problem_text;
    if (text.length >= 20) return text;

    // カテゴリに基づいて追加情報を補足
    let expanded = text;

    // 「必要」で終わる場合
    if (text.endsWith('必要。')) {
      expanded = text.replace('必要。', '必要である。');
    }

    // カテゴリ情報を活用
    const category = problem.category || '';
    if (category.includes('営業許可')) {
      if (text.includes('申請')) {
        expanded = text.replace('。', '必要である。');
      }
    }

    return expanded;
  }

  // 二重否定を肯定表現に
  fixDoubleNegative(text) {
    // 「～でなければならない」は二重否定ではなく義務表現なので保持
    // 「～ないことはない」→「～がある」
    let fixed = text;
    fixed = fixed.replace(/ないことはない/g, 'がある');
    fixed = fixed.replace(/なくはない/g, 'がある');

    return fixed;
  }

  // 個別問題の修正
  fixProblem(problem, reviewResult) {
    if (!reviewResult || reviewResult.score >= 80) {
      return { problem, fixed: false, changes: [] };
    }

    const changes = [];
    let fixedProblem = { ...problem };

    // 1. 解説の指示語削除
    const hasDemo = reviewResult.issues.some(i => i.type === 'demonstrative' && i.location === 'explanation');
    if (hasDemo) {
      const originalExplanation = fixedProblem.explanation;
      fixedProblem.explanation = this.removeDemonstrativesFromExplanation(originalExplanation);
      if (fixedProblem.explanation !== originalExplanation) {
        changes.push({
          type: 'demonstrative_removed',
          field: 'explanation',
          before: originalExplanation,
          after: fixedProblem.explanation
        });
      }
    }

    // 2. 主語の追加
    const unclearSubject = reviewResult.issues.some(i => i.type === 'unclear_subject');
    if (unclearSubject) {
      const originalText = fixedProblem.problem_text;
      fixedProblem.problem_text = this.addSubject(originalText);
      if (fixedProblem.problem_text !== originalText) {
        changes.push({
          type: 'subject_added',
          field: 'problem_text',
          before: originalText,
          after: fixedProblem.problem_text
        });
      }
    }

    // 3. 二重否定の修正
    const hasDoubleNeg = reviewResult.issues.some(i => i.type === 'double_negative');
    if (hasDoubleNeg) {
      const originalText = fixedProblem.problem_text;
      fixedProblem.problem_text = this.fixDoubleNegative(originalText);
      if (fixedProblem.problem_text !== originalText) {
        changes.push({
          type: 'double_negative_fixed',
          field: 'problem_text',
          before: originalText,
          after: fixedProblem.problem_text
        });
      }
    }

    // 4. 短い文の拡張（慎重に）
    const tooShort = reviewResult.issues.some(i => i.type === 'too_short');
    if (tooShort && fixedProblem.problem_text.length < 20) {
      const originalText = fixedProblem.problem_text;
      fixedProblem.problem_text = this.expandShortText(fixedProblem);
      if (fixedProblem.problem_text !== originalText) {
        changes.push({
          type: 'text_expanded',
          field: 'problem_text',
          before: originalText,
          after: fixedProblem.problem_text
        });
      }
    }

    return {
      problem: fixedProblem,
      fixed: changes.length > 0,
      changes: changes,
      original_score: reviewResult.score,
      remaining_issues: reviewResult.issues.filter(i =>
        i.type !== 'demonstrative' ||
        (i.type === 'demonstrative' && i.location === 'problem_text')
      )
    };
  }

  // 全問題の修正
  fixAll(problems, reviewResults) {
    console.log('='.repeat(60));
    console.log('自動修正システム実行');
    console.log('='.repeat(60));
    console.log(`\n総問題数: ${problems.length}問\n`);

    const reviewMap = new Map();
    reviewResults.results.forEach(r => {
      reviewMap.set(r.problem_id, r);
    });

    const fixResults = problems.map(p => {
      const review = reviewMap.get(p.problem_id);
      return this.fixProblem(p, review);
    });

    const stats = {
      total: fixResults.length,
      fixed: fixResults.filter(r => r.fixed).length,
      unchanged: fixResults.filter(r => !r.fixed).length,
      changes_by_type: {}
    };

    fixResults.forEach(r => {
      r.changes.forEach(change => {
        const type = change.type;
        stats.changes_by_type[type] = (stats.changes_by_type[type] || 0) + 1;
      });
    });

    console.log('■ 自動修正結果:');
    console.log(`  - 修正した問題: ${stats.fixed}問`);
    console.log(`  - 未修正: ${stats.unchanged}問`);
    console.log('');

    console.log('■ 修正タイプ別:');
    Object.entries(stats.changes_by_type).forEach(([type, count]) => {
      console.log(`  - ${type}: ${count}件`);
    });
    console.log('');

    return {
      stats: stats,
      results: fixResults,
      fixed_problems: fixResults.filter(r => r.fixed).map(r => r.problem)
    };
  }
}

// 実行
if (require.main === module) {
  const problemsPath = './data/opus_634_final_20251023.json';
  const reviewPath = './reports/self_review_results_1761201035836.json';
  const outputDir = './reports';

  const problemsData = JSON.parse(fs.readFileSync(problemsPath, 'utf8'));
  const reviewData = JSON.parse(fs.readFileSync(reviewPath, 'utf8'));

  const problems = problemsData.problems;

  const fixer = new AutoFixSystem();
  const fixResults = fixer.fixAll(problems, reviewData);

  // 修正後の問題を保存
  const fixedProblems = fixResults.results.map(r => r.problem);
  const outputData = {
    metadata: {
      ...problemsData.metadata,
      auto_fix_date: new Date().toISOString(),
      auto_fix_stats: fixResults.stats
    },
    problems: fixedProblems
  };

  const timestamp = Date.now();
  const outputPath = `${outputDir}/opus_634_auto_fixed_${timestamp}.json`;
  fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));

  console.log(`✅ 修正済みデータ保存: ${outputPath}`);

  // 修正詳細レポート
  const detailPath = `${outputDir}/auto_fix_details_${timestamp}.json`;
  fs.writeFileSync(detailPath, JSON.stringify(fixResults, null, 2));

  console.log(`✅ 修正詳細保存: ${detailPath}`);

  console.log('\n' + '='.repeat(60));
  console.log('自動修正完了');
  console.log('='.repeat(60));
}

module.exports = AutoFixSystem;
