const fs = require('fs');

// Load problems.json
const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

const remainingIds = [1, 3, 9, 10, 11, 23, 24];
let fixedCount = 0;

data.problems.forEach(problem => {
  if (!remainingIds.includes(problem.problem_id)) {
    return;
  }

  const originalBasis = problem.basis;

  // Remove "[会話履歴 (詳細記述なし)]" annotation
  if (problem.basis.includes('[会話履歴 (詳細記述なし)]')) {
    problem.basis = problem.basis
      .replace(/\s*\[会話履歴 \(詳細記述なし\)\]\.?/g, '')
      .replace(/\s+\./g, '.')
      .trim();

    // Ensure it ends with a period
    if (!problem.basis.endsWith('.')) {
      problem.basis += '.';
    }

    fixedCount++;

    console.log(`✓ 問題 ${problem.problem_id}: 会話履歴の付記を削除`);
    console.log(`  修正前: ${originalBasis}`);
    console.log(`  修正後: ${problem.basis}`);
    console.log('');
  }
});

// Save the corrected problems.json
fs.writeFileSync('backend/db/problems.json', JSON.stringify(data, null, 2), 'utf8');

console.log('='.repeat(80));
console.log(`✅ 追加で ${fixedCount}問の会話履歴付記を削除しました。`);
console.log('✅ backend/db/problems.json を更新しました。');
