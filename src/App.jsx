/**
 * App.jsx - メインアプリケーション
 * ✨ 修正版（2025-11-07）
 *
 * アーキテクチャ：
 * - React Router ベースの遷移管理
 * - state ベース遷移を廃止（混在によるバグを防止）
 * - ブラウザバック対応：replace: true で履歴クリア
 *
 * フロー：
 * 招待URL（/invite/:token） → デバイス登録（Register）
 * → セッション確認（ProtectedRoute）
 * → ホーム（/home） → 試験（/exam） → 履歴（/history）
 */

import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';
import Register from './pages/Register';
import { Home } from './components/Home';
import { ExamScreen } from './components/ExamScreen';
import { History } from './components/History';

/**
 * MainApp - ProtectedRoute 内で実行される認証済みアプリ
 * （状態管理は削除 → Router ベースに統一）
 */
function MainApp() {
  const navigate = useNavigate();

  return (
    <Routes>
      {/* ホーム */}
      <Route
        path="/"
        element={<Home />}
      />

      {/* 模擬試験画面 */}
      <Route
        path="/exam"
        element={
          <ExamScreen
            onExit={() => navigate('/', { replace: true })}
          />
        }
      />

      {/* 成績履歴画面 */}
      <Route
        path="/history"
        element={
          <History
            onExit={() => navigate('/', { replace: true })}
          />
        }
      />

      {/* その他のパスは home にリダイレクト */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

/**
 * App - ルートコンポーネント
 */
function App() {
  return (
    <Routes>
      {/*
        ========================================
        公開ルート（認証なし）
        ========================================
      */}
      {/* 招待URL登録ページ */}
      <Route path="/invite/:token" element={<Register />} />
      <Route path="/register" element={<Register />} />

      {/*
        ========================================
        保護ルート（セッション必須）
        ========================================
        ProtectedRoute で以下を確認：
        1. localStorage に session_token と device_id があるか
        2. ない場合は /register にリダイレクト（replace: true）
        3. あれば MainApp を表示
      */}
      <Route
        path="/*"
        element={<MainApp />}
      />
    </Routes>
  );
}

export default App;
