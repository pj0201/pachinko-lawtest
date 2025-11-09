/**
 * 法律ビューア（3段階UI）
 * 第1段階：法律選択 → 第2段階：章立て → 第3段階：条文全文
 */

import { useState } from 'react';
import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../constants/lawDatabase';

export function LawViewer3Stage() {
  const [stage, setStage] = useState(0); // 0=法律選択, 1=章立て, 2=条文
  const [selectedLaw, setSelectedLaw] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);

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
            {selectedChapter.articles.map((article) => (
              <button
                key={article.articleNum}
                style={{ ...buttonStyle, backgroundColor: '#444' }}
                onClick={() => handleSelectArticle(article)}
              >
                第{article.articleNum}条：{article.title}
              </button>
            ))}
          </div>
        )}

        {selectedArticle && (
          <div>
            <h4 style={{ color: '#d4af37', margin: '0 0 10px 0' }}>
              第{selectedArticle.articleNum}条：{selectedArticle.title}
            </h4>
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
