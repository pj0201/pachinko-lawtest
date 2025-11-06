import '../styles/HomePage.css'

export default function HomePage({ onStartTest }) {
  return (
    <div className="home-page">
      <div className="header">
        <h1>🎓 主任者講習試験対策</h1>
        <p>パチンコ業界の資格試験対策アプリ</p>
      </div>

      <div className="content">
        <div className="stats-card">
          <div className="stat">
            <span className="stat-label">実施テスト</span>
            <span className="stat-value">5回</span>
          </div>
          <div className="stat">
            <span className="stat-label">平均正答率</span>
            <span className="stat-value">68%</span>
          </div>
          <div className="stat">
            <span className="stat-label">最高成績</span>
            <span className="stat-value">82%</span>
          </div>
        </div>

        <button className="primary-btn" onClick={onStartTest}>
          📝 模擬テスト開始
        </button>

        <div className="menu-buttons">
          <button className="menu-btn">📊 学習進捗</button>
          <button className="menu-btn">🎯 弱点分析</button>
          <button className="menu-btn">⚙️ 設定</button>
        </div>
      </div>

      <div className="footer">
        <p>準備を整えて、試験合格を目指しましょう！</p>
      </div>
    </div>
  )
}
