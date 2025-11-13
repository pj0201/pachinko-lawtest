/**
 * ホーム画面 - トップページ
 * ✨ 修正版（2025-11-07）
 * モバイルファースト対応
 * Router ベースのナビゲーション
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/home.css';
import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../constants/lawDatabase';
import { LawViewer3Stage } from './LawViewer3Stage';

export function Home() {
  const navigate = useNavigate();
  const [showLegalDoc, setShowLegalDoc] = useState(false);
  const [showPdf1, setShowPdf1] = useState(false);
  const [showPdf2, setShowPdf2] = useState(false);

  // 3段階UI用State
  const [expandedLaw, setExpandedLaw] = useState(null); // どの法律を展開しているか('law' or 'regulation')
  const [expandedChapter, setExpandedChapter] = useState(null); // どの章を展開しているか
  const [expandedArticle, setExpandedArticle] = useState(null); // どの条を展開しているか

  // localStorage からユーザー名を取得
  const username = localStorage.getItem('username') || 'ゲスト';

  // PDF ファイル名定義
  const PDF_FILES = {
    law: '風俗営業等の規制及び業務の適正化等に関する法律.pdf',
    regulation: '風俗営業等の規制及び業務の適正化等に関する法律施行規則.pdf'
  };

  // API URL ビルダー
  const getPdfUrl = (filename) => `/api/pdf/${encodeURIComponent(filename)}`;

  // 問題集を解く
  const handleStartExam = (mode) => {
    // localStorage に モード情報を保存してから遷移
    console.log(`🏠 Home.jsx: handleStartExam('${mode}') が呼ばれました`);
    localStorage.setItem('examMode', mode);
    console.log(`💾 localStorage.setItem('examMode', '${mode}') を実行`);
    console.log(`🔍 確認: localStorage.getItem('examMode') = '${localStorage.getItem('examMode')}'`);
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
        <p className="user-info">ユーザー: {username}</p>
      </div>

      {/* メインコンテンツ */}
      <div className="home-content">

        {/* 法律参照 */}
        <div className="legal-reference">
          <h3>📜 法律参照</h3>

          {/* 3段階法律ビューア */}
          <LawViewer3Stage />

          {/* 法律参照情報 */}
          <div style={{
            marginTop: '12px',
            padding: '8px',
            fontSize: '12px',
            lineHeight: '1.6',
            color: '#ccc',
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: '6px'
          }}>
            <p style={{ margin: '0 0 6px 0', fontWeight: '500' }}>📋 法律参照</p>
            <p style={{ margin: '0 0 4px 0' }}>本問題集は日本の<strong>風営法</strong>（昭和23年法律第122号）及び<strong>風営法施行規則</strong>（昭和63年自治省令第1号）に基づいて作成されています。</p>
            <p style={{ margin: '0', fontSize: '11px', color: '#999' }}>データ出典：e-Gov法令検索 / ライセンス：CC BY 4.0</p>
          </div>
        </div>

        {/* 公式試験情報 */}
        <div className="exam-schedule" style={{ textAlign: 'center' }}>
          <h3>📅 遊技機取扱主任者試験情報</h3>
          <p style={{ margin: '0 0 12px 0', fontSize: '13px', lineHeight: '1.6' }}>
            日遊協が実施する資格制度。詳細は公式サイトをご確認ください。
          </p>
          <a
            href="https://exam.nichiyukyo.or.jp/"
            target="_blank"
            rel="noopener noreferrer"
            className="official-link"
          >
            公式サイトで情報確認 →
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
                <span className="label">練習</span>
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
                <span className="badge">成績履歴あり</span>
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
                <span className="label">上級</span>
                <span className="badge">成績履歴あり</span>
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

      {/* フッター */}
      <div className="home-footer">
        <p>© 2025 風営法理解度チェックアプリ</p>
      </div>
    </div>
  );
}
