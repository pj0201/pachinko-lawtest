/**
 * App.jsx - メインアプリケーション
 * 招待URL登録 → ログイン → ホーム → 模擬試験 → 成績 → 履歴 の遷移管理
 */

import { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { Login } from './components/Login';
import { Home } from './components/Home';
import { ExamScreen } from './components/ExamScreen';
import { History } from './components/History';

function MainApp() {
  const [currentPage, setCurrentPage] = useState('login');
  const [user, setUser] = useState(null);
  const [examMode, setExamMode] = useState(null); // 'small', 'medium', 'large'
  const navigate = useNavigate();

  // ログイン処理
  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentPage('home');
  };

  // ログアウト処理
  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('session_token');
    localStorage.removeItem('device_id');
    setUser(null);
    setCurrentPage('login');
    navigate('/register');
  };

  // 模擬試験開始
  const handleStartExam = (mode) => {
    setExamMode(mode);
    setCurrentPage('exam');
  };

  // 成績履歴表示
  const handleViewHistory = () => {
    setCurrentPage('history');
  };

  return (
    <div className="app">
      {/* ログインページ */}
      {currentPage === 'login' && !user && (
        <Login onLogin={handleLogin} />
      )}

      {/* ホームページ */}
      {currentPage === 'home' && user && (
        <Home
          user={user}
          onStartExam={handleStartExam}
          onViewHistory={handleViewHistory}
          onLogout={handleLogout}
        />
      )}

      {/* 模擬試験ページ */}
      {currentPage === 'exam' && user && (
        <ExamScreen
          examMode={examMode}
          onExit={() => setCurrentPage('home')}
        />
      )}

      {/* 成績履歴ページ */}
      {currentPage === 'history' && user && (
        <History
          onExit={() => setCurrentPage('home')}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <Routes>
      {/* 招待URL登録ページ（公開） */}
      <Route path="/invite/:token" element={<Register />} />
      <Route path="/register" element={<Register />} />

      {/* メインアプリ（セッション検証必須） */}
      <Route path="/*" element={
        <ProtectedRoute>
          <MainApp />
        </ProtectedRoute>
      } />
    </Routes>
  );
}

export default App;
