/**
 * 開発者ダッシュボード
 * メールアドレス: 729393 でログイン
 */

import { useState, useEffect } from 'react';

export function DevDashboard() {
  const [devToken, setDevToken] = useState(null);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [deviceStats, setDeviceStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ログイン状態チェック
  useEffect(() => {
    const saved = localStorage.getItem('dev_token');
    if (saved) {
      setDevToken(saved);
      fetchDashboardData(saved);
    }
  }, []);

  // ログイン処理
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/dev/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });

      const data = await response.json();

      if (data.success) {
        setDevToken(data.dev_token);
        localStorage.setItem('dev_token', data.dev_token);
        fetchDashboardData(data.dev_token);
      } else {
        setError(data.message || 'ログインに失敗しました');
      }
    } catch (err) {
      setError('サーバーエラーが発生しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ダッシュボードデータ取得
  const fetchDashboardData = async (token) => {
    setLoading(true);

    try {
      // ユーザー一覧取得
      const usersRes = await fetch('/api/dev/users', {
        headers: { 'X-Dev-Token': token }
      });
      const usersData = await usersRes.json();
      if (usersData.success) {
        setUsers(usersData.users);
      }

      // 統計情報取得
      const statsRes = await fetch('/api/dev/stats', {
        headers: { 'X-Dev-Token': token }
      });
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.stats);
        setDeviceStats(statsData.device_stats);
      }
    } catch (err) {
      setError('データの取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ログアウト
  const handleLogout = () => {
    setDevToken(null);
    localStorage.removeItem('dev_token');
    setUsers([]);
    setStats(null);
    setDeviceStats(null);
  };

  // ===== スタイル =====

  const containerStyle = {
    minHeight: '100vh',
    backgroundColor: '#1a1a1a',
    color: '#fff',
    padding: '20px'
  };

  const headerStyle = {
    backgroundColor: '#d4af37',
    color: '#0a0a0a',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const cardStyle = {
    backgroundColor: '#2a2a2a',
    border: '1px solid #444',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px'
  };

  const buttonStyle = {
    backgroundColor: '#d4af37',
    color: '#0a0a0a',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: '14px'
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '12px',
    backgroundColor: '#333',
    border: '1px solid #555',
    borderRadius: '4px',
    color: '#fff',
    fontSize: '14px'
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '12px'
  };

  const thStyle = {
    backgroundColor: '#333',
    padding: '12px',
    textAlign: 'left',
    borderBottom: '2px solid #d4af37',
    fontWeight: 'bold'
  };

  const tdStyle = {
    padding: '12px',
    borderBottom: '1px solid #444'
  };

  // ===== ログイン画面 =====

  if (!devToken) {
    return (
      <div style={containerStyle}>
        <div style={{ maxWidth: '400px', margin: '100px auto' }}>
          <div style={cardStyle}>
            <h2 style={{ color: '#d4af37', marginBottom: '20px', textAlign: 'center' }}>
              🔧 開発者ダッシュボード
            </h2>

            {error && (
              <div style={{
                backgroundColor: '#ff4444',
                color: '#fff',
                padding: '12px',
                borderRadius: '4px',
                marginBottom: '12px'
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleLogin}>
              <input
                type="text"
                placeholder="メールアドレス"
                value={loginForm.email}
                onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                style={inputStyle}
                required
              />

              <input
                type="password"
                placeholder="パスワード"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                style={inputStyle}
                required
              />

              <button
                type="submit"
                style={{ ...buttonStyle, width: '100%' }}
                disabled={loading}
              >
                {loading ? 'ログイン中...' : 'ログイン'}
              </button>
            </form>

            <p style={{ marginTop: '20px', color: '#888', fontSize: '12px', textAlign: 'center' }}>
              開発者認証情報: 729393 / 729393
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ===== ダッシュボード画面 =====

  return (
    <div style={containerStyle}>
      {/* ヘッダー */}
      <div style={headerStyle}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>🔧 開発者ダッシュボード</h1>
        <button onClick={handleLogout} style={{ ...buttonStyle, backgroundColor: '#666' }}>
          ログアウト
        </button>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#d4af37' }}>
          読み込み中...
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: '#ff4444',
          color: '#fff',
          padding: '12px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {/* 統計情報 */}
      {stats && (
        <div style={cardStyle}>
          <h2 style={{ color: '#d4af37', marginBottom: '16px' }}>📊 統計情報</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>総ユーザー数</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#d4af37' }}>
                {stats.total_users}
              </div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>アクティブセッション</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4ade80' }}>
                {stats.active_sessions}
              </div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>総招待トークン</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#60a5fa' }}>
                {stats.total_tokens}
              </div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>使用済みトークン</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f472b6' }}>
                {stats.used_tokens}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* デバイス種類統計 */}
      {deviceStats && (
        <div style={cardStyle}>
          <h2 style={{ color: '#d4af37', marginBottom: '16px' }}>📱 デバイス種類別ユーザー数</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
            <div style={{ backgroundColor: '#333', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>📱 Android</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{deviceStats.Android}</div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>🍎 iPhone</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{deviceStats.iPhone}</div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>💻 PC</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{deviceStats.PC}</div>
            </div>
            <div style={{ backgroundColor: '#333', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>❓ Unknown</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{deviceStats.Unknown}</div>
            </div>
          </div>
        </div>
      )}

      {/* ユーザー一覧 */}
      <div style={cardStyle}>
        <h2 style={{ color: '#d4af37', marginBottom: '16px' }}>👥 ユーザー一覧</h2>

        {users.length === 0 ? (
          <p style={{ color: '#888' }}>ユーザーが登録されていません</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>ID</th>
                  <th style={thStyle}>メールアドレス</th>
                  <th style={thStyle}>デバイス種類</th>
                  <th style={thStyle}>登録日時</th>
                  <th style={thStyle}>最終ログイン</th>
                  <th style={thStyle}>セッション数</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td style={tdStyle}>{user.id}</td>
                    <td style={tdStyle}>{user.email || '未登録'}</td>
                    <td style={tdStyle}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: user.device_type === 'Android' ? '#4ade80' :
                                        user.device_type === 'iPhone' ? '#60a5fa' :
                                        user.device_type === 'PC' ? '#f472b6' : '#666',
                        color: '#0a0a0a',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {user.device_type || 'Unknown'}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      {user.registered_at ? new Date(user.registered_at).toLocaleString('ja-JP') : '-'}
                    </td>
                    <td style={tdStyle}>
                      {user.last_login ? new Date(user.last_login).toLocaleString('ja-JP') : '-'}
                    </td>
                    <td style={tdStyle}>{user.session_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* リロードボタン */}
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <button
          onClick={() => fetchDashboardData(devToken)}
          style={buttonStyle}
          disabled={loading}
        >
          {loading ? '更新中...' : '🔄 データを再読み込み'}
        </button>
      </div>
    </div>
  );
}
