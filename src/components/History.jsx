/**
 * History.jsx - 成績履歴画面
 * 過去の試験結果を表示・分析
 */

import { useState, useEffect } from 'react';
import '../styles/history.css';
import { CATEGORY_NAMES, SHORT_CATEGORY_NAMES } from '../constants/categoryNames';

export function History({ onExit }) {
  // ホーム画面に戻る（ブラウザバック対策：履歴を置き換え）
  const handleExit = () => {
    if (onExit) {
      onExit();
    }
  };
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);

  // 初期化：履歴を読み込み
  useEffect(() => {
    loadHistory();
  }, []);

  /**
   * localStorage から成績履歴を読み込み
   */
  function loadHistory() {
    const data = JSON.parse(localStorage.getItem('examHistory') || '[]');
    setHistory(data);

    // 統計情報を計算
    if (data.length > 0) {
      calculateStats(data);
    }
  }

  /**
   * 統計情報を計算
   */
  function calculateStats(data) {
    const totalExams = data.length;
    const passedExams = data.filter(r => r.passed).length;
    const avgPercentage = Math.round(
      data.reduce((sum, r) => sum + r.percentage, 0) / data.length
    );

    // カテゴリ別の平均スコア
    const categoryAverages = {};
    data.forEach(result => {
      result.categoryStats?.forEach(cat => {
        if (!categoryAverages[cat.category]) {
          categoryAverages[cat.category] = [];
        }
        categoryAverages[cat.category].push(cat.percentage);
      });
    });

    const categoryStats = Object.entries(categoryAverages).map(([category, scores]) => ({
      category,
      avgScore: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
      attempts: scores.length
    }));

    setStats({
      totalExams,
      passedExams,
      passRate: Math.round((passedExams / totalExams) * 100),
      avgPercentage,
      categoryStats
    });
  }

  /**
   * 日付をフォーマット
   */
  function formatDate(isoDate) {
    const date = new Date(isoDate);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
  }

  /**
   * 試験モード名を取得
   */
  function getExamModeName(mode) {
    const names = {
      small: '練習（10問）',
      medium: '更新試験（30問）',
      large: '新規試験（50問）'
    };
    return names[mode] || mode;
  }

  // 履歴がない場合
  if (history.length === 0) {
    return (
      <div className="history-container">
        <div className="history-header">
          <h1>📊 成績履歴</h1>
          <button className="btn-close" onClick={handleExit}>✕</button>
        </div>

        <div className="history-empty">
          <p>成績履歴がまだありません</p>
          <p>チェックを実施して成績を記録しましょう</p>
          <button className="btn btn-primary" onClick={handleExit}>
            ホームに戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      {/* ヘッダー */}
      <div className="history-header">
        <h1>📊 成績履歴</h1>
        <button className="btn-close" onClick={handleExit}>✕</button>
      </div>

      <div className="history-content">
        {/* 統計サマリー */}
        {stats && (
          <div className="history-summary">
            <h2>📈 これまでの実績</h2>

            <div className="summary-grid">
              <div className="summary-card">
                <div className="summary-label">総試験回数</div>
                <div className="summary-value">{stats.totalExams}</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">合格回数</div>
                <div className="summary-value passed">{stats.passedExams}</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">合格率</div>
                <div className="summary-value">{stats.passRate}%</div>
              </div>

              <div className="summary-card">
                <div className="summary-label">平均スコア</div>
                <div className="summary-value">{stats.avgPercentage}%</div>
              </div>
            </div>

            {/* カテゴリ別統計 */}
            <div className="category-stats">
              <h3>カテゴリ別平均スコア</h3>
              <div className="category-list">
                {stats.categoryStats.map(cat => (
                  <div key={cat.category} className="category-item">
                    <div className="cat-name">
                      <span className="full-name">{CATEGORY_NAMES[cat.category] || cat.category}</span>
                      <span className="short-name">{SHORT_CATEGORY_NAMES[cat.category] || cat.category}</span>
                    </div>
                    <div className="cat-bar">
                      <div
                        className="cat-fill"
                        style={{ width: `${cat.avgScore}%` }}
                      ></div>
                    </div>
                    <div className="cat-score">
                      {cat.avgScore}% ({cat.attempts}回)
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 成績一覧 */}
        <div className="history-list">
          <h2>🕐 試験履歴</h2>

          {history.map((result, index) => (
            <div
              key={result.id}
              className={`history-item ${result.passed ? 'passed' : 'failed'}`}
              onClick={() => setSelectedResult(selectedResult?.id === result.id ? null : result)}
            >
              {/* サマリー */}
              <div className="item-summary">
                <div className="item-number">#{history.length - index}</div>

                <div className="item-info">
                  <div className="item-date">{formatDate(result.date)}</div>
                  <div className="item-mode">{getExamModeName(result.examMode)}</div>
                </div>

                <div className="item-score">
                  <div className={`score-circle ${result.passed ? 'pass' : 'fail'}`}>
                    {result.percentage}%
                  </div>
                  <div className="score-label">
                    {result.passed ? '✓ 合格' : '✗ 不合格'}
                  </div>
                </div>

                <div className="item-details">
                  {result.correctAnswers}/{result.totalQuestions}問正解
                </div>

                <div className="item-arrow">
                  {selectedResult?.id === result.id ? '▼' : '▶'}
                </div>
              </div>

              {/* 詳細表示 */}
              {selectedResult?.id === result.id && (
                <div className="item-detail">
                  <div className="detail-header">
                    <h4>カテゴリ別成績</h4>
                  </div>

                  <div className="detail-categories">
                    {result.categoryStats.map(cat => (
                      <div key={cat.category} className="detail-category">
                        <span className="cat-name">{CATEGORY_NAMES[cat.category] || cat.category}</span>
                        <span className="cat-score">
                          {cat.correct}/{cat.total} ({cat.percentage}%)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* アクション */}
        <div className="history-actions">
          <button className="btn btn-secondary" onClick={handleExit}>
            ホームに戻る
          </button>
        </div>
      </div>
    </div>
  );
}
