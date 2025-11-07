/**
 * Category-Based Scoring Module
 * 遊技機取扱主任者試験の項目別採点機能
 *
 * 4つの主要項目に基づいて採点・分析を実施
 */

/**
 * 5つの主要項目の定義
 */
const EXAM_CATEGORIES = {
  SYSTEM_AND_TEST: {
    id: 'system_and_test',
    name: '制度・試験・資格認定',
    problemRange: [1, 30],
    description: '試験制度、資格認定、講習関連の規程'
  },
  BUSINESS_LAW: {
    id: 'business_law',
    name: '風営法規制と義務',
    problemRange: [[31, 60], [151, 180]],
    description: '風営法に基づく営業者の義務と規制'
  },
  GAME_MACHINE_STANDARDS: {
    id: 'game_machine_standards',
    name: '遊技機規制基準',
    problemRange: [[61, 90], [121, 150]],
    description: '遊技機の技術基準と射幸性基準'
  },
  SUPERVISOR_DUTIES: {
    id: 'supervisor_duties',
    name: '主任者実務と業界要綱',
    problemRange: [[91, 120]],
    description: '取扱主任者の業務と実務スキル'
  },
  FINAL_PROBLEMS: {
    id: 'final_problems',
    name: '最終問題',
    problemRange: [[181, 230]],
    description: '総合的な試験対策問題'
  }
};

/**
 * 問題番号からカテゴリを判定
 */
function getCategoryByProblemId(problemId) {
  for (const [key, category] of Object.entries(EXAM_CATEGORIES)) {
    const ranges = Array.isArray(category.problemRange[0])
      ? category.problemRange
      : [category.problemRange];

    for (const [start, end] of ranges) {
      if (problemId >= start && problemId <= end) {
        return category;
      }
    }
  }
  return null;
}

/**
 * ユーザーの項目別成績を記録
 */
function recordCategoryScore(userId, problemId, isCorrect) {
  const category = getCategoryByProblemId(problemId);
  if (!category) return;

  const scoresKey = `category_scores_${userId}`;
  const scores = JSON.parse(localStorage.getItem(scoresKey) || '{}');

  if (!scores[category.id]) {
    scores[category.id] = {
      categoryId: category.id,
      categoryName: category.name,
      totalAttempts: 0,
      correctAnswers: 0,
      accuracy: 0,
      lastUpdated: null
    };
  }

  scores[category.id].totalAttempts += 1;
  if (isCorrect) {
    scores[category.id].correctAnswers += 1;
  }
  scores[category.id].accuracy =
    (scores[category.id].correctAnswers / scores[category.id].totalAttempts * 100).toFixed(1);
  scores[category.id].lastUpdated = new Date().toISOString();

  localStorage.setItem(scoresKey, JSON.stringify(scores));
}

/**
 * ユーザーの全項目別成績を取得
 */
function getCategoryScores(userId) {
  const scoresKey = `category_scores_${userId}`;
  const scores = JSON.parse(localStorage.getItem(scoresKey) || '{}');

  // カテゴリの順序で並べ替え
  const orderedScores = {};
  Object.values(EXAM_CATEGORIES).forEach(category => {
    if (scores[category.id]) {
      orderedScores[category.id] = scores[category.id];
    } else {
      // 未実施のカテゴリもデフォルト値で追加
      orderedScores[category.id] = {
        categoryId: category.id,
        categoryName: category.name,
        totalAttempts: 0,
        correctAnswers: 0,
        accuracy: 0,
        lastUpdated: null
      };
    }
  });

  return orderedScores;
}

/**
 * 全体成績の集計
 */
function getOverallScore(userId) {
  const scores = getCategoryScores(userId);
  let totalAttempts = 0;
  let totalCorrect = 0;
  const categoryResults = [];

  Object.values(scores).forEach(score => {
    totalAttempts += score.totalAttempts;
    totalCorrect += score.correctAnswers;
    categoryResults.push({
      name: score.categoryName,
      accuracy: score.accuracy,
      total: score.totalAttempts,
      correct: score.correctAnswers
    });
  });

  return {
    totalAttempts,
    totalCorrect,
    overallAccuracy: totalAttempts > 0 ? (totalCorrect / totalAttempts * 100).toFixed(1) : 0,
    categories: categoryResults,
    passedCategories: categoryResults.filter(c => c.accuracy >= 80).length,
    totalCategories: Object.keys(EXAM_CATEGORIES).length
  };
}

/**
 * カテゴリ別の分析レポート生成
 */
function generateCategoryReport(userId) {
  const scores = getCategoryScores(userId);
  const overallScore = getOverallScore(userId);

  const report = {
    userId,
    generatedAt: new Date().toISOString(),
    overallScore,
    categoryDetails: []
  };

  Object.entries(EXAM_CATEGORIES).forEach(([key, category]) => {
    const score = scores[category.id];
    report.categoryDetails.push({
      categoryId: category.id,
      categoryName: category.name,
      description: category.description,
      accuracy: score.accuracy,
      totalProblems: getCategoryProblems(category).length,
      attemptedProblems: score.totalAttempts,
      correctAnswers: score.correctAnswers,
      status: score.accuracy >= 80 ? '合格' : '要学習',
      progressPercentage: score.totalAttempts > 0
        ? ((score.totalAttempts / getCategoryProblems(category).length) * 100).toFixed(1)
        : 0
    });
  });

  return report;
}

/**
 * カテゴリに含まれる問題番号の一覧を取得
 */
function getCategoryProblems(category) {
  const problems = [];
  const ranges = Array.isArray(category.problemRange[0])
    ? category.problemRange
    : [category.problemRange];

  for (const [start, end] of ranges) {
    for (let i = start; i <= end; i++) {
      problems.push(i);
    }
  }

  return problems;
}

/**
 * 弱点カテゴリを特定
 */
function getWeakCategories(userId, threshold = 80) {
  const scores = getCategoryScores(userId);
  const weakCategories = [];

  Object.values(scores).forEach(score => {
    if (score.totalAttempts > 0 && score.accuracy < threshold) {
      weakCategories.push({
        categoryName: score.categoryName,
        accuracy: score.accuracy,
        correctAnswers: score.correctAnswers,
        totalAttempts: score.totalAttempts,
        recommendedProblems: getCategoryProblems(
          Object.values(EXAM_CATEGORIES).find(c => c.id === score.categoryId)
        )
      });
    }
  });

  return weakCategories;
}

/**
 * カテゴリ別の進捗を可視化するデータを生成
 */
function getProgressData(userId) {
  const scores = getCategoryScores(userId);
  const progressData = {
    labels: [],
    datasets: {
      accuracy: [],
      completion: []
    }
  };

  Object.values(EXAM_CATEGORIES).forEach(category => {
    const score = scores[category.id];
    const categoryProblems = getCategoryProblems(category);

    progressData.labels.push(category.name);
    progressData.datasets.accuracy.push(parseFloat(score.accuracy) || 0);
    progressData.datasets.completion.push(
      score.totalAttempts > 0
        ? ((score.totalAttempts / categoryProblems.length) * 100).toFixed(1)
        : 0
    );
  });

  return progressData;
}

/**
 * 項目別成績の履歴をリセット
 */
function clearCategoryScores(userId) {
  const scoresKey = `category_scores_${userId}`;
  localStorage.removeItem(scoresKey);
}

export {
  EXAM_CATEGORIES,
  getCategoryByProblemId,
  recordCategoryScore,
  getCategoryScores,
  getOverallScore,
  generateCategoryReport,
  getCategoryProblems,
  getWeakCategories,
  getProgressData,
  clearCategoryScores
};
