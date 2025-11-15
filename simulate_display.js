/**
 * コンポーネントの実際の表示をシミュレート
 * whiteSpace: 'pre-wrap' での表示を確認
 */

import { WIND_BUSINESS_LAW } from './src/constants/lawDatabase.js';

console.log('=== 実際のアプリ表示シミュレーション ===\n');
console.log('whiteSpace: "pre-wrap" が適用されるため、\\nは改行として表示されます\n');

// 修正した7条文を表示
const articlesToDisplay = [
  { chapter: 3, num: '十九', title: '遊技料金等の規制' },
  { chapter: 3, num: '二十', title: '遊技機の規制及び認定等' },
  { chapter: 3, num: '二十一', title: '条例への委任' },
  { chapter: 3, num: '二十二', title: '風俗営業を営む者の禁止行為等' },
  { chapter: 4, num: '二十七', title: '営業等の届出' },
  { chapter: 4, num: '二十八', title: '店舗型性風俗特殊営業の禁止区域等' },
  { chapter: 4, num: '三十', title: '営業の停止等' }
];

articlesToDisplay.forEach((check, index) => {
  const chapter = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === check.chapter);
  const article = chapter.articles.find(art => art.articleNum === check.num);

  console.log('═'.repeat(70));
  console.log(`第${check.num}条：${article.title}`);
  console.log('═'.repeat(70));
  console.log(article.text);
  console.log('\n');

  // 冒頭100文字を確認
  console.log(`📝 冒頭100文字: ${article.text.substring(0, 100)}...`);
  console.log(`📊 テキスト長: ${article.text.length}文字`);
  console.log(`📊 改行数: ${(article.text.match(/\n/g) || []).length}回`);

  // 不正文字チェック
  if (check.num === '三十') {
    if (article.text.includes('\n9\n')) {
      console.log('❌ 不正な文字「9」が含まれています！');
    } else {
      console.log('✅ 不正な文字「9」は含まれていません');
    }
  }

  console.log('\n\n');
});

// ロック済み条文も1つ表示して比較
console.log('═'.repeat(70));
console.log('【比較：ロック済み条文（第一条）】');
console.log('═'.repeat(70));
const article1 = WIND_BUSINESS_LAW.chapters[0].articles[0];
console.log(article1.text);
console.log('\n');
console.log(`📝 冒頭100文字: ${article1.text.substring(0, 100)}...`);
console.log(`📊 テキスト長: ${article1.text.length}文字`);
console.log(`📊 改行数: ${(article1.text.match(/\n/g) || []).length}回`);
