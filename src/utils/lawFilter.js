/**
 * パチンコ主任者試験向け法令フィルター
 * 風営法・施行規則からパチンコ業界に関連する条文のみを抽出
 */

import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../constants/lawDatabase.js';
import lawScreening from '../../data/fueiho_structure_pachinko.json' with { type: 'json' };
import regulationScreening from '../../data/fueiho_enforcement_rules_pachinko.json' with { type: 'json' };

/**
 * 漢数字からアラビア数字への変換マップ
 */
const kanjiToArabicMap = {
  '一': '1',
  '二': '2',
  '三': '3',
  '四': '4',
  '五': '5',
  '六': '6',
  '七': '7',
  '八': '8',
  '九': '9',
  '十': '10',
  '十一': '11',
  '十二': '12',
  '十三': '13',
  '十四': '14',
  '十五': '15',
  '十六': '16',
  '十七': '17',
  '十八': '18',
  '十九': '19',
  '二十': '20',
  '二十一': '21',
  '二十二': '22',
  '二十三': '23',
  '二十四': '24',
  '二十五': '25',
  '二十六': '26',
  '二十七': '27',
  '二十八': '28',
  '二十九': '29',
  '三十': '30',
  '三十一': '31',
  '三十二': '32',
  '三十三': '33',
  '三十四': '34',
  '三十五': '35',
  '三十六': '36',
  '三十七': '37',
  '三十八': '38',
  '三十九': '39',
  '四十': '40',
  '四十一': '41',
  '四十二': '42',
  '四十三': '43',
  '四十四': '44',
  '四十五': '45',
  '四十六': '46',
  '四十七': '47',
  '四十八': '48',
  '四十九': '49',
  '五十': '50',
  '五十一': '51',
  '五十二': '52',
  '五十三': '53',
  '五十四': '54',
  '五十五': '55',
  '五十六': '56',
  '五十七': '57',
  '五十八': '58',
  // 施行規則用の大きい数字
  '百': '100',
  '百一': '101',
  '百二': '102',
  '百三': '103',
  '百四': '104',
  '百五': '105',
  '百六': '106',
  '百七': '107',
  '百八': '108',
  '百九': '109',
  '百十': '110',
  '百十一': '111',
  '百十二': '112',
  '百十三': '113',
  // 「の」を含む条文番号（例：七の二 → 7の2）
  '七の二': '7の2',
  '七の三': '7の3',
  '十の二': '10の2',
  '十八の二': '18の2',
  '十八の三': '18の3',
  '二十二の二': '22の2',
  '三十六の二': '36の2',
  '三十七の二': '37の2',
  '三十八の二': '38の2',
  '三十八の三': '38の3',
  '三十八の四': '38の4',
  '四十一の二': '41の2',
  '四十一の三': '41の3',
  '六の二': '6の2',
  '七十四の二': '74の2',
};

/**
 * パチンコ関連の章番号セット（風営法）
 */
const pachinkoRelevantChaptersLaw = new Set([1, 2, 3, 5, 6, 7]);

/**
 * パチンコ関連の章番号セット（施行規則）
 * 注：施行規則には第5章がなく、第4章の後に第6章（雑則）が来る
 */
const pachinkoRelevantChaptersRegulation = new Set([1, 2, 3, 6]);

/**
 * パチンコ関連条文マップを生成（風営法）
 */
function buildPachinkoArticleMapLaw() {
  const map = new Map();

  lawScreening.chapters.forEach(chapter => {
    if (chapter.pachinko_relevant === false) return;

    if (chapter.articles) {
      chapter.articles.forEach(article => {
        if (article.pachinko_relevant) {
          const key = `${chapter.chapter_num}-${article.article_num}`;
          map.set(key, {
            importance: article.importance || 'normal',
            title: article.title
          });
        }
      });
    }
  });

  return map;
}

/**
 * パチンコ関連条文マップを生成（施行規則）
 * 注：スクリーニングJSONでは第5章が雑則だが、lawDatabase.jsでは第6章が雑則
 */
function buildPachinkoArticleMapRegulation() {
  const map = new Map();

  regulationScreening.chapters.forEach(chapter => {
    if (chapter.pachinko_relevant === false) return;

    if (chapter.articles) {
      chapter.articles.forEach(article => {
        if (article.pachinko_relevant) {
          // スクリーニングJSONの第5章（雑則）はlawDatabase.jsでは第6章
          const actualChapterNum = chapter.chapter_num === 5 ? 6 : chapter.chapter_num;
          const key = `${actualChapterNum}-${article.article_num}`;
          map.set(key, {
            importance: article.importance || 'normal',
            title: article.title
          });
        }
      });
    }
  });

  return map;
}

// グローバルマップを生成
const pachinkoArticleMapLaw = buildPachinkoArticleMapLaw();
const pachinkoArticleMapRegulation = buildPachinkoArticleMapRegulation();

