/**
 * Register.jsx - 招待URL登録ページ
 * 招待トークン検証 → デバイス登録 → メイン画面へ
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Navigate } from 'react-router-dom';
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import './Register.css';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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

    // トークン検証
    if (!token) {
      setError('招待URLが無効です');
      setLoading(false);
      return;
    }

    fetch('/api/auth/verify-invite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    })
      .then(res => res.json())
      .then(data => {
        if (!data.valid) {
          setError(data.message || '無効な招待URLです');
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('❌ トークン検証失敗:', err);
        setError('サーバーへの接続に失敗しました');
        setLoading(false);
      });
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!deviceId) {
      setError('デバイス識別情報が取得できていません。ページを再読み込みしてください。');
      return;
    }

    if (!email || !password) {
      setError('メールアドレスとパスワードを入力してください');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          device_id: deviceId,
          email,
          password
        })
      });

      const data = await response.json();

      if (data.success) {
        // セッショントークン保存
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('device_id', deviceId);

        // ユーザー情報も保存（既存のLogin互換性のため）
        localStorage.setItem('user', JSON.stringify({
          email,
          session_token: data.session_token
        }));

        console.log('✅ 登録成功 - セッショントークン:', data.session_token);

        // メイン画面へリダイレクト（履歴を置き換え - ブラウザバックで戻れないように）
        navigate('/', { replace: true });
      } else {
        setError(data.message || '登録に失敗しました');
      }
    } catch (err) {
      console.error('❌ 登録エラー:', err);
      setError('サーバーへの接続に失敗しました');
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
          <p>招待URLを検証しています</p>
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h1>遊技機取扱主任者試験アプリ</h1>
        <h2>アルファ版登録</h2>

        {error && <div className="error-message">{error}</div>}

        {!error && (
          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-group">
              <label htmlFor="email">メールアドレス</label>
              <input
                id="email"
                type="text"
                placeholder="メールアドレス"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">パスワード</label>
              <input
                id="password"
                type="password"
                placeholder="パスワード"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button type="submit" disabled={loading} className="submit-button">
              {loading ? '登録中...' : '登録して始める'}
            </button>
          </form>
        )}

        <p className="note">※ 招待URLは1台のデバイスのみ登録可能です</p>
        <p className="note">※ アルファ版テスターとして選ばれたことに感謝します</p>
      </div>
    </div>
  );
}
