/**
 * Register.jsx - 招待URL登録ページ
 * 招待トークン検証 → デバイス登録 → メイン画面へ
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Navigate } from 'react-router-dom';
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import './Register.css';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [deviceId, setDeviceId] = useState('');
  const [alreadyLoggedIn, setAlreadyLoggedIn] = useState(false);  // 既にログイン状態の場合
  const params = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // トークンを URL パラメータまたはクエリパラメータから取得
  const token = params.token || searchParams.get('token');

  // マウント時：既にセッションがあれば、ホーム画面にリダイレクト
  useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');

    if (sessionToken && deviceId) {
      console.log('✅ セッション確認 - ホーム画面へリダイレクト');
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

    // サーバーレスモード: トークン不要（常に有効）
    console.log('✅ サーバーレスモード: 招待URL不要');
    setLoading(false);
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!deviceId) {
      setError('デバイス識別情報が取得できていません。ページを再読み込みしてください。');
      return;
    }

    if (!username) {
      setError('ユーザー名を入力してください');
      return;
    }

    if (!email) {
      setError('メールアドレスを入力してください');
      return;
    }

    setLoading(true);

    try {
      // サーバーレス化: localStorage に直接セッション情報を保存
      const sessionToken = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);

      // セッショントークン保存
      localStorage.setItem('session_token', sessionToken);
      localStorage.setItem('device_id', deviceId);

      // ユーザー情報も保存
      localStorage.setItem('username', username);
      localStorage.setItem('email', email);
      localStorage.setItem('user', JSON.stringify({
        username,
        email,
        session_token: sessionToken,
        registered_at: new Date().toISOString()
      }));

      // テスト用トークン無効化（重要）
      if (token && (token.startsWith('TEST_') || token.startsWith('ADMIN_'))) {
        const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
        if (!usedTokens.includes(token)) {
          usedTokens.push(token);
          localStorage.setItem('used_tokens', JSON.stringify(usedTokens));
          console.log(`✅ トークン無効化: ${token}`);
        }
      }

      console.log('✅ 登録成功（サーバーレス） - セッショントークン:', sessionToken);

      // メイン画面へリダイレクト（履歴を置き換え - ブラウザバックで戻れないように）
      navigate('/', { replace: true });
    } catch (err) {
      console.error('❌ 登録エラー:', err);
      setError('登録に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // 既にログイン状態なら、ホーム画面にリダイレクト
  if (alreadyLoggedIn) {
    return <Navigate to="/" replace />;
  }

  if (loading && !error) {
    return (
      <div className="register-container">
        <div className="loading">
          <h2>読み込み中...</h2>
          <p>初期化しています</p>
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h1>風営法（パチンコ業界）理解度チェック</h1>
        <h2>アカウント登録</h2>

        {error && <div className="error-message">{error}</div>}

        {!error && (
          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-group">
              <label htmlFor="username">ユーザー名</label>
              <input
                id="username"
                type="text"
                placeholder="ユーザー名（例：テスト001）"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                autoComplete="off"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">メールアドレス</label>
              <input
                id="email"
                type="email"
                placeholder="メールアドレス（例：test@example.com）"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <button type="submit" disabled={loading} className="submit-button">
              {loading ? '登録中...' : '登録して始める'}
            </button>
          </form>
        )}

        <p className="note">※ ユーザー名とメールアドレスを入力してアプリを開始してください</p>
      </div>
    </div>
  );
}
