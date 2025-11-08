/**
 * Smart Question Distribution Module
 * Manages question selection to avoid duplicates for the same account
 *
 * Features:
 * - Tracks which questions user has already attempted
 * - Ensures no duplicate questions in same session
 * - Provides smart filtering based on user history and difficulty
 * - Supports new 5-category system (2025-11-08)
 */

// カテゴリ別問題配分設定
const DIFFICULTY_DISTRIBUTION = {
  easy: {
    // 易: 主任者制度30%、営業規制40%、その他30%
    qualification_system: { range: [1, 30], weight: 0.3 },
    business_regulation_and_obligations: { range: [[31, 60], [151, 180], [220, 220], [226, 226], [227, 227]], weight: 0.4 },
    other: { weight: 0.3 }
  },
  medium: {
    // 中: 技術基準40%、実務指導30%、その他30%
    game_machine_technical_standards: { range: [[61, 90], [121, 150], [181, 190], [206, 206], [207, 207], [212, 212], [213, 213], [215, 215]], weight: 0.4 },
    supervisor_duties_and_guidance: { range: [[91, 120], [208, 208], [209, 209]], weight: 0.3 },
    other: { weight: 0.3 }
  },
  hard: {
    // 難: 技術基準50%、行政手続30%、その他20%
    game_machine_technical_standards: { range: [[61, 90], [121, 150], [181, 190], [206, 206], [207, 207], [212, 212], [213, 213], [215, 215]], weight: 0.5 },
    administrative_procedures_and_penalties: { range: [[191, 192], [199, 200], [204, 205], [210, 211], [214, 214], [216, 217], [219, 219], [223, 225], [228, 229]], weight: 0.3 },
    other: { weight: 0.2 }
  }
};

/**
 * Generate a unique key for user account
 * Combines device ID and user info to create account identifier
 */
function getUserAccountKey() {
  const deviceId = localStorage.getItem('device_id');
  const sessionToken = localStorage.getItem('session_token');
  return `${deviceId}-${sessionToken}`;
}

/**
 * Get user's question history (list of problem IDs already attempted)
 */
function getUserQuestionHistory() {
  const accountKey = getUserAccountKey();
  const historyKey = `question_history_${accountKey}`;
  const history = JSON.parse(localStorage.getItem(historyKey) || '[]');
  return history; // Array of problem IDs
}

/**
 * Add a question to user's history after completion
 */
function recordQuestionAttempt(problemId) {
  const accountKey = getUserAccountKey();
  const historyKey = `question_history_${accountKey}`;
  const history = getUserQuestionHistory();

  if (!history.includes(problemId)) {
    history.push(problemId);
    localStorage.setItem(historyKey, JSON.stringify(history));
  }
}

/**
 * Get smart question distribution statistics per user
 */
function getQuestionDistributionStats() {
  const accountKey = getUserAccountKey();
  const statsKey = `question_stats_${accountKey}`;
  const stats = JSON.parse(localStorage.getItem(statsKey) || '{}');
  return stats;
}

/**
 * Record question performance to distribution stats
 */
function recordQuestionPerformance(problemId, correct) {
  const accountKey = getUserAccountKey();
  const statsKey = `question_stats_${accountKey}`;
  const stats = getQuestionDistributionStats();

  if (!stats[problemId]) {
    stats[problemId] = { attempts: 0, correct: 0, lastAttempt: null };
  }

  stats[problemId].attempts += 1;
  if (correct) stats[problemId].correct += 1;
  stats[problemId].lastAttempt = new Date().toISOString();

  localStorage.setItem(statsKey, JSON.stringify(stats));
}

/**
 * Filter questions to exclude user's history
 * @param {Array} allProblems - All available questions
 * @param {number} count - Number of questions to select
 * @param {Object} options - Selection options {difficulty, category, excludeRecent}
 * @returns {Array} - Selected questions that user hasn't seen before
 */
