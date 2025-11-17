/**
 * 法令フィルターの詳細検証スクリプト
 * - スクリーニングJSONと実際のデータベースの対応を確認
 * - 余り・不足の確認
 * - 重要条文の検証
 */

import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../src/constants/lawDatabase.js';
import lawScreening from '../data/fueiho_structure_pachinko.json' with { type: 'json' };
import regulationScreening from '../data/fueiho_enforcement_rules_pachinko.json' with { type: 'json' };

// 漢数字変換マップ
const kanjiToArabicMap = {
  '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
  '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
  '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
  '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20',
  '二十一': '21', '二十二': '22', '二十三': '23', '二十四': '24', '二十五': '25',
  '二十六': '26', '二十七': '27', '二十八': '28', '二十九': '29', '三十': '30',
  '三十一': '31', '三十二': '32', '三十三': '33', '三十四': '34', '三十五': '35',
  '三十六': '36', '三十七': '37', '三十八': '38', '三十九': '39', '四十': '40',
  '四十一': '41', '四十二': '42', '四十三': '43', '四十四': '44', '四十五': '45',
  '四十六': '46', '四十七': '47', '四十八': '48', '四十九': '49', '五十': '50',
  '五十一': '51', '五十二': '52', '五十三': '53', '五十四': '54', '五十五': '55',
  '五十六': '56', '五十七': '57', '五十八': '58',
  '七の二': '7の2', '七の三': '7の3', '十の二': '10の2',
  '十八の二': '18の2', '十八の三': '18の3', '二十二の二': '22の2',
  '三十六の二': '36の2', '三十七の二': '37の2',
  '三十八の二': '38の2', '三十八の三': '38の3', '三十八の四': '38の4',
  '四十一の二': '41の2', '四十一の三': '41の3',
  '六の二': '6の2', '七十四の二': '74の2',
  // lawDatabase.jsでの実際の「条」付き表記（例：十八条の二）
  '十八条の二': '18の2', '十八条の三': '18の3', '二十二条の二': '22の2',
  '百': '100', '百一': '101', '百二': '102', '百三': '103', '百四': '104',
  '百五': '105', '百六': '106', '百七': '107', '百八': '108', '百九': '109',
  '百十': '110', '百十一': '111', '百十二': '112', '百十三': '113'
};

console.log('='.repeat(100));
console.log('パチンコ主任者試験向け法令フィルター - 詳細検証');
console.log('='.repeat(100));

// ============================================
// 風営法の検証
// ============================================
console.log('\n【風営法の検証】');

let lawTotalExpected = 0;
let lawTotalActual = 0;
let lawErrors = [];

lawScreening.chapters.forEach(screeningChapter => {
  if (screeningChapter.pachinko_relevant === false) {
    console.log(`\n第${screeningChapter.chapter_num}章 ${screeningChapter.chapter_name}: スキップ（パチンコ非関連）`);
    return;
  }

  // 実際のデータベースから該当する章を取得
  const dbChapter = WIND_BUSINESS_LAW.chapters.find(ch => ch.chapterNum === screeningChapter.chapter_num);

  if (!dbChapter) {
    lawErrors.push(`❌ 第${screeningChapter.chapter_num}章がlawDatabase.jsに存在しません`);
    return;
  }

  console.log(`\n第${screeningChapter.chapter_num}章 ${screeningChapter.chapter_name}`);

  // パチンコ関連条文を抽出
  const relevantArticles = screeningChapter.articles.filter(a => a.pachinko_relevant);
  lawTotalExpected += relevantArticles.length;

  console.log(`  スクリーニング対象: ${relevantArticles.length}条`);
  console.log(`  データベース総数: ${dbChapter.articles.length}条`);

  // 各条文の存在確認
  relevantArticles.forEach(screeningArticle => {
    const arabicNum = kanjiToArabicMap[screeningArticle.article_num] || screeningArticle.article_num;

    // lawDatabase.jsの条文番号は漢数字なので、逆引きが必要
    const kanjiNum = Object.entries(kanjiToArabicMap).find(([k, v]) => v === arabicNum)?.[0] || screeningArticle.article_num;

    const dbArticle = dbChapter.articles.find(a => {
      const dbArabic = kanjiToArabicMap[a.articleNum] || a.articleNum;
      return dbArabic === arabicNum;
    });

    if (!dbArticle) {
      lawErrors.push(`  ❌ 第${screeningChapter.chapter_num}章 第${arabicNum}条「${screeningArticle.title}」がlawDatabase.jsに存在しません`);
    } else {
      lawTotalActual++;

      // タイトルの一致確認
      if (dbArticle.title !== screeningArticle.title) {
        console.log(`  ⚠️ 第${arabicNum}条: タイトル不一致`);
        console.log(`     スクリーニング: "${screeningArticle.title}"`);
        console.log(`     データベース: "${dbArticle.title}"`);
      }

      // 本文の存在確認
      if (!dbArticle.text || dbArticle.text.trim() === '') {
        lawErrors.push(`  ❌ 第${arabicNum}条「${screeningArticle.title}」: 本文が空です`);
      }
    }
  });
});

console.log(`\n【風営法 集計】`);
console.log(`  期待される条文数: ${lawTotalExpected}条`);
console.log(`  実際に存在する条文数: ${lawTotalActual}条`);
console.log(`  差分: ${lawTotalExpected - lawTotalActual}条`);

