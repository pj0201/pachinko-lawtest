const fs = require('fs');

// Load problems.json
const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

// Load original ambiguous problems list
const originalAmbiguous = JSON.parse(fs.readFileSync('audit-ambiguous-sources.json', 'utf8'));
const ambiguousIds = new Set(originalAmbiguous.map(p => p.problem_id));

let stillAmbiguous = [];
let fixed = [];

data.problems.forEach(problem => {
  if (!ambiguousIds.has(problem.problem_id)) {
    return;
  }

  // Check if still contains ambiguous patterns
  const hasConversationHistory = problem.basis.includes('会話履歴 (詳細記述なし)');
  const hasNoSpecificRegulation = problem.basis.includes('具体的な規定はソースにない');
  const hasParenthesisOnly = problem.basis.match(/^（.*）$/);

  if (hasConversationHistory || hasNoSpecificRegulation || hasParenthesisOnly) {
    stillAmbiguous.push({
      problem_id: problem.problem_id,
      basis: problem.basis
    });
  } else {
    fixed.push(problem.problem_id);
  }
});

console.log('='.repeat(80));
console.log('📊 修正検証レポート');
console.log('='.repeat(80));
console.log('');
console.log(`✅ 修正完了: ${fixed.length}問`);
console.log(`⚠️  まだ曖昧: ${stillAmbiguous.length}問`);
console.log('');

if (stillAmbiguous.length > 0) {
  console.log('⚠️  以下の問題はまだ曖昧なソース引用を含んでいます:');
  console.log('');
  stillAmbiguous.forEach(p => {
    console.log(`  問題 ${p.problem_id}:`);
    console.log(`    根拠: ${p.basis}`);
    console.log('');
  });
} else {
  console.log('🎉 全ての曖昧なソース引用が修正されました！');
}

console.log('='.repeat(80));
console.log('');

// Summary of fixed problems
if (fixed.length > 0) {
  console.log('✅ 修正された問題ID一覧:');
  console.log(fixed.sort((a, b) => a - b).join(', '));
  console.log('');
}
