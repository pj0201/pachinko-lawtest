const fs = require('fs');

// Load problems.json
const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

let fixedCount = 0;
let totalAmbiguous = 0;

data.problems.forEach(problem => {
  const originalBasis = problem.basis;

  // Check if it contains any form of "会話履歴 (詳細記述なし)"
  if (problem.basis.includes('会話履歴 (詳細記述なし)')) {
    totalAmbiguous++;

    // Remove the annotation - handle both patterns:
    // Pattern 1: [規程第X条, 会話履歴 (詳細記述なし)]
    // Pattern 2: [会話履歴 (詳細記述なし)]

    // First, remove ", 会話履歴 (詳細記述なし)" if it exists
    problem.basis = problem.basis.replace(/,\s*会話履歴 \(詳細記述なし\)/g, '');

    // Then remove standalone "[会話履歴 (詳細記述なし)]"
    problem.basis = problem.basis.replace(/\s*\[会話履歴 \(詳細記述なし\)\]\.?/g, '');

    // Clean up extra spaces and ensure proper ending
    problem.basis = problem.basis.replace(/\s+\./g, '.').trim();

    // Ensure it ends with a period
    if (!problem.basis.endsWith('.') && !problem.basis.endsWith('）') && !problem.basis.endsWith(']')) {
      problem.basis += '.';
    }

    if (originalBasis !== problem.basis) {
      fixedCount++;
      console.log(`✓ 問題 ${problem.problem_id}: 会話履歴の付記を削除`);
      console.log(`  修正前: ${originalBasis}`);
      console.log(`  修正後: ${problem.basis}`);
      console.log('');
    }
  }
});

// Save the corrected problems.json
fs.writeFileSync('backend/db/problems.json', JSON.stringify(data, null, 2), 'utf8');

console.log('='.repeat(80));
console.log(`✅ 合計 ${fixedCount}問の会話履歴付記を削除しました。`);
console.log(`📊 会話履歴を含む問題の総数: ${totalAmbiguous}問`);
console.log('✅ backend/db/problems.json を更新しました。');
