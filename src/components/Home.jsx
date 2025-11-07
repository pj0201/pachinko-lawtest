/**
 * ホーム画面 - トップページ
 * ✨ 修正版（2025-11-07）
 * モバイルファースト対応
 * Router ベースのナビゲーション
 */

import { useNavigate } from 'react-router-dom';
import '../styles/home.css';

export function Home({ onLogout }) {
  const navigate = useNavigate();

  // localStorage からユーザー情報を取得
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  // 問題集を解く
  const handleStartExam = (mode) => {
    // localStorage に モード情報を保存してから遷移
    localStorage.setItem('examMode', mode);
    navigate('/exam', { replace: false });
  };

  // 成績履歴を表示
  const handleViewHistory = () => {
    navigate('/history', { replace: false });
  };

  return (
    <div className="home-container">
      {/* ヘッダー */}
      <div className="home-header">
        <h1>🎰 風営法理解度チェック</h1>
        <p className="header-description">本アプリは風俗営業等の規制及び業務の適正化等に関する法律についての知識を学ぶアプリです</p>
        <p className="user-info">ユーザー: {user?.email || 'ゲスト'}</p>
      </div>

      {/* メインコンテンツ */}
      <div className="home-content">

        {/* 法律参照 */}
        <div className="legal-reference">
          <h3>📜 法律参照</h3>
          <a
            href="https://laws.e-gov.go.jp/law/323AC0000000122"
            target="_blank"
            rel="noopener noreferrer"
            className="legal-link"
          >
            風俗営業等の規制及び業務の適正化等に関する法律（e-Gov） →
          </a>
        </div>

        {/* 試験日程 */}
        <div className="exam-schedule">
          <h3>📅 遊技機取扱主任者試験日程</h3>
          <a
            href="https://exam.nichiyukyo.or.jp/"
            target="_blank"
            rel="noopener noreferrer"
            className="official-link"
          >
            公式サイトで日程確認 →
          </a>
        </div>

        {/* チェック開始セクション */}
        <div className="mock-exam-section">
          <h2>🧪 問題集を解く</h2>
          <p className="section-subtitle">（次ページで難易度を選べます）</p>

          <div className="exam-options">
            {/* 10問テスト */}
            <button
              className="exam-option small"
              onClick={() => handleStartExam('small')}
            >
              <div className="option-header">
                <span className="label">練習用</span>
                <span className="badge">記録なし</span>
              </div>
              <div className="option-content">
                <p className="num-questions">10問</p>
              </div>
            </button>

            {/* 30問テスト */}
            <button
              className="exam-option medium"
              onClick={() => handleStartExam('medium')}
            >
              <div className="option-header">
                <span className="label">標準</span>
                <span className="badge">成績記録</span>
              </div>
              <div className="option-content">
                <p className="num-questions">30問</p>
              </div>
            </button>

            {/* 50問テスト */}
            <button
              className="exam-option large"
              onClick={() => handleStartExam('large')}
            >
              <div className="option-header">
                <span className="label">本試験</span>
                <span className="badge">成績記録</span>
              </div>
              <div className="option-content">
                <p className="num-questions">50問</p>
              </div>
            </button>
          </div>
        </div>

        {/* 成績履歴 */}
        <div className="history-section">
          <button className="history-link" onClick={handleViewHistory}>
            📊 成績履歴を表示
          </button>
        </div>

      </div>

      {/* フッター＋ログアウト */}
      <div className="home-footer">
        <p>© 2025 風営法理解度チェックアプリ</p>
        <button
          className="logout-button"
          onClick={onLogout}
          title="セッション削除してログアウト"
        >
          ログアウト
        </button>
      </div>
    </div>
  );
}
