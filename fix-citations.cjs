const fs = require('fs');

// Load problems.json
const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

// Load list of problems with ambiguous sources
const ambiguousProblems = JSON.parse(fs.readFileSync('audit-ambiguous-sources.json', 'utf8'));
const ambiguousIds = new Set(ambiguousProblems.map(p => p.problem_id));

let fixedCount = 0;
let priority1Count = 0;
let priority2Problems = [];

data.problems.forEach(problem => {
  if (!ambiguousIds.has(problem.problem_id)) {
    return; // Skip problems not in ambiguous list
  }

  const originalBasis = problem.basis;

  // Priority 1: Remove "[会話履歴 (詳細記述なし)]" annotation
  if (problem.basis.includes('[会話履歴 (詳細記述なし)]')) {
    // Remove the annotation
    problem.basis = problem.basis
      .replace(/\s*\[会話履歴 \(詳細記述なし\)\]\.?/g, '')
      .replace(/\s+\./g, '.')  // Clean up extra spaces before period
      .trim();

    // Make sure it ends with a period if it doesn't have one
    if (!problem.basis.endsWith('.') && !problem.basis.endsWith('）')) {
      problem.basis += '.';
    }

    priority1Count++;
    fixedCount++;

    console.log(`✓ 問題 ${problem.problem_id}: 会話履歴の付記を削除`);
    console.log(`  修正前: ${originalBasis}`);
    console.log(`  修正後: ${problem.basis}`);
    console.log('');
  }
  // Priority 2: Problems that need source investigation
  else if (
    problem.basis.includes('具体的な規定はソースにない') ||
    problem.basis.includes('認定及び処分に関する通知・報告義務')
  ) {
    priority2Problems.push({
      problem_id: problem.problem_id,
      statement: problem.statement,
      basis: problem.basis
    });
  }
});

// Save the corrected problems.json
fs.writeFileSync('backend/db/problems.json', JSON.stringify(data, null, 2), 'utf8');

console.log('='.repeat(80));
console.log('📊 修正完了サマリー');
console.log('='.repeat(80));
console.log(`✅ 優先度1（会話履歴の付記削除）: ${priority1Count}問`);
console.log(`⚠️  優先度2（ソース調査が必要）: ${priority2Problems.length}問`);
console.log(`📝 合計修正: ${fixedCount}問`);
console.log('');

if (priority2Problems.length > 0) {
  console.log('⚠️  以下の問題は引き続きソース調査が必要です:');
  priority2Problems.forEach(p => {
    console.log(`   問題 ${p.problem_id}: ${p.statement.substring(0, 60)}...`);
    console.log(`   現在の根拠: ${p.basis}`);
    console.log('');
  });
}

console.log('✅ backend/db/problems.json を更新しました。');
