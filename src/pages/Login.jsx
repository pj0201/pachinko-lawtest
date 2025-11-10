/**
 * Login.jsx - 再ログインページ
 * メールアドレス + ユーザー名で認証
 */

import { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import './Register.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [deviceId, setDeviceId] = useState('');
  const [alreadyLoggedIn, setAlreadyLoggedIn] = useState(false);
  const navigate = useNavigate();

  // マウント時：既にセッションがあれば、ホーム画面にリダイレクト
  useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');

    if (sessionToken && deviceId) {
      console.log('✅ セッション確認済み - ホーム画面へリダイレクト');
      setAlreadyLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    // デバイスID取得
    const initFingerprint = async () => {
      try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        setDeviceId(result.visitorId);
        console.log('✅ デバイスID取得:', result.visitorId);
      } catch (err) {
        console.error('❌ デバイスID取得失敗:', err);
        setError('デバイス識別に失敗しました');
      }
    };

    initFingerprint();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!deviceId) {
      setError('デバイス識別情報が取得できていません。ページを再読み込みしてください。');
      return;
    }

    if (!email) {
      setError('メールアドレスを入力してください');
      return;
    }

    if (!username) {
      setError('ユーザー名を入力してください');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          username,
          device_id: deviceId
        })
      });

      const data = await response.json();

      if (data.success) {
        // セッショントークン保存
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('device_id', deviceId);

        // ユーザー情報も保存
        localStorage.setItem('email', data.email);
        localStorage.setItem('username', data.username);
        localStorage.setItem('user', JSON.stringify({
          email: data.email,
          username: data.username,
          session_token: data.session_token
        }));

        console.log('✅ ログイン成功 - セッショントークン:', data.session_token);

        // ホーム画面へリダイレクト（履歴を置き換え）
        navigate('/', { replace: true });
      } else {
        setError(data.message || 'ログインに失敗しました');
      }
    } catch (err) {
      console.error('❌ ログインエラー:', err);
      setError('サーバーへの接続に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // 既にログイン状態なら、ホーム画面にリダイレクト
  if (alreadyLoggedIn) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h1>風営法（パチンコ業界）理解度チェック</h1>
        <h2>ログイン</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              id="email"
              type="email"
              placeholder="登録時のメールアドレス"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">ユーザー名</label>
            <input
              id="username"
              type="text"
              placeholder="登録時のユーザー名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="off"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        <div className="important-notice">
          <p className="note">※ 登録時に入力したメールアドレスとユーザー名を使用してください</p>
          <p className="note">※ 登録したデバイスからのみログイン可能です</p>
        </div>
      </div>
    </div>
  );
}
