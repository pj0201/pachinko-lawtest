/**
 * 法律ビューア（3段階UI + 学習進捗管理）
 * 第1段階：法律選択 → 第2段階：章立て → 第3段階：条文全文
 * ✨ 学習進捗管理機能：各条文にチェックボックスを追加
 */

import { useState, useEffect } from 'react';
import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../constants/lawDatabase';

export function LawViewer3Stage() {
  const [stage, setStage] = useState(0); // 0=法律選択, 1=章立て, 2=条文
  const [selectedLaw, setSelectedLaw] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [checkedArticles, setCheckedArticles] = useState({});

  // ===== チェック状態の読み込み =====
  useEffect(() => {
    const savedChecks = localStorage.getItem('law_article_checks');
    if (savedChecks) {
      try {
        setCheckedArticles(JSON.parse(savedChecks));
      } catch (e) {
        console.error('チェック状態の読み込みエラー:', e);
      }
    }
  }, []);

  // ===== チェック状態のキー生成 =====
  const getCheckKey = (lawName, chapterNum, articleNum) => {
    return `${lawName}_ch${chapterNum}_art${articleNum}`;
  };

  // ===== チェックボックスのトグル =====
  const toggleCheck = (lawName, chapterNum, articleNum) => {
    const key = getCheckKey(lawName, chapterNum, articleNum);
    const newCheckedArticles = {
      ...checkedArticles,
      [key]: !checkedArticles[key]
    };
    setCheckedArticles(newCheckedArticles);

    // localStorage に保存
    localStorage.setItem('law_article_checks', JSON.stringify(newCheckedArticles));
  };

  // ===== チェック状態の取得 =====
  const isChecked = (lawName, chapterNum, articleNum) => {
    const key = getCheckKey(lawName, chapterNum, articleNum);
    return !!checkedArticles[key];
  };

  const handleSelectLaw = (law) => {
    setSelectedLaw(law);
    setSelectedChapter(null);
    setSelectedArticle(null);
    setStage(1);
  };

  const handleSelectChapter = (chapter) => {
    setSelectedChapter(chapter);
    setSelectedArticle(null);
    setStage(2);
  };

  const handleSelectArticle = (article) => {
    setSelectedArticle(article);
  };

  const handleBack = () => {
    if (stage === 2) {
      setStage(1);
      setSelectedArticle(null);
    } else if (stage === 1) {
      setStage(0);
      setSelectedLaw(null);
    }
  };

  const containerStyle = {
    marginTop: '12px',
    padding: '12px',
    backgroundColor: '#1a1a1a',
    border: '1px solid #444',
    borderRadius: '4px',
    fontSize: '13px',
    lineHeight: '1.8',
    color: '#ccc',
    maxHeight: '600px',
    overflowY: 'auto'
  };

  const buttonStyle = {
    marginBottom: '8px',
    padding: '10px 12px',
    backgroundColor: '#d4af37',
    border: '1px solid #d4af37',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '13px',
    width: '100%',
    textAlign: 'left',
    fontWeight: '600',
    color: '#0a0a0a'
  };

  const checkboxStyle = {
    marginRight: '8px',
    width: '16px',
    height: '16px',
    cursor: 'pointer',
    accentColor: '#d4af37'
  };

  // 第1段階：法律選択
  if (stage === 0) {
    return (
      <div style={containerStyle}>
        <p style={{ margin: '0 0 10px 0', color: '#d4af37', fontWeight: 'bold' }}>📋 法律を選択してください</p>
        <button style={buttonStyle} onClick={() => handleSelectLaw(WIND_BUSINESS_LAW)}>
          風営法（法律）{' '} →
        </button>
        <button style={buttonStyle} onClick={() => handleSelectLaw(WIND_BUSINESS_REGULATION)}>
          風営法施行規則 →
        </button>
      </div>
    );
  }

  // 第2段階：章立て
  if (stage === 1 && selectedLaw) {
    return (
      <div style={containerStyle}>
        <button style={{ ...buttonStyle, backgroundColor: '#666', marginBottom: '12px' }} onClick={handleBack}>
          ← 戻る
        </button>
        <p style={{ margin: '0 0 10px 0', color: '#d4af37', fontWeight: 'bold' }}>{selectedLaw.name}</p>
        {selectedLaw.chapters.map((chapter) => (
          <button
            key={chapter.chapterNum}
            style={buttonStyle}
            onClick={() => handleSelectChapter(chapter)}
          >
            第{chapter.chapterNum}章：{chapter.chapterName} →
          </button>
        ))}
      </div>
    );
  }

  // 第3段階：条文
  if (stage === 2 && selectedChapter) {
    return (
      <div style={containerStyle}>
        <button style={{ ...buttonStyle, backgroundColor: '#666', marginBottom: '12px' }} onClick={handleBack}>
          ← 戻る
        </button>
        <p style={{ margin: '0 0 10px 0', color: '#d4af37', fontWeight: 'bold' }}>
          第{selectedChapter.chapterNum}章：{selectedChapter.chapterName}
        </p>

        {!selectedArticle && (
          <div>
            <p style={{ margin: '0 0 8px 0', color: '#ccc', fontSize: '12px' }}>条を選択：</p>
            {selectedChapter.articles.map((article) => {
              const checked = isChecked(selectedLaw.name, selectedChapter.chapterNum, article.articleNum);

              return (
                <div
                  key={article.articleNum}
                  style={{
                    marginBottom: '8px',
                    padding: '10px 12px',
                    backgroundColor: '#444',
                    border: '1px solid #555',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  {/* チェックボックス */}
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => {
                      e.stopPropagation();
                      toggleCheck(selectedLaw.name, selectedChapter.chapterNum, article.articleNum);
                    }}
                    style={checkboxStyle}
                  />

                  {/* 条文ボタン */}
                  <button
                    style={{
                      flex: 1,
                      backgroundColor: 'transparent',
                      border: 'none',
                      color: checked ? '#88ff88' : '#ccc',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontSize: '13px',
                      fontWeight: checked ? 'bold' : 'normal',
                      padding: 0
                    }}
                    onClick={() => handleSelectArticle(article)}
                  >
                    第{article.articleNum}条：{article.title}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {selectedArticle && (
          <div>
            {/* 条文詳細ページのチェックボックス */}
            <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={isChecked(selectedLaw.name, selectedChapter.chapterNum, selectedArticle.articleNum)}
                onChange={() => toggleCheck(selectedLaw.name, selectedChapter.chapterNum, selectedArticle.articleNum)}
                style={{ ...checkboxStyle, width: '18px', height: '18px' }}
              />
              <h4 style={{
                color: '#d4af37',
                margin: 0,
                marginLeft: '8px',
                flex: 1
              }}>
                第{selectedArticle.articleNum}条：{selectedArticle.title}
              </h4>
            </div>

            <p style={{ color: '#ffffff', whiteSpace: 'pre-wrap', wordWrap: 'break-word', margin: 0 }}>
              {selectedArticle.text}
            </p>

            <button
              style={{ ...buttonStyle, backgroundColor: '#444', marginTop: '12px' }}
              onClick={() => setSelectedArticle(null)}
            >
              条一覧に戻る
            </button>
          </div>
        )}
      </div>
    );
  }

  return null;
}
