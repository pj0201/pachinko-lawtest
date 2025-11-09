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

    // 開発者モード（token=dev）
    if (token === 'dev') {
      console.log('🔧 開発者モード有効');
      setLoading(false);
      return;
    }

    // テスト用トークン検証（ローカル）
    const verifyTestToken = async () => {
      try {
        const response = await fetch('/test-tokens.json');
        const testTokenData = await response.json();

        // トークンが存在するか確認
        if (!testTokenData.tokens[token]) {
          setError('無効な招待URLです');
          setLoading(false);
          return;
        }

        // 既に使用済みか確認
        const usedTokens = JSON.parse(localStorage.getItem('used_tokens') || '[]');
        if (usedTokens.includes(token)) {
          setError('この招待URLは既に使用済みです');
          setLoading(false);
          return;
        }

        console.log(`✅ テスト用トークン有効: ${token}`);
        setLoading(false);
      } catch (err) {
        console.error('❌ テスト用トークン検証失敗:', err);
        setError('トークン検証に失敗しました');
        setLoading(false);
      }
    };

    verifyTestToken();
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

    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          device_id: deviceId,
          username
        })
      });

      const data = await response.json();

      if (data.success) {
        // セッショントークン保存
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('device_id', deviceId);

        // ユーザー情報も保存
        localStorage.setItem('username', username);
        localStorage.setItem('user', JSON.stringify({
          username,
          session_token: data.session_token
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

            <button type="submit" disabled={loading} className="submit-button">
              {loading ? '登録中...' : '登録して始める'}
            </button>
          </form>
        )}

        <p className="note">※ 招待URLは1台のデバイスのみ登録可能です</p>
      </div>
    </div>
  );
}
