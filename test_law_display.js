/**
 * lawDatabase.jsが正しく読み込めるか、修正した条文が正しく表示されるかテスト
 */

import { WIND_BUSINESS_LAW } from './src/constants/lawDatabase.js';

console.log('=== lawDatabase.js 読み込みテスト ===\n');

// 修正した7条文を検証
const articlesToCheck = [
  { chapter: 3, num: '十九', title: '遊技料金等の規制', expectedStart: '第二条第一項第四号の営業を営む' },
  { chapter: 3, num: '二十', title: '遊技機の規制及び認定等', expectedStart: '第四条第四項に規定する営業を営む' },
  { chapter: 3, num: '二十一', title: '条例への委任', expectedStart: '第十二条から第十九条まで、前条第一項' },
  { chapter: 3, num: '二十二', title: '風俗営業を営む者の禁止行為等', expectedStart: '風俗営業を営む者は、次に掲げる行為をしてはならない' },
  { chapter: 4, num: '二十七', title: '営業等の届出', expectedStart: '店舗型性風俗特殊営業を営もうとする者は' },
  { chapter: 4, num: '二十八', title: '店舗型性風俗特殊営業の禁止区域等', expectedStart: '店舗型性風俗特殊営業は、一団地の官公庁施設' },
  { chapter: 4, num: '三十', title: '営業の停止等', expectedStart: '公安委員会は、店舗型性風俗特殊営業を営む者' }
];

let passCount = 0;
let failCount = 0;

console.log('【修正した7条文の冒頭チェック】\n');

articlesToCheck.forEach(check => {
  // 章を取得
  const chapter = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === check.chapter);
  if (!chapter) {
    console.log(`❌ 第${check.chapter}章が見つかりません`);
    failCount++;
    return;
  }

  // 条文を取得
  const article = chapter.articles.find(art => art.articleNum === check.num);
  if (!article) {
    console.log(`❌ 第${check.num}条が見つかりません`);
    failCount++;
    return;
  }

  // タイトルチェック
  if (article.title !== check.title) {
    console.log(`⚠️  第${check.num}条のタイトルが異なります`);
    console.log(`   期待: ${check.title}`);
    console.log(`   実際: ${article.title}`);
  }

  // 冒頭チェック
  const actualStart = article.text.substring(0, check.expectedStart.length);
  if (actualStart === check.expectedStart) {
    console.log(`✅ 第${check.num}条（${article.title}）`);
    console.log(`   冒頭: ${actualStart.substring(0, 40)}...`);
    passCount++;
  } else {
    console.log(`❌ 第${check.num}条（${article.title}）- 冒頭が一致しません`);
    console.log(`   期待: ${check.expectedStart.substring(0, 40)}...`);
    console.log(`   実際: ${actualStart.substring(0, 40)}...`);
    failCount++;
  }
  console.log('');
});

// 第三十条の「9」混入チェック
console.log('【第三十条の不正文字チェック】\n');
const chapter4 = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === 4);
const article30 = chapter4.articles.find(art => art.articleNum === '三十');
if (article30.text.includes('営業を\n9\n営む者')) {
  console.log('❌ 第三十条に不正な文字「9」が含まれています');
  failCount++;
} else if (article30.text.includes('営業を営む者')) {
  console.log('✅ 第三十条の不正文字「9」は削除されています');
  passCount++;
} else {
  console.log('⚠️  第三十条のテキストが想定と異なります');
}

// 改行のチェック
console.log('\n【改行処理のチェック】\n');
const article1 = WIND_BUSINESS_LAW.chapters[0].articles[0];
const lineCount = article1.text.split('\n').length;
console.log(`第一条のテキストに含まれる改行数: ${lineCount - 1}`);
if (lineCount > 1) {
  console.log('✅ 改行が正しく保持されています');
  passCount++;
} else {
  console.log('⚠️  改行が保持されていない可能性があります');
}

// 結果サマリー
console.log('\n===================');
console.log('【検証結果サマリー】');
console.log('===================');
console.log(`✅ 成功: ${passCount}件`);
console.log(`❌ 失敗: ${failCount}件`);

if (failCount === 0) {
  console.log('\n🎉 すべての検証に合格しました！');
  process.exit(0);
} else {
  console.log('\n⚠️  いくつかの検証に失敗しました。');
  process.exit(1);
}
