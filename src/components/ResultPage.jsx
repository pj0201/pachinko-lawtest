import '../styles/ResultPage.css'

export default function ResultPage({ results, onReturnHome }) {
  if (!results) return null

  const getCategoryPercentage = (category) => {
    const score = results.categoryScores[category]
    const count = results.categoryCounts[category]
    return count > 0 ? Math.round((score / count) * 100) : 0
  }

  const categories = ['法律知識', '営業管理', '機械知識']

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
          <h3>カテゴリー別成績</h3>
          {categories.map(category => {
            const percentage = getCategoryPercentage(category)
            return (
              <div key={category} className="category-item">
                <div className="category-name">{category}</div>
                <div className="category-chart">
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="percentage">{percentage}%</div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="feedback">
          <h3>📊 分析結果</h3>
          {results.isPassed ? (
            <p>素晴らしい成績です！試験合格の可能性が高いです。</p>
          ) : (
            <p>弱点を分析して、さらに学習を進めてください。</p>
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
