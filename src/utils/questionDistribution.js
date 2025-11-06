/**
 * Smart Question Distribution Module
 * Manages question selection to avoid duplicates for the same account
 *
 * Features:
 * - Tracks which questions user has already attempted
 * - Ensures no duplicate questions in same session
 * - Provides smart filtering based on user history and difficulty
 */

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
  getAttemptStatistics,
  clearQuestionHistory
};
