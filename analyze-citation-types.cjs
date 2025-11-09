const fs = require('fs');

const ambiguousProblems = JSON.parse(fs.readFileSync('audit-ambiguous-sources.json', 'utf8'));

// 引用タイプ別に分類
const citationTypes = {
  '会話履歴（詳細記述なし）': [],
  '具体的な規定なし': [],
  '認定及び処分に関する通知・報告義務': [],
  '異議申立ての期間に関する規定なし': [],
  'その他': []
};

ambiguousProblems.forEach(p => {
  if (p.basis.includes('会話履歴 (詳細記述なし)')) {
    citationTypes['会話履歴（詳細記述なし）'].push(p);
  } else if (p.basis.includes('具体的な規定はソースにない') || p.basis.includes('ソースにない')) {
    citationTypes['具体的な規定なし'].push(p);
  } else if (p.basis.includes('認定及び処分に関する通知・報告義務')) {
    citationTypes['認定及び処分に関する通知・報告義務'].push(p);
  } else if (p.basis.includes('異議申立ての期間に関する具体的な規定はソースにない')) {
    citationTypes['異議申立ての期間に関する規定なし'].push(p);
  } else {
    citationTypes['その他'].push(p);
  }
});

console.log('### 引用タイプ別の統計 ###');
console.log('');
Object.entries(citationTypes).forEach(([type, probs]) => {
  console.log(`【${type}】: ${probs.length}問`);
});

console.log('');
console.log('='.repeat(80));
console.log('');

// 各タイプの詳細
Object.entries(citationTypes).forEach(([type, probs]) => {
  if (probs.length === 0) return;

  console.log(`### 【${type}】の問題一覧 (${probs.length}問) ###`);
  console.log('');

  probs.forEach(p => {
    console.log(`問題 ${p.problem_id}:`);
    console.log(`  問題文: ${p.statement}`);
    console.log(`  正答: ${p.answer_display}`);
    console.log(`  現在の根拠: ${p.basis}`);
    console.log(`  カテゴリ: ${p.category}`);
    console.log('');
  });

  console.log('='.repeat(80));
  console.log('');
});

// 修正が必要な問題IDリストを出力
console.log('### 修正が必要な問題IDリスト ###');
console.log('');
const problemIds = ambiguousProblems.map(p => p.problem_id).sort((a, b) => a - b);
console.log(problemIds.join(', '));
console.log('');
console.log(`合計: ${problemIds.length}問`);