function selectSmartQuestions(allProblems, count = 10, options = {}) {
  const history = getUserQuestionHistory();
  const stats = getQuestionDistributionStats();

  // Filter out already attempted questions
  let availableQuestions = allProblems.filter(
    q => !history.includes(q.problem_id)
  );

  // If not enough new questions, allow retakes of least recently attempted
  if (availableQuestions.length < count) {
    const retakeThreshold = 7; // Days before allowing same question again
    const now = new Date();

    const retakeCandidates = allProblems.filter(q => {
      const stat = stats[q.problem_id];
      if (!stat || !stat.lastAttempt) return true;

      const lastAttempt = new Date(stat.lastAttempt);
      const daysDiff = (now - lastAttempt) / (1000 * 60 * 60 * 24);
      return daysDiff >= retakeThreshold;
    });

    availableQuestions = availableQuestions.concat(retakeCandidates);
  }

  // Sort by difficulty if specified
  if (options.difficulty) {
    availableQuestions = availableQuestions.sort((a, b) => {
      const difficultyOrder = { easy: 0, medium: 1, hard: 2 };
      const aDiff = difficultyOrder[a.difficulty] || 1;
      const bDiff = difficultyOrder[b.difficulty] || 1;
      return aDiff - bDiff;
    });
  }

  // Filter by category if specified
  if (options.category) {
    availableQuestions = availableQuestions.filter(
      q => q.theme_name === options.category
    );
  }

  // Shuffle and select requested count
  availableQuestions = availableQuestions.sort(() => Math.random() - 0.5);
  return availableQuestions.slice(0, count);
}

/**
 * Get statistics about user's question attempts
 */
function getAttemptStatistics() {
  const history = getUserQuestionHistory();
  const stats = getQuestionDistributionStats();

  let totalAttempts = 0;
  let totalCorrect = 0;

  Object.values(stats).forEach(stat => {
    totalAttempts += stat.attempts || 0;
    totalCorrect += stat.correct || 0;
  });

  return {
    uniqueQuestionsAttempted: history.length,
    totalAttempts,
    totalCorrect,
    accuracy: totalAttempts > 0 ? (totalCorrect / totalAttempts * 100).toFixed(1) : 0,
    questionStats: stats
  };
}

/**
 * Select questions based on difficulty distribution (新カテゴリ対応版)
 * @param {Array} allProblems - All available questions
 * @param {number} count - Number of questions to select
 * @param {string} difficulty - Difficulty level ('easy', 'medium', 'hard')
 * @returns {Array} - Selected questions based on difficulty distribution
 */
function selectQuestionsByDifficulty(allProblems, count = 10, difficulty = 'medium') {
  const distribution = DIFFICULTY_DISTRIBUTION[difficulty] || DIFFICULTY_DISTRIBUTION.medium;
  const selectedQuestions = [];

  // カテゴリごとの問題数を計算
  const categoryQuestions = {};

  for (const [category, config] of Object.entries(distribution)) {
    if (category === 'other') continue;

    const questionCount = Math.floor(count * config.weight);
    const ranges = Array.isArray(config.range[0]) ? config.range : [config.range];

    // 該当範囲の問題を選択
    const categoryProblems = allProblems.filter(q => {
      const problemId = q.problem_id;
      return ranges.some(([start, end]) => problemId >= start && problemId <= end);
    });

    // ランダムに選択
    const shuffled = categoryProblems.sort(() => Math.random() - 0.5);
    selectedQuestions.push(...shuffled.slice(0, questionCount));
  }

  // その他カテゴリから残りを補充
  const otherWeight = distribution.other?.weight || 0;
  if (otherWeight > 0) {
    const remainingCount = count - selectedQuestions.length;
    const selectedIds = new Set(selectedQuestions.map(q => q.problem_id));
    const otherProblems = allProblems
      .filter(q => !selectedIds.has(q.problem_id))
      .sort(() => Math.random() - 0.5);
    selectedQuestions.push(...otherProblems.slice(0, remainingCount));
  }

  // 最終的にシャッフル
  return selectedQuestions.sort(() => Math.random() - 0.5).slice(0, count);
}

/**
 * Clear question history (for testing or admin purposes)
 */
function clearQuestionHistory() {
  const accountKey = getUserAccountKey();
  localStorage.removeItem(`question_history_${accountKey}`);
  localStorage.removeItem(`question_stats_${accountKey}`);
}

export {
  getUserAccountKey,
  getUserQuestionHistory,
  recordQuestionAttempt,
  getQuestionDistributionStats,
  recordQuestionPerformance,
  selectSmartQuestions,
  selectQuestionsByDifficulty,
  getAttemptStatistics,
  clearQuestionHistory,
  DIFFICULTY_DISTRIBUTION
};
