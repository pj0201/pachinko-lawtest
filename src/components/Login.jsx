/**
 * ログイン画面 - モバイルファースト
 * スマホ 360px以上に対応
 */

import { useState } from 'react';
import '../styles/login.css';

export function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // デモ用: 簡単な認証（実装後はバックエンド連携）
      if (!email || !password) {
        throw new Error('メールアドレスとパスワードを入力してください');
      }

      // ローカルストレージに保存（デモ用）
      localStorage.setItem('user', JSON.stringify({
        email: email,
        name: email.split('@')[0],
        loginTime: new Date().toISOString()
      }));

      onLogin({ email });
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* ヘッダー */}
      <div className="login-header">
        <div className="app-title">
          <h1>🎰 風営法理解度チェック</h1>
          <p className="subtitle">学習サポートアプリ</p>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="login-content">
        <form onSubmit={handleSubmit} className="login-form">
          <h2>ログイン</h2>

          {/* エラーメッセージ */}
          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
            </div>
          )}

          {/* メールアドレス入力 */}
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              id="email"
              type="email"
              placeholder="example@mail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {/* パスワード入力 */}
          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {/* ログインボタン */}
          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? 'ログイン中...' : 'ログイン'}
          </button>

          {/* パスワード忘却リンク */}
          <div className="forgot-password">
            <a href="#forgot">パスワードをお忘れの方</a>
          </div>
        </form>

        {/* デモ用注記 */}
        <div className="demo-info">
          <p>✓ デモ用: 任意のメール・パスワードでログイン可能</p>
        </div>
      </div>

      {/* フッター */}
      <div className="login-footer">
        <p className="version">v1.0</p>
        <p className="terms">利用規約 | プライバシーポリシー</p>
      </div>
    </div>
  );
}
