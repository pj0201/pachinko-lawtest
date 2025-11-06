/**
 * ProtectedRoute.jsx - セッション検証ミドルウェア
 * ログイン済みユーザーのみアクセス可能
 */

import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const [isValid, setIsValid] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const verifySession = async () => {
      // ✅ 開発環境モード: パソコンでのテスト用
      // .env.local の VITE_DEV_MODE=true で有効 (本番環境では false に変更)
      const isDev = import.meta.env.VITE_DEV_MODE === 'true' &&
                    (window.location.hostname === 'localhost' ||
                     window.location.hostname === '127.0.0.1');

      if (isDev) {
        console.log('🔧 開発環境モード: セッション検証をスキップ (本番環境に復帰する際は .env.local の VITE_DEV_MODE を false に設定)');

        // テスト用ダミーセッション作成
        if (!localStorage.getItem('session_token')) {
          localStorage.setItem('session_token', 'dev-test-token-' + Date.now());
          localStorage.setItem('device_id', 'dev-desktop-' + Date.now());
          localStorage.setItem('user', JSON.stringify({
            email: 'test@dev.local',
            name: 'Test User',
            loginTime: new Date().toISOString(),
            isDev: true
          }));
          console.log('✅ テスト用セッション作成完了');
        }

        setIsValid(true);
        setIsLoading(false);
        return;
      }

      // 本番環境: 通常の認証チェック
      const sessionToken = localStorage.getItem('session_token');
      const deviceId = localStorage.getItem('device_id');

      // セッション情報がない場合は即座に登録ページへ
      if (!sessionToken || !deviceId) {
        console.log('⚠️ セッション情報なし - 登録ページへリダイレクト');
        setIsValid(false);
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/auth/verify-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_token: sessionToken,
            device_id: deviceId
          })
        });

        const data = await response.json();

        if (data.valid) {
          console.log('✅ セッション有効');
          setIsValid(true);
        } else {
          console.log('❌ セッション無効:', data.message);
          // 無効なセッション情報を削除
          localStorage.removeItem('session_token');
          localStorage.removeItem('device_id');
          localStorage.removeItem('user');
          setIsValid(false);
        }
      } catch (err) {
        console.error('❌ セッション検証エラー:', err);
        setIsValid(false);
      } finally {
        setIsLoading(false);
      }
    };

    verifySession();
  }, []);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '1.5rem'
      }}>
        <div>
          <p>セッション確認中...</p>
        </div>
      </div>
    );
  }

  if (!isValid) {
    return <Navigate to="/register" replace />;
  }

  return children;
}
