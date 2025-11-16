/**
 * Register.jsx - 招待URL登録ページ
 * 招待トークン検証 → デバイス登録 → メイン画面へ
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Navigate } from 'react-router-dom';
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import { checkDeviceRestriction } from '../utils/deviceCheck';
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

  // マウント時：デバイス制限チェック
  useEffect(() => {
    const deviceCheck = checkDeviceRestriction();
    if (!deviceCheck.allowed) {
      setError(deviceCheck.message);
      setLoading(false);
      return;
    }

    // 既にセッションがあれば、ホーム画面にリダイレクト
    const sessionToken = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');

    if (sessionToken && deviceId) {
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

    // トークン基本チェック（API呼び出し前）
    if (!token) {
      setError('招待URLが無効です。正しいURLからアクセスしてください。');
      setLoading(false);
      return;
    }

    // トークンフォーマットチェック（UUID形式または TEST_/ADMIN_ プレフィックス）
    const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);
    const hasPrefix = token.startsWith('TEST_') || token.startsWith('ADMIN_');

    if (!isUUID && !hasPrefix) {
      setError('無効な招待URLです。');
      setLoading(false);
      return;
    }

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

    if (!token) {
      setError('招待URLが無効です');
      return;
    }

    setLoading(true);

    try {
      // Vercel KV API でトークンとメールアドレスを検証
      const validateResponse = await fetch('/api/validate-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, email })
      });

      const validateData = await validateResponse.json();

      if (!validateResponse.ok || !validateData.valid) {
        setError(validateData.error || '検証に失敗しました');
        setLoading(false);
        return;
      }

      // Vercel KV API でユーザー登録
      const registerResponse = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          username,
          token,
          deviceId
        })
      });

      const registerData = await registerResponse.json();

      if (!registerResponse.ok || !registerData.success) {
        setError(registerData.error || '登録に失敗しました');
        setLoading(false);
        return;
      }

      // セッション情報を localStorage に保存
      const { sessionToken, user } = registerData;
      localStorage.setItem('session_token', sessionToken);
      localStorage.setItem('device_id', deviceId);
      localStorage.setItem('username', user.username);
      localStorage.setItem('email', user.email);
      localStorage.setItem('invite_token', token);
      localStorage.setItem('user', JSON.stringify({
        username: user.username,
        email: user.email,
        invite_token: token,
        session_token: sessionToken,
        registered_at: user.registeredAt
      }));

      // メイン画面へリダイレクト
      navigate('/', { replace: true });
    } catch (err) {
      console.error('❌ 登録エラー:', err);
      setError('サーバーとの通信に失敗しました');
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

        <p className="note">※ 招待URLは1回のみ使用可能です。ユーザー名とメールアドレスを入力してください。</p>
      </div>
    </div>
  );
}
