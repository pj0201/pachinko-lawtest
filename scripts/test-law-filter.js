/**
 * 法令フィルター機能のテストスクリプト
 */

import {
  filterPachinkoLaw,
  filterPachinkoRegulation,
  getKeyArticlesLaw,
  getKeyArticlesRegulation,
  getFilteringStats
} from '../src/utils/lawFilter.js';

console.log('='.repeat(80));
console.log('パチンコ主任者試験向け法令フィルタリング - テスト結果');
console.log('='.repeat(80));

// 統計情報を取得
const stats = getFilteringStats();

console.log('\n【フィルタリング統計】');
console.log('\n1. 風営法（本法）');
console.log(`   全条文数: ${stats.law.total}条`);
console.log(`   パチンコ関連: ${stats.law.pachinko}条 (${stats.law.percentage}%)`);
console.log(`   除外: ${stats.law.excluded}条`);

console.log('\n2. 風営法施行規則');
console.log(`   全条文数: ${stats.regulation.total}条`);
console.log(`   パチンコ関連: ${stats.regulation.pachinko}条 (${stats.regulation.percentage}%)`);
console.log(`   除外: ${stats.regulation.excluded}条`);

// フィルタリング結果を取得
const filteredLaw = filterPachinkoLaw();
const filteredRegulation = filterPachinkoRegulation();

console.log('\n【フィルタリング後の章構成】');
console.log('\n風営法:');
filteredLaw.chapters.forEach(ch => {
  console.log(`  第${ch.chapterNum}章 ${ch.chapterName} (${ch.articles.length}条)`);
});

console.log('\n施行規則:');
filteredRegulation.chapters.forEach(ch => {
  console.log(`  第${ch.chapterNum}章 ${ch.chapterName} (${ch.articles.length}条)`);
});

// 重要条文リストを取得
const keyArticlesLaw = getKeyArticlesLaw();
const keyArticlesRegulation = getKeyArticlesRegulation();

console.log('\n【パチンコ重要条文】');
console.log('\n風営法:');
keyArticlesLaw.forEach(article => {
  console.log(`  第${article.articleNum}条: ${article.title}`);
});

console.log('\n施行規則:');
keyArticlesRegulation.forEach(article => {
  console.log(`  第${article.articleNum}条: ${article.title}`);
});

// サンプル条文の確認
console.log('\n【サンプル条文（風営法 第19条）】');
const chapter3 = filteredLaw.chapters.find(ch => ch.chapterNum === 3);
const article19 = chapter3?.articles.find(a => a.articleNum === '十九');
if (article19) {
  console.log(`タイトル: ${article19.title}`);
  console.log(`重要度: ${article19.importance}`);
  console.log(`本文: ${article19.text.substring(0, 100)}...`);
} else {
  console.log('❌ 第19条が見つかりません');
}

console.log('\n' + '='.repeat(80));
console.log('テスト完了');
console.log('='.repeat(80));
