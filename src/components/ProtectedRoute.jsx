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

      // 本番環境: localStorage を優先（高速化）
      const sessionToken = localStorage.getItem('session_token');
      const deviceId = localStorage.getItem('device_id');

      // セッション情報がない場合は即座に登録ページへ
      if (!sessionToken || !deviceId) {
        console.log('⚠️ セッション情報なし - 登録ページへリダイレクト');
        setIsValid(false);
        setIsLoading(false);
        return;
      }

      // ✅ localStorage があれば即座にアクセス許可（UX向上）
      console.log('✅ localStorage確認済み - アクセス許可（バックグラウンド検証実行）');
      setIsValid(true);
      setIsLoading(false);

      // バックグラウンドで検証を実行（ユーザーはブロックされない）
      try {
        const response = await fetch('/api/auth/verify-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_token: sessionToken,
            device_id: deviceId
          })
        });

        const data = await response.json();

        if (!data.valid) {
          console.warn('⚠️ バックグラウンド検証でセッション無効を検出:', data.message);
          // 無効なセッション情報を削除
          localStorage.removeItem('session_token');
          localStorage.removeItem('device_id');
          localStorage.removeItem('user');
          // 次のページ移動時に Register にリダイレクト
          setIsValid(false);
        } else {
          console.log('✅ バックグラウンド検証完了 - セッション有効');
        }
      } catch (err) {
        console.warn('⚠️ バックグラウンド検証エラー（無視）:', err);
        // バックグラウンド検証エラーは無視
        // ユーザーはアクセス可能なままで、次の検証機会に確認
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
