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
  const [showExplanation, setShowExplanation] = useState(false);

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

        {/* 関連法律 */}
        <div className="legal-reference">
          <h3>📜 関連法律</h3>

          {/* 3段階法律ビューア */}
          <LawViewer3Stage />

          {/* 風営法と施行規則の違い解説 */}
          <button
            className="legal-doc-toggle"
            onClick={() => setShowExplanation(!showExplanation)}
            style={{
              marginTop: '12px',
              padding: '8px 16px',
              backgroundColor: '#d4af37',
              border: '1px solid #d4af37',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              width: '100%',
              textAlign: 'left',
              fontWeight: '600',
              color: '#0a0a0a'
            }}
          >
            📋 風営法と風営法施行規則の違いについて {showExplanation ? '▼' : '▶'}
          </button>

          {showExplanation && (
            <div className="legal-doc-content" style={{
              marginTop: '12px',
              padding: '16px',
              backgroundColor: '#1a1a1a',
              borderLeft: '4px solid #d4af37',
              fontSize: '13px',
              lineHeight: '1.6',
              maxHeight: '600px',
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              color: '#ffffff',
              borderRadius: '4px',
              border: '1px solid #333'
            }}>
              <h4 style={{ marginTop: 0, color: '#d4af37', fontSize: '14px', fontWeight: 'bold' }}>風営法と風営法施行規則の違いについて</h4>

              <p style={{ color: '#ffffff' }}>風営法（<strong>風俗営業等の規制及び業務の適正化等に関する法律</strong>）と風営法施行規則（<strong>風俗営業等の規制及び業務の適正化等に関する法律施行規則</strong>）は、いずれも風俗営業や特定遊興飲食店営業などを規制するための法令ですが、<strong>その役割と規定する内容の階層</strong>が異なります。</p>

              <h5 style={{ color: '#d4af37', fontSize: '13px', fontWeight: 'bold', marginTop: '16px', marginBottom: '8px' }}>1. 根拠となる法律と規則の違い</h5>

              <p style={{ color: '#ffffff' }}>この二つの法規の違いは、国家の法体系における役割の違いに基づいています。</p>

              <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '16px', border: '1px solid #444' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #d4af37', backgroundColor: '#222' }}>
                    <th style={{ padding: '10px', textAlign: 'left', borderRight: '1px solid #444', color: '#d4af37', fontWeight: 'bold' }}>項目</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderRight: '1px solid #444', color: '#d4af37', fontWeight: 'bold' }}>風営法（法律）</th>
                    <th style={{ padding: '10px', textAlign: 'left', color: '#d4af37', fontWeight: 'bold' }}>風営法施行規則（国家公安委員会規則）</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #444' }}>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}><strong>法的根拠</strong></td>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}><strong>法律</strong>（国会で制定される）</td>
                    <td style={{ padding: '10px', color: '#ffffff' }}><strong>規則</strong>（国家公安委員会によって定められる）</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #444' }}>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}><strong>役割</strong></td>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}><strong>大枠の規制、目的、定義、権利義務、罰則</strong>など、根幹となる事項を定める。</td>
                    <td style={{ padding: '10px', color: '#ffffff' }}>法律の規定を実施・運用するための<strong>具体的・技術的な基準や手続き</strong>を定める。</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}><strong>規定の例</strong></td>
                    <td style={{ padding: '10px', borderRight: '1px solid #444', color: '#ffffff' }}>風俗営業の<strong>定義</strong>、<strong>許可の必要性</strong>、営業を<strong>制限する目的</strong>、<strong>罰則</strong>の適用範囲など。</td>
                    <td style={{ padding: '10px', color: '#ffffff' }}>営業所の<strong>構造及び設備の技術上の基準</strong>、照度の<strong>測定方法</strong>、各種申請書の<strong>様式</strong>、帳簿の<strong>記載事項</strong>など。</td>
                  </tr>
                </tbody>
              </table>

              <h5 style={{ color: '#d4af37', fontSize: '13px', fontWeight: 'bold', marginTop: '16px', marginBottom: '8px' }}>2. 法律（風営法）の役割と規定内容</h5>

              <p style={{ color: '#ffffff' }}>風営法は、この規制体系の最も上位に位置し、以下の基本的な枠組みを定めます。</p>

              <ul style={{ color: '#ffffff' }}>
                <li><strong>目的（総則）</strong>: 善良の風俗と清浄な風俗環境を保持し、少年の健全な育成に障害を及ぼす行為を防止すること。</li>
                <li><strong>営業の定義</strong>: 「風俗営業」や「特定遊興飲食店営業」などの概念的な定義を定めます（例：ぱちんこ屋は客に射幸心をそそるおそれのある遊技をさせる営業である）。</li>
                <li><strong>許可・承認</strong>: 風俗営業を営むには、営業所ごとに都道府県公安委員会の<strong>許可</strong>が必要であることや、相続・合併の際の<strong>承認</strong>の必要性。</li>
                <li><strong>禁止行為と罰則</strong>: 現金または有価証券を賞品として提供することや、賞品を買い取ることなどの<strong>禁止行為</strong>、これに違反した場合の<strong>罰則</strong>の適用範囲（例：懲役や罰金の最高額）を定めます。</li>
                <li><strong>遊技機の規制大枠</strong>: 著しく客の射幸心をそそるおそれのある遊技機を設置してはならないという原則（法第20条第1項）を定める。</li>
              </ul>

              <h5 style={{ color: '#d4af37', fontSize: '13px', fontWeight: 'bold', marginTop: '16px', marginBottom: '8px' }}>3. 規則（風営法施行規則）の役割と規定内容</h5>

              <p style={{ color: '#ffffff' }}>風営法施行規則は、法律の定めた大枠を具体的に運用するための<strong>細則や技術的な事項</strong>を定めます。主任者試験においては、この規則に定められた具体的な数値や手順が特に重要になります。</p>

              <ul style={{ color: '#ffffff' }}>
                <li><strong>技術基準の詳細</strong>: 営業所の構造・設備に関する技術上の基準を、営業の種別に応じて具体的に定めます（例：客室の床面積、施錠設備の有無など）。</li>
                <li><strong>射幸心基準の具体的数値</strong>: 法律で「著しく射幸心をそそるおそれがある遊技機」を禁止しているのに対し、規則で遊技機の種類（ぱちんこ遊技機、回胴式遊技機など）ごとに、具体的な獲得率や入賞数、発射数などの数値基準（例：ぱちんこ遊技機は4時間で獲得数が発射数の1.5倍を超える性能を有してはならない）を詳細に定めます。</li>
                <li><strong>手続きと帳簿</strong>: 各種申請書や許可証の<strong>様式</strong>、管理者が備え付ける<strong>苦情の処理に関する帳簿</strong>に記載すべき具体的な事項（氏名、連絡先、原因究明の結果など5項目）や<strong>保存期間（3年間）</strong>を定めます。</li>
                <li><strong>測定方法</strong>: 照度の規制について、照度を計る場所や方法（遊技設備の前面または上面における<strong>水平面</strong>で計ること）を定めます。</li>
              </ul>

              <p style={{ color: '#ffffff' }}>したがって、<strong>風営法</strong>が「何を規制するか、なぜ規制するか」という骨格を定めるのに対し、<strong>風営法施行規則</strong>は「その規制を具体的にどう実現するか」という運用上の具体的なルールや数値を定めている、という違いがあります。</p>
            </div>
          )}

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
        <div className="exam-schedule">
          <h3>📅 遊技機取扱主任者試験情報</h3>
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