/**
 * 風営法からパチンコ関連条文のみをフィルタリング
 * @returns {Object} フィルタリングされた法律データ
 */
export function filterPachinkoLaw() {
  if (!WIND_BUSINESS_LAW || !WIND_BUSINESS_LAW.chapters) {
    return { chapters: [] };
  }

  const filteredChapters = WIND_BUSINESS_LAW.chapters
    .filter(chapter => pachinkoRelevantChaptersLaw.has(chapter.chapterNum))
    .map(chapter => {
      const filteredArticles = chapter.articles.filter(article => {
        const arabicNum = kanjiToArabicMap[article.articleNum] || article.articleNum;
        const key = `${chapter.chapterNum}-${arabicNum}`;
        return pachinkoArticleMapLaw.has(key);
      }).map(article => {
        const arabicNum = kanjiToArabicMap[article.articleNum] || article.articleNum;
        const key = `${chapter.chapterNum}-${arabicNum}`;
        const metadata = pachinkoArticleMapLaw.get(key);

        return {
          ...article,
          pachinkoRelevant: true,
          importance: metadata?.importance || 'normal'
        };
      });

      return {
        ...chapter,
        articles: filteredArticles,
        pachinkoRelevant: true
      };
    });

  return {
    ...WIND_BUSINESS_LAW,
    chapters: filteredChapters
  };
}

/**
 * 施行規則からパチンコ関連条文のみをフィルタリング
 * @returns {Object} フィルタリングされた規則データ
 */
export function filterPachinkoRegulation() {
  if (!WIND_BUSINESS_REGULATION || !WIND_BUSINESS_REGULATION.chapters) {
    return { chapters: [] };
  }

  const filteredChapters = WIND_BUSINESS_REGULATION.chapters
    .filter(chapter => pachinkoRelevantChaptersRegulation.has(chapter.chapterNum))
    .map(chapter => {
      const filteredArticles = chapter.articles.filter(article => {
        const arabicNum = kanjiToArabicMap[article.articleNum] || article.articleNum;
        const key = `${chapter.chapterNum}-${arabicNum}`;
        return pachinkoArticleMapRegulation.has(key);
      }).map(article => {
        const arabicNum = kanjiToArabicMap[article.articleNum] || article.articleNum;
        const key = `${chapter.chapterNum}-${arabicNum}`;
        const metadata = pachinkoArticleMapRegulation.get(key);

        return {
          ...article,
          pachinkoRelevant: true,
          importance: metadata?.importance || 'normal'
        };
      });

      return {
        ...chapter,
        articles: filteredArticles,
        pachinkoRelevant: true
      };
    });

  return {
    ...WIND_BUSINESS_REGULATION,
    chapters: filteredChapters
  };
}

/**
 * パチンコ関連の重要条文リストを取得（風営法）
 * @returns {Array} 重要条文の配列
 */
export function getKeyArticlesLaw() {
  return Array.from(pachinkoArticleMapLaw.entries())
    .filter(([_, metadata]) => metadata.importance === 'high')
    .map(([key, metadata]) => {
      const [chapterNum, articleNum] = key.split('-');
      return {
        chapterNum: parseInt(chapterNum),
        articleNum,
        title: metadata.title,
        importance: metadata.importance
      };
    });
}

/**
 * パチンコ関連の重要条文リストを取得（施行規則）
 * @returns {Array} 重要条文の配列
 */
export function getKeyArticlesRegulation() {
  return Array.from(pachinkoArticleMapRegulation.entries())
    .filter(([_, metadata]) => metadata.importance === 'high')
    .map(([key, metadata]) => {
      const [chapterNum, articleNum] = key.split('-');
      return {
        chapterNum: parseInt(chapterNum),
        articleNum,
        title: metadata.title,
        importance: metadata.importance
      };
    });
}

/**
 * 統計情報を取得
 * @returns {Object} フィルタリング統計
 */
export function getFilteringStats() {
  const lawTotal = WIND_BUSINESS_LAW?.chapters?.reduce(
    (sum, ch) => sum + (ch.articles?.length || 0), 0
  ) || 0;

  const lawFiltered = Array.from(pachinkoArticleMapLaw.keys()).length;

  const regulationTotal = WIND_BUSINESS_REGULATION?.chapters?.reduce(
    (sum, ch) => sum + (ch.articles?.length || 0), 0
  ) || 0;

  const regulationFiltered = Array.from(pachinkoArticleMapRegulation.keys()).length;

  return {
    law: {
      total: lawTotal,
      pachinko: lawFiltered,
      excluded: lawTotal - lawFiltered,
      percentage: ((lawFiltered / lawTotal) * 100).toFixed(1)
    },
    regulation: {
      total: regulationTotal,
      pachinko: regulationFiltered,
      excluded: regulationTotal - regulationFiltered,
      percentage: ((regulationFiltered / regulationTotal) * 100).toFixed(1)
    }
  };
}
