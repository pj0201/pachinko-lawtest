/**
 * QuestionCategorizer - 問題の自動分類ロジック
 *
 * カテゴリ:
 * 1. 総則・定義（総則・法律基礎）
 * 2. 遊技機仕様（機械的原理・検定基準）
 * 3. 遊技料金・営業管理
 * 4. 営業所管理・入場管理
 * 5. 実務知識（現場対応）
 */

class QuestionCategorizer {
  constructor() {
    // カテゴリとキーワードのマッピング
    this.categoryKeywords = {
      '総則・定義': {
        keywords: ['風営法', '定義', '目的', '適用', '解釈', '法律'],
        relevance: 1.0
      },
      '遊技機仕様': {
        keywords: ['遊技機', '仕様', '機械', '原理', '検定', 'パチンコ', 'スロット', 'メダル'],
        relevance: 0.9
      },
      '遊技料金': {
        keywords: ['料金', '賃金', '価格', '金銭', '両替', '交換'],
        relevance: 0.8
      },
      '営業所管理': {
        keywords: ['営業所', '出張所', '管理', '設置', '構造', '施設'],
        relevance: 0.9
      },
      '入場管理': {
        keywords: ['入場', '入店', '管理', '年齢', '確認', '身分'],
        relevance: 0.8
      },
      '現場対応': {
        keywords: ['対応', '事件', '報告', '指導', '処分', '実務'],
        relevance: 0.7
      },
      '記録・報告': {
        keywords: ['記録', '報告', '書類', '帳簿', '管理'],
        relevance: 0.8
      },
      '其の他法律': {
        keywords: ['特例', '例外', '特則', 'その他'],
        relevance: 0.5
      }
    };

    // 難易度判定ルール
    this.difficultyRules = {
      'easy': {
        keywords: ['定義', '意味', 'とは', '説明'],
        minKeywordHits: 1
      },
      'medium': {
        keywords: ['適用', '条件', '要件', 'ただし'],
        minKeywordHits: 1
      },
      'hard': {
        keywords: ['例外', '特例', '相互', '複合', '判断'],
        minKeywordHits: 1
      }
    };
  }

  /**
   * 問題をカテゴライズ
   * @param {Object} question - {question, options, correct_index, explanation}
   * @returns {Object}
   */
  categorizeQuestion(question) {
    const combinedText = `${question.question} ${question.explanation}`.toLowerCase();

    // カテゴリスコア計算
    const scores = {};
    for (const [category, config] of Object.entries(this.categoryKeywords)) {
      scores[category] = this._calculateCategoryScore(combinedText, config.keywords, config.relevance);
    }

    // 最高スコアのカテゴリを選択
    const bestCategory = Object.entries(scores)
      .sort((a, b) => b[1] - a[1])[0][0];

    // 難易度判定
    const difficulty = this._determineDifficulty(question.question, combinedText);

    // サブカテゴリ判定
    const subcategory = this._determineSubcategory(combinedText);

    return {
      mainCategory: bestCategory,
      subcategory,
      difficulty,
      categoryScores: scores,
      confidence: scores[bestCategory] // 信頼度
    };
  }

  /**
   * 複数問をバッチ処理
   */
  categorizeQuestions(questions) {
    return questions.map(q => ({
      ...q,
      categorization: this.categorizeQuestion(q)
    }));
  }

  /**
   * カテゴリスコア計算
   */
  _calculateCategoryScore(text, keywords, baseRelevance) {
    let hits = 0;
    for (const keyword of keywords) {
      const regex = new RegExp(keyword, 'g');
      const matches = text.match(regex);
      if (matches) {
        hits += matches.length;
      }
    }
    return (Math.min(hits, keywords.length * 2) / (keywords.length * 2)) * baseRelevance;
  }

  /**
   * 難易度判定
   */
  _determineDifficulty(question, text) {
    const hardHits = this.difficultyRules.hard.keywords.filter(kw => text.includes(kw)).length;
    const mediumHits = this.difficultyRules.medium.keywords.filter(kw => text.includes(kw)).length;
    const easyHits = this.difficultyRules.easy.keywords.filter(kw => text.includes(kw)).length;

    // 総合判定
    if (hardHits >= this.difficultyRules.hard.minKeywordHits) {
      return 'hard';
    } else if (mediumHits >= this.difficultyRules.medium.minKeywordHits) {
      return 'medium';
    }
    return 'easy';
  }

  /**
   * サブカテゴリ判定（より詳細な分類）
   */
  _determineSubcategory(text) {
    const subcategoryMap = {
      '事業者': text.includes('事業者') || text.includes('営業者'),
      '有技者': text.includes('技術者') || text.includes('主任者'),
      '機械的性能': text.includes('機械') || text.includes('仕様'),
      '遊戯球': text.includes('玉') || text.includes('ボール'),
      '交換': text.includes('交換') || text.includes('両替'),
      '出張・移動': text.includes('出張') || text.includes('移動'),
      '雇用・労務': text.includes('雇用') || text.includes('労務'),
      '消費者保護': text.includes('消費者') || text.includes('保護')
    };

    const matches = Object.entries(subcategoryMap)
      .filter(([_, match]) => match)
      .map(([subcategory, _]) => subcategory);

    return matches.length > 0 ? matches[0] : '其他';
  }

  /**
   * 学習進捗分析
   */
  analyzeProgress(answeredQuestions) {
    const categoryStats = {};

    for (const q of answeredQuestions) {
      const category = q.categorization?.mainCategory || '未分類';
      if (!categoryStats[category]) {
        categoryStats[category] = {
          total: 0,
          correct: 0,
          accuracy: 0,
          easyCount: 0,
          mediumCount: 0,
          hardCount: 0
        };
      }

      const stat = categoryStats[category];
      stat.total++;
      if (q.isCorrect) stat.correct++;

      const difficulty = q.categorization?.difficulty || 'medium';
      stat[`${difficulty}Count`]++;

      stat.accuracy = (stat.correct / stat.total * 100).toFixed(1);
    }

    return categoryStats;
  }

  /**
   * 弱点分析・学習推奨
   */
  suggestLearningTopics(answeredQuestions, targetAccuracy = 80) {
    const progress = this.analyzeProgress(answeredQuestions);

    const suggestions = [];
    for (const [category, stats] of Object.entries(progress)) {
      if (stats.accuracy < targetAccuracy) {
        suggestions.push({
          category,
          currentAccuracy: parseFloat(stats.accuracy),
          recommendedFocus: stats.correct < stats.total / 2 ? 'intense' : 'moderate',
          suggestedTopics: this._getTopicsForCategory(category)
        });
      }
    }

    return suggestions.sort((a, b) => a.currentAccuracy - b.currentAccuracy);
  }

  /**
   * カテゴリに対応するトピック取得
   */
  _getTopicsForCategory(category) {
    const topicMap = {
      '総則・定義': ['風営法の目的と定義', '法適用の範囲', '基本用語の説明'],
      '遊技機仕様': ['パチンコ機の構造', 'スロット機の仕様', '検定基準の要点'],
      '遊技料金': ['料金規制', '玉・メダルの交換', '料金管理'],
      '営業所管理': ['営業所の設置', '出張所の管理', '施設基準'],
      '入場管理': ['入場管理の方法', '年齢確認', '不健全客の対応'],
      '現場対応': ['事故報告', '警察との連携', '指導処分対応'],
      '記録・報告': ['帳簿記録', '報告義務', '書類保管'],
      '其の他法律': ['例外規定', '特例措置', '改正法への対応']
    };

    return topicMap[category] || ['基礎知識の復習'];
  }
}

export { QuestionCategorizer };
