import { useState, useEffect } from 'react'
import '../styles/TestPage.css'
import { generateSampleQuestions, extractQuestionsFromOCR } from '../utils/ocrToQuestions'

export default function TestPage({ onComplete }) {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})

  // 初期化: OCR結果を読み込み、または サンプル問題を使用
  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    try {
      setLoading(true)
      setError(null)

      // バックエンドから OCR結果を取得
      const response = await fetch('http://localhost:3001/api/pdf-ocr/results')
      if (response.ok) {
        const data = await response.json()
        if (data.data && data.data.results) {
          // OCR結果から問題を生成
          const ocrQuestions = extractQuestionsFromOCR(data.data.results)
          if (ocrQuestions.length > 0) {
            setQuestions(ocrQuestions)
            console.log(`✅ OCR結果から${ocrQuestions.length}問を読み込みました`)
            return
          }
        }
      }

      // OCR結果がない場合はサンプル問題を使用
      const sampleQuestions = generateSampleQuestions()
      setQuestions(sampleQuestions)
      console.log('📝 サンプル問題を使用します')

    } catch (err) {
      console.warn('⚠️ バックエンド接続エラー:', err.message)
      // エラーでもサンプル問題を使用
      const sampleQuestions = generateSampleQuestions()
      setQuestions(sampleQuestions)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="test-page">
        <div className="loading">
          <p>⏳ 問題を読み込み中...</p>
        </div>
      </div>
    )
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="test-page">
        <div className="error">
          <p>❌ 問題が見つかりません</p>
        </div>
      </div>
    )
  }

  const SAMPLE_QUESTIONS = questions

  const currentQuestion = SAMPLE_QUESTIONS[currentIndex]
  const selectedAnswer = answers[currentQuestion.id]
  const progress = ((currentIndex) / SAMPLE_QUESTIONS.length) * 100

  const handleAnswer = (optionId) => {
    setAnswers({
      ...answers,
      [currentQuestion.id]: optionId
    })
  }

  const handleNext = () => {
    if (currentIndex < SAMPLE_QUESTIONS.length - 1) {
      setCurrentIndex(currentIndex + 1)
    } else {
      // テスト完了
      const results = calculateResults()
      onComplete(results)
    }
  }

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const calculateResults = () => {
    let correctCount = 0
    const categoryScores = {
      '法律知識': 0,
      '営業管理': 0,
      '機械知識': 0
    }
    const categoryCounts = { '法律知識': 0, '営業管理': 0, '機械知識': 0 }

    SAMPLE_QUESTIONS.forEach(question => {
      const selected = answers[question.id]
      const option = question.options.find(o => o.id === selected)

      categoryCounts[question.category]++

      if (option && option.isCorrect) {
        correctCount++
        categoryScores[question.category]++
      }
    })

    return {
      correctCount,
      totalCount: SAMPLE_QUESTIONS.length,
      percentage: Math.round((correctCount / SAMPLE_QUESTIONS.length) * 100),
      categoryScores,
      categoryCounts,
      isPassed: Math.round((correctCount / SAMPLE_QUESTIONS.length) * 100) >= 60
    }
  }

  return (
    <div className="test-page">
      <div className="test-header">
        <div className="progress-info">
          <span>問題 {currentIndex + 1}/{SAMPLE_QUESTIONS.length}</span>
          <span>進捗 {Math.round(progress)}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      <div className="test-content">
        <div className="category-badge">{currentQuestion.category}</div>

        <div className="question-text">
          <p>{currentQuestion.text}</p>
        </div>

        <div className="options">
          {currentQuestion.options.map(option => (
            <button
              key={option.id}
              className={`option-btn ${selectedAnswer === option.id ? 'selected' : ''}`}
              onClick={() => handleAnswer(option.id)}
            >
              <span className="option-circle">
                {selectedAnswer === option.id ? '✓' : ''}
              </span>
              <span className="option-text">{option.text}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="test-footer">
        <button
          className="nav-btn"
          onClick={handlePrevious}
          disabled={currentIndex === 0}
        >
          ← 前へ
        </button>

        <button className="submit-btn">
          {selectedAnswer ? '✓ 回答済み' : '◯ 未回答'}
        </button>

        <button
          className="nav-btn next-btn"
          onClick={handleNext}
          disabled={!selectedAnswer}
        >
          {currentIndex === SAMPLE_QUESTIONS.length - 1 ? 'テスト完了 →' : '次へ →'}
        </button>
      </div>
    </div>
  )
}