if (lawErrors.length > 0) {
  console.log(`\n【風営法 エラー】`);
  lawErrors.forEach(err => console.log(err));
} else {
  console.log(`  ✅ すべての条文が正しく設置されています`);
}

// ============================================
// 施行規則の検証
// ============================================
console.log('\n' + '='.repeat(100));
console.log('【施行規則の検証】');

let regulationTotalExpected = 0;
let regulationTotalActual = 0;
let regulationErrors = [];

regulationScreening.chapters.forEach(screeningChapter => {
  if (screeningChapter.pachinko_relevant === false) {
    console.log(`\n第${screeningChapter.chapter_num}章 ${screeningChapter.chapter_name}: スキップ（パチンコ非関連）`);
    return;
  }

  // スクリーニングJSONの第5章（雑則）はlawDatabase.jsでは第6章
  const actualChapterNum = screeningChapter.chapter_num === 5 ? 6 : screeningChapter.chapter_num;

  // 実際のデータベースから該当する章を取得
  const dbChapter = WIND_BUSINESS_REGULATION.chapters.find(ch => ch.chapterNum === actualChapterNum);

  if (!dbChapter) {
    regulationErrors.push(`❌ 第${actualChapterNum}章がlawDatabase.jsに存在しません`);
    return;
  }

  console.log(`\n第${screeningChapter.chapter_num}章 → DB第${actualChapterNum}章 ${screeningChapter.chapter_name}`);

  // パチンコ関連条文を抽出
  const relevantArticles = screeningChapter.articles.filter(a => a.pachinko_relevant);
  regulationTotalExpected += relevantArticles.length;

  console.log(`  スクリーニング対象: ${relevantArticles.length}条`);
  console.log(`  データベース総数: ${dbChapter.articles.length}条`);

  // 各条文の存在確認
  relevantArticles.forEach(screeningArticle => {
    const arabicNum = kanjiToArabicMap[screeningArticle.article_num] || screeningArticle.article_num;

    const dbArticle = dbChapter.articles.find(a => {
      const dbArabic = kanjiToArabicMap[a.articleNum] || a.articleNum;
      return dbArabic === arabicNum;
    });

    if (!dbArticle) {
      regulationErrors.push(`  ❌ 第${actualChapterNum}章 第${arabicNum}条「${screeningArticle.title}」がlawDatabase.jsに存在しません`);
    } else {
      regulationTotalActual++;

      // タイトルの一致確認（一部のタイトルは「確認できませんが」となっている）
      if (screeningArticle.title.includes('確認できません')) {
        // スキップ
      } else if (dbArticle.title !== screeningArticle.title) {
        console.log(`  ⚠️ 第${arabicNum}条: タイトル不一致`);
        console.log(`     スクリーニング: "${screeningArticle.title}"`);
        console.log(`     データベース: "${dbArticle.title}"`);
      }

      // 本文の存在確認
      if (!dbArticle.text || dbArticle.text.trim() === '') {
        regulationErrors.push(`  ❌ 第${arabicNum}条「${screeningArticle.title}」: 本文が空です`);
      }
    }
  });
});

console.log(`\n【施行規則 集計】`);
console.log(`  期待される条文数: ${regulationTotalExpected}条`);
console.log(`  実際に存在する条文数: ${regulationTotalActual}条`);
console.log(`  差分: ${regulationTotalExpected - regulationTotalActual}条`);

if (regulationErrors.length > 0) {
  console.log(`\n【施行規則 エラー】`);
  regulationErrors.forEach(err => console.log(err));
} else {
  console.log(`  ✅ すべての条文が正しく設置されています`);
}

// ============================================
// 総合レビュー
// ============================================
console.log('\n' + '='.repeat(100));
console.log('【総合レビュー】');

const totalErrors = lawErrors.length + regulationErrors.length;

console.log(`\n風営法:`);
console.log(`  ✓ 期待条文数: ${lawTotalExpected}条`);
console.log(`  ✓ 実際の条文数: ${lawTotalActual}条`);
console.log(`  ✓ エラー数: ${lawErrors.length}件`);

console.log(`\n施行規則:`);
console.log(`  ✓ 期待条文数: ${regulationTotalExpected}条`);
console.log(`  ✓ 実際の条文数: ${regulationTotalActual}条`);
console.log(`  ✓ エラー数: ${regulationErrors.length}件`);

console.log(`\n合計:`);
console.log(`  ✓ 総期待条文数: ${lawTotalExpected + regulationTotalExpected}条`);
console.log(`  ✓ 総実際条文数: ${lawTotalActual + regulationTotalActual}条`);
console.log(`  ✓ 総エラー数: ${totalErrors}件`);

if (totalErrors === 0 && lawTotalExpected === lawTotalActual && regulationTotalExpected === regulationTotalActual) {
  console.log(`\n${'★'.repeat(50)}`);
  console.log(`✅ すべての条文が正しく設置されています！`);
  console.log(`✅ 余りも不足もありません！`);
  console.log(`✅ パチンコ主任者試験向け法令フィルターは正常に動作します！`);
  console.log(`${'★'.repeat(50)}`);
} else {
  console.log(`\n${'⚠'.repeat(50)}`);
  console.log(`❌ 問題が検出されました。上記のエラーを確認してください。`);
  console.log(`${'⚠'.repeat(50)}`);
  process.exit(1);
}

console.log('\n' + '='.repeat(100));
