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
      // 開発モードチェック（環境変数で厳密に管理）
      const isDev = import.meta.env.MODE === 'development' &&
                    import.meta.env.VITE_DEV_MODE === 'true' &&
                    (window.location.hostname === 'localhost' ||
                     window.location.hostname === '127.0.0.1');

      if (isDev) {
        console.log('🔧 開発環境モード: セッション検証をスキップ');
        console.warn('⚠️ 本番環境では .env の VITE_DEV_MODE を false に設定してください');

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
          localStorage.removeItem('verify_fail_count');
          // 即座に登録ページへリダイレクト
          setIsValid(false);
        } else {
          console.log('✅ バックグラウンド検証完了 - セッション有効');
          // 検証成功時はfail_countをリセット
          localStorage.removeItem('verify_fail_count');
        }
      } catch (err) {
        console.error('❌ バックグラウンド検証エラー:', err);
        // ネットワークエラーの場合は一定回数まで許容するが、
        // セキュリティを優先して3回連続失敗でログアウト
        const failCount = parseInt(localStorage.getItem('verify_fail_count') || '0');
        if (failCount >= 2) {
          console.error('🔒 セッション検証が3回連続で失敗したため、ログアウトします');
          localStorage.removeItem('session_token');
          localStorage.removeItem('device_id');
          localStorage.removeItem('user');
          localStorage.removeItem('verify_fail_count');
          setIsValid(false);
        } else {
          localStorage.setItem('verify_fail_count', String(failCount + 1));
          console.warn(`⚠️ セッション検証失敗 (${failCount + 1}/3回目) - 次回も失敗するとログアウトされます`);
        }
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
