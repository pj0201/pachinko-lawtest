/**
 * ExamScreen.jsx - 模擬試験画面（スマホ用）
 * 問題表示・回答・結果管理
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/exam.css';
import {
  recordQuestionAttempt,
  recordQuestionPerformance,
  getAttemptStatistics
} from '../utils/questionDistribution';
import {
  recordCategoryScore,
  getCategoryScores,
  getOverallScore,
  generateCategoryReport,
  getWeakCategories
} from '../utils/categoryScoring';

// カテゴリ名のマッピング（2025-11-08 再構築版 - 1行表示 + 古いID対応）
const CATEGORY_NAMES = {
  'qualification_system': '遊技機取扱主任者制度と資格維持',
  'game_machine_technical_standards': '遊技機規制技術基準（射幸性・技術）',
  'supervisor_duties_and_guidance': '主任者の実務、指導及び業界要綱',
  'business_regulation_and_obligations': '風俗営業の一般規制と義務',
  'administrative_procedures_and_penalties': '行政手続、構造基準及び罰則',
  // 古いカテゴリIDも対応（ローカルストレージ互換性）
  'system_and_test': '遊技機取扱主任者制度と資格維持',
  'business_law': '風俗営業の一般規制と義務',
  'game_machine_standards': '遊技機規制技術基準（射幸性・技術）',
  'supervisor_duties': '主任者の実務、指導及び業界要綱',
  'final_problems': '行政手続、構造基準及び罰則'
};

export function ExamScreen({ examMode, onExit }) {
  const navigate = useNavigate();

  const [problems, setProblems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // { problemId: true/false }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [resultSaved, setResultSaved] = useState(false); // 成績保存済みフラグ
  const [difficultyLevel, setDifficultyLevel] = useState(null); // 難易度選択待ち

  // ホーム画面に戻る（中断確認ダイアログ付き）
  const handleExit = () => {
    // 結果表示画面なら確認なしで戻る
    if (showResults || resultSaved) {
      if (onExit) {
        onExit();
      } else {
        navigate('/', { replace: true });
      }
      return;
    }

    // 試験中なら確認ダイアログ
    if (window.confirm('テストを中断しますか？\n途中結果は保存されません。')) {
      if (onExit) {
        onExit();
      } else {
        navigate('/', { replace: true });
      }
    }
  };

  // 試験問題数を決定
  const totalQuestions = {
    small: 10,
    medium: 30,
    large: 50
  }[examMode] || 10;

  /**
   * 難易度選択後に問題をロード
   * バックエンド Flask API (/api/problems/quiz) から取得
   */
  const loadProblems = useCallback(async () => {
    try {
      console.log('🔄 loadProblems 関数開始');
      console.log(`📋 difficultyLevel: ${difficultyLevel}, totalQuestions: ${totalQuestions}`);

      setLoading(true);

      // バックエンド API のベース URL（相対パスで、プロキシ経由でアクセス）
      const API_BASE = '';  // 空文字列 = 相対パス（/api/...）
      console.log(`🌐 API_BASE: ${API_BASE}（相対パス）`);

      // 難易度をバックエンド形式に変換（★/★★/★★★）
      const difficultyMap = {
        'low': '★',           // 易しい
        'medium': '★★',       // 普通
        'high': '★★★'        // 難しい
      };

      const selectedDifficulty = difficultyMap[difficultyLevel];
      console.log(`⭐ 難易度マップ: ${difficultyLevel} → ${selectedDifficulty}`);

      // API リクエスト
      const requestBody = {
        count: totalQuestions,
        difficulty: selectedDifficulty
      };
      console.log(`📤 API リクエストボディ:`, requestBody);

      const response = await fetch(`${API_BASE}/api/problems/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📥 API レスポンスステータス: ${response.status}`);

      if (!response.ok) {
        throw new Error(`API エラー: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`📊 API レスポンスデータ:`, data);

      let allProblems = data.problems || [];
      console.log(`📚 取得した問題数: ${allProblems.length}`);

      if (allProblems.length === 0) throw new Error('問題データが空です');

      console.log(`✅ バックエンドから ${allProblems.length} 問を取得しました`);

      // ✅ バックエンドが要求数正確に返すため、selectSmartQuestions は不要（削減防止）

      // バックエンドのデータをフロントエンドの形式に変換
      console.log(`🔄 ${allProblems.length} 個の問題を変換開始...`);

      const convertedProblems = allProblems.map((problem, index) => {
        // 難易度を変換
        const difficultyMap = {
          '★': 'easy',
          '★★': 'medium',
          '★★★': 'hard',
          '★★★★': 'hard'
        };

        // 正答を boolean に変換
        const answer = problem.correct_answer === '○' || problem.correct_answer === true;

        // 法律参照を文字列に変換
        let lawReference = '';
        if (problem.legal_reference) {
          if (typeof problem.legal_reference === 'string') {
            lawReference = problem.legal_reference;
          } else if (typeof problem.legal_reference === 'object') {
            const lr = problem.legal_reference;
            lawReference = `${lr.law || ''} ${lr.article || ''} ${lr.section || ''}`.trim();
          }
        }

        const converted = {
          // 1. 問題ID
          id: problem.problem_id,

          // 2. 問題文
          statement: problem.problem_text,

          // 3. 正答（boolean）
          answer: answer,

          // 4. 解説
          explanation: problem.explanation,

          // 5. カテゴリ
          category: problem.category,

          // 6. 難易度
          difficulty: difficultyMap[problem.difficulty] || 'medium',

          // 7. 法律参照
          lawReference: lawReference,

          // 8. パターン名
          pattern: problem.pattern_name,

          // 9. テーマ名
          theme: problem.theme_name
        };

        // 最初の問題をデバッグ出力
        if (index === 0) {
          console.log(`【問題1のフィールド確認】`);
          console.log(`  1️⃣  id: ${converted.id}`);
          console.log(`  2️⃣  statement: ${converted.statement?.substring(0, 30)}...`);
          console.log(`  3️⃣  answer: ${converted.answer}`);
          console.log(`  4️⃣  explanation: ${converted.explanation?.substring(0, 30)}...`);
          console.log(`  5️⃣  category: ${converted.category}`);
          console.log(`  6️⃣  difficulty: ${converted.difficulty}`);
          console.log(`  7️⃣  lawReference: ${converted.lawReference}`);
          console.log(`  8️⃣  pattern: ${converted.pattern}`);
          console.log(`  9️⃣  theme: ${converted.theme}`);
        }

        return converted;
      });

      setProblems(convertedProblems);
      setError(null);
    } catch (err) {
      console.error('❌ 問題ロードエラー:', err);
      setError(err.message);
      setProblems([]);
    } finally {
      setLoading(false);
    }
  }, [difficultyLevel, totalQuestions]);

  /**
   * 難易度が選択されたときに自動的に問題をロード
   */
  useEffect(() => {
    if (difficultyLevel) {
      loadProblems();
    }
  }, [difficultyLevel, loadProblems]);

  // 成績を保存（showResults が true になった時点で一度だけ）
  useEffect(() => {
    if (showResults && !resultSaved && problems.length > 0) {
      const score = calculateScore();
      const categoryStats = getCategoryStats(problems, answers);
      const result = {
        id: `exam_${Date.now()}`,
        date: new Date().toISOString(),
        examMode: examMode,
        totalQuestions: problems.length,
        correctAnswers: score.correct,
        percentage: score.percentage,
        passed: score.percentage >= 80,
        categoryStats: categoryStats
      };

      let history = JSON.parse(localStorage.getItem('examHistory') || '[]');

      const resultDate = new Date(result.date);
      const resultSecond = Math.floor(resultDate.getTime() / 1000);

      const isDuplicate = history.some(h => {
        const historyDate = new Date(h.date);
        const historySecond = Math.floor(historyDate.getTime() / 1000);

        return (
          historySecond === resultSecond &&
          h.examMode === result.examMode &&
          h.correctAnswers === result.correctAnswers &&
          h.percentage === result.percentage
        );
      });

      if (!isDuplicate) {
        history.push(result);

        if (history.length > 50) {
          history = history.slice(-50);
        }

        localStorage.setItem('examHistory', JSON.stringify(history));
        console.log('✅ 成績を保存しました:', result);
        console.log('📊 現在の履歴数:', history.length);
      } else {
        console.warn('⚠️ 重複する成績を検出したため、保存をスキップしました');
      }

      setResultSaved(true);
    }
  }, [showResults, resultSaved, problems.length, examMode, answers]);

  /**
   * 回答を記録
   */
  function handleAnswer(answer) {
    const problemId = problems[currentIndex].id;
    const isCorrect = answer === problems[currentIndex].answer;

    setAnswers({
      ...answers,
      [problemId]: answer
    });

    // 【スマート質問分配への記録】回答結果をローカル履歴に記録
    recordQuestionPerformance(problemId, isCorrect);
    console.log(`📊 問題${problemId}の結果を記録: ${isCorrect ? '✅正解' : '❌不正解'}`);

    // 次の問題へ（または結果表示へ）
    if (currentIndex < problems.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResults(true);
    }
  }

  /**
   * 結果を計算
   */
  function calculateScore() {
    let correct = 0;
    const userId = localStorage.getItem('userId') || 'guest_' + Date.now();

    // 各問題の採点とカテゴリ別スコア記録
    problems.forEach(problem => {
      const isCorrect = answers[problem.id] === problem.answer;
      if (isCorrect) {
        correct++;
      }

      // カテゴリ別採点を記録
      // problem.problem_id が問題番号、カテゴリ判定はcategoryScoring.jsで行われる
      recordCategoryScore(userId, problem.problem_id || parseInt(problem.id), isCorrect);
    });

    return {
      correct,
      total: problems.length,
      percentage: Math.round((correct / problems.length) * 100)
    };
  }

  /**
   * 前の問題へ
   */
  function handlePrevious() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  }

  /**
   * 次の問題へ（確認なしジャンプ）
   */
  function handleNext() {
    if (currentIndex < problems.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }

  /**
   * 試験をリセット
   */
  function handleRetry() {
    setCurrentIndex(0);
    setAnswers({});
    setShowResults(false);
    setResultSaved(false);
    setDifficultyLevel(null); // 難易度選択画面に戻す
  }

  // 難易度選択中
  if (!difficultyLevel) {
    return (
      <div className="exam-container">
        <div className="difficulty-selector">
          <h2>🎯 難易度を選択してください</h2>
          <p className="intro-text">テスト開始前に難易度を選択します</p>

          <div className="difficulty-buttons">
            <button
              className="difficulty-btn low"
              onClick={() => setDifficultyLevel('low')}
            >
              <span className="level">低</span>
              <span className="num-questions">10問</span>
            </button>

            <button
              className="difficulty-btn medium"
              onClick={() => setDifficultyLevel('medium')}
            >
              <span className="level">中</span>
              <span className="num-questions">30問</span>
            </button>

            <button
              className="difficulty-btn high"
              onClick={() => setDifficultyLevel('high')}
            >
              <span className="level">高</span>
              <span className="num-questions">50問</span>
            </button>
          </div>

          <button className="cancel-btn" onClick={handleExit}>キャンセル</button>
        </div>
      </div>
    );
  }

  // ローディング中
  if (loading) {
    return (
      <div className="exam-container">
        <div className="exam-loading">
          <div className="spinner"></div>
          <p>問題を読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラー
  if (error) {
    return (
      <div className="exam-container">
        <div className="exam-error">
          <h2>⚠️ エラー</h2>
          <p>{error}</p>
          <button onClick={() => handleExit()}>ホームに戻る</button>
        </div>
      </div>
    );
  }

  // 問題がない
  if (problems.length === 0) {
    return (
      <div className="exam-container">
        <div className="exam-error">
          <h2>⚠️ 問題が見つかりません</h2>
          <p>問題データが利用できません</p>
          <button onClick={() => handleExit()}>ホームに戻る</button>
        </div>
      </div>
    );
  }

  // 結果表示
  if (showResults) {
    const score = calculateScore();
    const passingScore = Math.ceil(problems.length * 0.8); // 80%合格

    return (
      <div className="exam-container">
        <div className="exam-results">
          <div className="results-header">
            <h1>試験結果</h1>
          </div>

          <div className="results-content">
            <div className="score-display">
              <div className={`score-circle ${score.percentage >= 80 ? 'pass' : 'fail'}`}>
                <div className="score-percent">{score.percentage}%</div>
              </div>

              <div className="score-details">
                <h2>{score.percentage >= 80 ? '🎉 合格!' : '❌ 不合格'}</h2>
                <p>正答率: {score.correct}/{score.total}</p>
                <p>合格ライン: {passingScore}問以上（80%）</p>
              </div>
            </div>

            <div className="results-breakdown">
              <h3>カテゴリ別成績</h3>
              <div className="category-stats">
                {/* カテゴリ別集計 */}
                {getCategoryStats(problems, answers).map(cat => (
                  <div key={cat.category} className="category-stat">
                    <span className="cat-name">{CATEGORY_NAMES[cat.category] || cat.category}</span>
                    <span className="cat-score">
                      {cat.correct}/{cat.total} ({cat.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="results-review">
              <h3>問題の確認</h3>
              <div className="review-list">
                {problems.map((problem, idx) => {
                  const isCorrect = answers[problem.id] === problem.answer;
                  const answered = answers[problem.id] !== undefined;

                  return (
                    <div
                      key={problem.id}
                      className={`review-item ${isCorrect ? 'correct' : 'incorrect'} ${!answered ? 'unanswered' : ''}`}
                    >
                      <div className="review-header">
                        <span className="question-num">問{idx + 1}</span>
                        <span className="review-status">
                          {!answered && '未回答'}
                          {answered && isCorrect && '✓ 正解'}
                          {answered && !isCorrect && '✗ 不正解'}
                        </span>
                      </div>
                      <p className="review-statement">{problem.statement}</p>
                      <div className="review-answers">
                        <div className="user-answer">
                          <strong>あなたの回答:</strong>
                          {answered ? (answers[problem.id] ? '○ 正しい' : '× 誤り') : '未回答'}
                        </div>
                        <div className="correct-answer">
                          <strong>正答:</strong>
                          {problem.answer ? '○ 正しい' : '× 誤り'}
                        </div>
                      </div>
                      {problem.explanation && (
                        <div className="review-explanation">
                          <strong>解説:</strong>
                          <p>{problem.explanation}</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="results-actions">
              <button className="btn btn-primary" onClick={handleRetry}>
                もう一度解く
              </button>
              <button className="btn btn-secondary" onClick={() => handleExit()}>
                ホームに戻る
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 問題表示
  const currentProblem = problems[currentIndex];
  const isAnswered = answers[currentProblem.id] !== undefined;
  const selectedAnswer = answers[currentProblem.id];

  return (
    <div className="exam-container">
      <div className="exam-header">
        <div className="exam-title">
          <h1>🎰 風営法理解度チェック</h1>
          <p>{examMode === 'small' ? '練習用' : examMode === 'medium' ? '標準版' : '完全版'}</p>
        </div>

        <div className="exam-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${((currentIndex + 1) / problems.length) * 100}%`
              }}
            ></div>
          </div>
          <p className="progress-text">
            {currentIndex + 1}/{problems.length}問
          </p>
        </div>

        <button className="btn-close" onClick={() => handleExit()}>
          ✕
        </button>
      </div>

      <div className="exam-content">
        <div className="problem-card">
          {/* 問題文 */}
          <div className="problem-header">
            <h2>問題 {currentIndex + 1}</h2>
            <span className="problem-category">{CATEGORY_NAMES[currentProblem.category] || currentProblem.category}</span>
            <span className={`problem-difficulty difficulty-${currentProblem.difficulty}`}>
              {currentProblem.difficulty === 'easy' && '易'}
              {currentProblem.difficulty === 'medium' && '中'}
              {currentProblem.difficulty === 'hard' && '難'}
            </span>
          </div>

          <div className="problem-statement">
            <p>{currentProblem.statement}</p>
          </div>

          {/* 回答ボタン */}
          <div className="problem-answers">
            <button
              className={`answer-btn ${selectedAnswer === true ? 'selected' : ''} ${
                selectedAnswer === true && isAnswered ? (selectedAnswer === currentProblem.answer ? 'correct' : 'incorrect') : ''
              }`}
              onClick={() => handleAnswer(true)}
              disabled={isAnswered}
            >
              <span className="answer-label">○ 正しい</span>
              <span className="answer-desc">True</span>
            </button>

            <button
              className={`answer-btn ${selectedAnswer === false ? 'selected' : ''} ${
                selectedAnswer === false && isAnswered ? (selectedAnswer === currentProblem.answer ? 'correct' : 'incorrect') : ''
              }`}
              onClick={() => handleAnswer(false)}
              disabled={isAnswered}
            >
              <span className="answer-label">× 誤り</span>
              <span className="answer-desc">False</span>
            </button>
          </div>

          {/* 解説 */}
          {isAnswered && currentProblem.explanation && (
            <div className={`problem-explanation ${selectedAnswer === currentProblem.answer ? 'correct' : 'incorrect'}`}>
              <h4>
                {selectedAnswer === currentProblem.answer ? '✓ 正解!' : '✗ 不正解'}
              </h4>
              <p>{currentProblem.explanation}</p>
              {currentProblem.lawReference && (
                <p className="law-ref">参考: {currentProblem.lawReference}</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="exam-footer">
        <div className="exam-navigation">
          <button
            className="btn btn-secondary"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
          >
            ← 前へ
          </button>

          {!isAnswered && (
            <p className="nav-hint">回答を選択してください</p>
          )}

          {isAnswered && currentIndex < problems.length - 1 && (
            <button className="btn btn-primary" onClick={handleNext}>
              次へ →
            </button>
          )}

          {isAnswered && currentIndex === problems.length - 1 && (
            <button className="btn btn-success" onClick={() => setShowResults(true)}>
              結果を見る →
            </button>
          )}
        </div>

        <div className="exam-answered-count">
          回答済み: {Object.keys(answers).length}/{problems.length}問
        </div>
      </div>
    </div>
  );
}

/**
 * カテゴリ別の成績を計算
 */
function getCategoryStats(problems, answers) {
  const categories = {};

  problems.forEach(problem => {
    const cat = problem.category;
    if (!categories[cat]) {
      categories[cat] = { correct: 0, total: 0 };
    }

    categories[cat].total++;

    if (answers[problem.id] === problem.answer) {
      categories[cat].correct++;
    }
  });

  return Object.entries(categories).map(([category, stats]) => ({
    category,
    correct: stats.correct,
    total: stats.total,
    percentage: Math.round((stats.correct / stats.total) * 100)
  }));
}
