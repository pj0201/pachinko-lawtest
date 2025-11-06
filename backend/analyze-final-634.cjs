const fs = require('fs');
const data = JSON.parse(fs.readFileSync('./data/opus_634_final_20251023.json', 'utf8'));
const problems = data.problems;

console.log('■ 最終データ統計');
console.log('総問題数:', problems.length);
console.log('');

// カテゴリ分布
const categories = {};
problems.forEach(p => {
  const cat = p.category || '未分類';
  categories[cat] = (categories[cat] || 0) + 1;
});

console.log('■ カテゴリ別分布:');
Object.entries(categories)
  .sort((a, b) => b[1] - a[1])
  .forEach(([cat, count]) => {
    const percent = (count / problems.length * 100).toFixed(1);
    console.log(`  ${cat}: ${count}問 (${percent}%)`);
  });

console.log('');

// テーマ別統計
function countTheme(theme) {
  return problems.filter(p => {
    const text = `${p.problem_text} ${p.explanation}`;
    return text.includes(theme);
  }).length;
}

console.log('■ 主要テーマの問題数（補充後）:');
const themes = {
  '取消': countTheme('取消'),
  '違反': countTheme('違反'),
  '設備': countTheme('設備'),
  '構造': countTheme('構造'),
  '営業許可': countTheme('営業許可')
};

Object.entries(themes).forEach(([theme, count]) => {
  console.log(`  ${theme}: ${count}問`);
});

console.log('');

// 法的根拠明記率
const withLegalRef = problems.filter(p => {
  const ref = p.legal_reference || '';
  return /第\d+条/.test(ref);
}).length;

const refRate = (withLegalRef / problems.length * 100).toFixed(1);
console.log('■ 品質指標:');
console.log(`  法的根拠明記率: ${refRate}% (${withLegalRef}/${problems.length}問)`);

// 平均文字数
const avgLength = Math.round(
  problems.reduce((sum, p) => sum + p.problem_text.length, 0) / problems.length
);
console.log('  平均問題文字数:', avgLength, '字');
