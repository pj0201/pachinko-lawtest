import '../styles/ResultPage.css'
import { getCategoryScores, getOverallScore, getWeakCategories } from '../utils/categoryScoring'

export default function ResultPage({ results, onReturnHome }) {
  if (!results) return null

  // ユーザーID取得
  const userId = localStorage.getItem('userId') || 'guest_' + Date.now()

  // カテゴリ別スコアを取得
  const categoryScores = getCategoryScores(userId)
  const overallScore = getOverallScore(userId)
  const weakCategories = getWeakCategories(userId, 80)

  // カテゴリ名マッピング
  const categoryNames = {
    system_and_test: '制度・試験・資格認定',
    business_law: '風営法規制と義務',
    game_machine_standards: '遊技機規制基準',
    supervisor_duties: '主任者実務と業界要綱',
    final_problems: '最終問題'
  }

  const categories = Object.keys(categoryScores)

  return (
    <div className="result-page">
      <div className="result-header">
        {results.isPassed ? (
          <div className="result-badge passed">🎉 合格</div>
        ) : (
          <div className="result-badge failed">もう一度チャレンジ</div>
        )}
        <h2>テスト完了</h2>
      </div>

      <div className="result-content">
        <div className="score-card">
          <div className="main-score">
            <span className="label">正解数</span>
            <span className="value">
              {results.correctCount} / {results.totalCount}
            </span>
          </div>
          <div className="percentage">
            <span className={results.isPassed ? 'passed' : 'failed'}>
              {results.percentage}%
            </span>
          </div>
        </div>

        <div className="category-scores">
          <h3>📊 カテゴリー別成績</h3>
          {categories.map(categoryId => {
            const score = categoryScores[categoryId]
            const percentage = score.totalAttempts > 0 ? parseInt(score.accuracy) : 0
            const categoryName = categoryNames[categoryId] || categoryId

            return (
              <div key={categoryId} className="category-item">
                <div className="category-name">{categoryName}</div>
                <div className="category-stats">
                  <span className="attempt-count">{score.correctAnswers}/{score.totalAttempts} 正解</span>
                </div>
                <div className="category-chart">
                  <div className="bar-container">
                    <div
                      className={`bar-fill ${percentage >= 80 ? 'passed' : 'failed'}`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className={`percentage ${percentage >= 80 ? 'passed' : 'failed'}`}>
                    {percentage}%
                  </div>
                </div>
                {percentage >= 80 ? (
                  <div className="status">✅ 合格</div>
                ) : (
                  <div className="status">⚠️ 要学習</div>
                )}
              </div>
            )
          })}
        </div>

        <div className="feedback">
          <h3>📈 分析結果</h3>
          <div className="overall-stats">
            <p><strong>総合成績:</strong> {overallScore.overallAccuracy}% ({overallScore.totalCorrect}/{overallScore.totalAttempts} 正解)</p>
            <p><strong>合格状況:</strong> {overallScore.passedCategories}/{overallScore.totalCategories} カテゴリ合格</p>
          </div>

          {overallScore.overallAccuracy >= 80 ? (
            <p className="positive-feedback">🎉 素晴らしい成績です！試験合格の可能性が高いです。</p>
          ) : (
            <p className="negative-feedback">📚 弱点を分析して、さらに学習を進めてください。</p>
          )}

          {weakCategories.length > 0 && (
            <div className="weak-categories-section">
              <h4>⚠️ 学習が必要な項目</h4>
              <ul className="weak-list">
                {weakCategories.map((category, idx) => (
                  <li key={idx}>
                    <span>{category.categoryName}</span>
                    <span className="accuracy">{category.accuracy}% ({category.correctAnswers}/{category.totalAttempts})</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="result-footer">
        <button className="primary-btn" onClick={onReturnHome}>
          🔄 ホームに戻る
        </button>
        <button className="secondary-btn">🎯 弱点特化テスト</button>
      </div>
    </div>
  )
}
