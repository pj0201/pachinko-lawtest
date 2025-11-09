const fs = require('fs');

const data = JSON.parse(fs.readFileSync('backend/db/problems.json', 'utf8'));

const ambiguousPatterns = [
  '会話履歴 (詳細記述なし)',
  '会話',
  'ソースにない',
  '具体的な規定はソースにない',
  '異議申立ての期間に関する具体的な規定はソースにない',
  '認定及び処分に関する通知・報告義務'
];

const ambiguousProblems = data.problems.filter(p => {
  return ambiguousPatterns.some(pattern => p.basis && p.basis.includes(pattern));
});

console.log('### 曖昧なソース引用を持つ問題の統計 ###');
console.log('総問題数:', data.problems.length);
console.log('曖昧な引用の問題数:', ambiguousProblems.length);
console.log('割合:', ((ambiguousProblems.length / data.problems.length) * 100).toFixed(1) + '%');
console.log('');

// カテゴリ別に集計
const byCategory = {};
ambiguousProblems.forEach(p => {
  const cat = p.category || 'unknown';
  if (!byCategory[cat]) byCategory[cat] = [];
  byCategory[cat].push(p);
});

console.log('### カテゴリ別の曖昧な問題数 ###');
Object.entries(byCategory).forEach(([cat, probs]) => {
  console.log(`${cat}: ${probs.length}問`);
});

console.log('');
console.log('### 曖昧な問題の詳細リスト ###');
console.log('');

ambiguousProblems.forEach(p => {
  console.log(`【問題 ${p.problem_id}】`);
  console.log(`問題文: ${p.statement}`);
  console.log(`正答: ${p.answer_display}`);
  console.log(`根拠: ${p.basis}`);
  console.log(`カテゴリ: ${p.category}`);
  console.log('---');
  console.log('');
});

// JSONファイルとしても出力
fs.writeFileSync('audit-ambiguous-sources.json', JSON.stringify(ambiguousProblems, null, 2), 'utf8');
console.log(`✅ ${ambiguousProblems.length}問の曖昧なソース引用を持つ問題を audit-ambiguous-sources.json に出力しました。`);
