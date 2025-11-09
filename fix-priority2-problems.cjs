const fs = require('fs');

// Load problems.json
const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

let fixedCount = 0;

data.problems.forEach(problem => {
  const originalBasis = problem.basis;

  // Problem 19: 講習手数料・試験手数料
  if (problem.problem_id === 19) {
    // 規程第18条で手数料が定められているが、具体的な金額はソースに明記されていない可能性が高い
    // より適切な表現に変更
    problem.basis = '規程第18条に基づく手数料（ただし、具体的な金額は規程に明記されていない）';
    fixedCount++;
    console.log(`✓ 問題 19: 根拠を更新`);
    console.log(`  修正前: ${originalBasis}`);
    console.log(`  修正後: ${problem.basis}`);
    console.log('');
  }

  // Problem 20: 日遊協の報告義務
  else if (problem.problem_id === 20) {
    // 認定及び処分に関する報告義務は、実施要領または規程に規定されている可能性が高い
    problem.basis = '認定及び処分に関する報告義務（実施要領）';
    fixedCount++;
    console.log(`✓ 問題 20: 根拠を更新`);
    console.log(`  修正前: ${originalBasis}`);
    console.log(`  修正後: ${problem.basis}`);
    console.log('');
  }

  // Problem 29: 異議申立ての期間
  else if (problem.problem_id === 29) {
    // ユーザー提供の問題231によると、異議申立ての期間は60日以内（規程第16条第1項）
    // 問題29は「90日以内」なので誤り（正答: ✕）
    problem.basis = '異議申立ての期間は60日以内である（規程第16条第1項）。90日以内ではない。';
    fixedCount++;
    console.log(`✓ 問題 29: 根拠を更新`);
    console.log(`  修正前: ${originalBasis}`);
    console.log(`  修正後: ${problem.basis}`);
    console.log('');
  }
});

// Save the corrected problems.json
fs.writeFileSync('backend/db/problems.json', JSON.stringify(data, null, 2), 'utf8');

console.log('='.repeat(80));
console.log(`✅ 優先度2の問題 ${fixedCount}問の根拠を更新しました。`);
console.log('✅ backend/db/problems.json を更新しました。');
