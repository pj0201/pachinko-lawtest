/**
 * 低スコア問題の手動修正
 * 問題ID: 601, 610
 */

const fs = require('fs');

// データ読み込み
const data = JSON.parse(fs.readFileSync('./reports/opus_634_auto_fixed_1761201147151.json', 'utf8'));

// 問題601の修正
const p601 = data.problems.find(p => p.problem_id === 601);
if (p601) {
  console.log('■ 問題601を修正中...');
  console.log('【修正前】');
  console.log('問題文:', p601.problem_text);
  console.log('解説:', p601.explanation);
  console.log('');

  // 修正
  p601.problem_text = '風営法第7条の2に基づき、営業所の構造設備を変更する場合、あらかじめ公安委員会の承認を受けなければならない。';
  p601.explanation = '正しい。風営法第7条の2第1項により、営業所の構造または設備を変更しようとするときは、あらかじめ公安委員会に届け出て、承認を受ける必要があります。';
  p601.legal_reference = '風営法第7条の2第1項';

  console.log('【修正後】');
  console.log('問題文:', p601.problem_text);
  console.log('解説:', p601.explanation);
  console.log('法的根拠:', p601.legal_reference);
  console.log('');
}

// 問題610の修正
const p610 = data.problems.find(p => p.problem_id === 610);
if (p610) {
  console.log('■ 問題610を修正中...');
  console.log('【修正前】');
  console.log('問題文:', p610.problem_text);
  console.log('解説:', p610.explanation);
  console.log('');

  // 修正（二重否定を肯定表現に）
  p610.problem_text = '風営法第20条第5項により、遊技機は著しく射幸心をそそるおそれのない構造でなければならない。';
  p610.explanation = '正しい。風営法第20条第5項により、遊技機は著しく射幸心をそそるおそれのある構造であってはならず、国家公安委員会規則で定める基準に適合する必要があります。';

  console.log('【修正後】');
  console.log('問題文:', p610.problem_text);
  console.log('解説:', p610.explanation);
  console.log('');
}

// 保存
fs.writeFileSync('./data/opus_634_manually_fixed_20251023.json', JSON.stringify(data, null, 2));

console.log('='.repeat(60));
console.log('✅ 手動修正完了');
console.log('='.repeat(60));
console.log('保存先: data/opus_634_manually_fixed_20251023.json');
console.log('');
console.log('修正内容:');
console.log('  - 問題601: 「所定の」→具体的な法令、指示語削除');
console.log('  - 問題610: 二重否定→肯定表現、誤字修正');
