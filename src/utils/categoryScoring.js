/**
 * Category-Based Scoring Module
 * 遊技機取扱主任者試験の項目別採点機能
 *
 * 4つの主要項目に基づいて採点・分析を実施
 */

/**
 * 5つの主要項目の定義（2025-11-08 再構築版）
 */
const EXAM_CATEGORIES = {
  QUALIFICATION_SYSTEM: {
    id: 'qualification_system',
    name: '遊技機取扱主任者制度と資格維持',
    problemRange: [1, 30],
    description: '資格の維持、試験、講習、欠格事由など、主任者資格に関わる規定',
    totalProblems: 30
  },
  GAME_MACHINE_TECHNICAL_STANDARDS: {
    id: 'game_machine_technical_standards',
    name: '遊技機規制技術基準（射幸性・技術）',
    problemRange: [[61, 90], [121, 150], [181, 190], [206, 206], [207, 207], [212, 212], [213, 213], [215, 215]],
    description: '射幸性、技術基準、獲得枚数/球数などの専門的な技術知識',
    totalProblems: 90
  },
  SUPERVISOR_DUTIES_AND_GUIDANCE: {
    id: 'supervisor_duties_and_guidance',
    name: '主任者の実務、指導及び業界要綱',
    problemRange: [[91, 120], [208, 208], [209, 209]],
    description: '主任者の業務、書類確認、保守管理、指導監督義務',
    totalProblems: 32
  },
  BUSINESS_REGULATION_AND_OBLIGATIONS: {
    id: 'business_regulation_and_obligations',
    name: '風俗営業の一般規制と義務',
    problemRange: [[31, 60], [151, 180], [220, 220], [226, 226], [227, 227]],
    description: '風営法の総則、定義、遊技料金、禁止行為などの基本的な法的義務',
    totalProblems: 63
  },
  ADMINISTRATIVE_PROCEDURES_AND_PENALTIES: {
    id: 'administrative_procedures_and_penalties',
    name: '行政手続、構造基準及び罰則',
    problemRange: [[191, 192], [199, 200], [204, 205], [210, 211], [214, 214], [216, 217], [219, 219], [223, 225], [228, 229]],
    description: '申請期限、構造基準、照度測定、帳簿細則、罰則',
    totalProblems: 17
  }
};

/**
 * 問題番号からカテゴリを判定
 */
function getCategoryByProblemId(problemId) {
  for (const [key, category] of Object.entries(EXAM_CATEGORIES)) {
    // problemRange が単純な配列 [start, end] か複合範囲 [[start, end], ...] かを判定
    let ranges;
    if (Array.isArray(category.problemRange[0])) {
      ranges = category.problemRange;
    } else {
      ranges = [category.problemRange];
    }

    // 各範囲で問題IDをチェック
    for (const range of ranges) {
      const [start, end] = range;
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
