/**
 * 法律ビューア（3段階UI）
 * 第1段階：法律選択 → 第2段階：章立て → 第3段階：条文全文
 */

import { useState } from 'react';
import { WIND_BUSINESS_LAW, WIND_BUSINESS_REGULATION } from '../constants/lawDatabase';
import '../styles/lawViewer.css';

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

  // 第1段階：法律選択
  if (stage === 0) {
    return (
      <div className="law-viewer-container">
        <p className="law-viewer-header">📋 法律を選択してください</p>
        <button className="law-viewer-button" onClick={() => handleSelectLaw(WIND_BUSINESS_LAW)}>
          風営法（法律）{' '} →
        </button>
        <button className="law-viewer-button" onClick={() => handleSelectLaw(WIND_BUSINESS_REGULATION)}>
          風営法施行規則 →
        </button>
      </div>
    );
  }

  // 第2段階：章立て
  if (stage === 1 && selectedLaw) {
    return (
      <div className="law-viewer-container">
        <button className="law-viewer-button law-viewer-back-button" onClick={handleBack}>
          ← 戻る
        </button>
        <p className="law-viewer-title">{selectedLaw.name}</p>
        {selectedLaw.chapters.map((chapter) => (
          <button
            key={chapter.chapterNum}
            className="law-viewer-button"
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
      <div className="law-viewer-container">
        <button className="law-viewer-button law-viewer-back-button" onClick={handleBack}>
          ← 戻る
        </button>
        <p className="law-viewer-title">
          第{selectedChapter.chapterNum}章：{selectedChapter.chapterName}
        </p>

        {!selectedArticle && (
          <div>
            <p className="law-viewer-select-prompt">条を選択：</p>
            {selectedChapter.articles.map((article) => (
              <button
                key={article.articleNum}
                className="law-viewer-button law-viewer-article-button"
                onClick={() => handleSelectArticle(article)}
              >
                第{article.articleNum}条：{article.title}
              </button>
            ))}
          </div>
        )}

        {selectedArticle && (
          <div className="law-viewer-article-content">
            <h4>
              第{selectedArticle.articleNum}条：{selectedArticle.title}
            </h4>
            <p className="law-viewer-article-text">
              {selectedArticle.text}
            </p>
            <button
              className="law-viewer-button law-viewer-back-to-list"
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
