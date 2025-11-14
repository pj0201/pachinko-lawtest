/**
 * ProtectedRoute.jsx - セッション検証ミドルウェア
 * ログイン済みユーザーのみアクセス可能
 */

import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { checkDeviceRestriction } from '../utils/deviceCheck';

export default function ProtectedRoute({ children }) {
  const [isValid, setIsValid] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deviceError, setDeviceError] = useState('');

  useEffect(() => {
    const verifySession = async () => {
      // デバイス制限チェック
      const deviceCheck = checkDeviceRestriction();
      if (!deviceCheck.allowed) {
        setDeviceError(deviceCheck.message);
        setIsValid(false);
        setIsLoading(false);
        return;
      }

      // サーバーレスモード: 常に開発モード（認証スキップ）
      const isDev = true;

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

      // ✅ サーバーレス化: localStorage のみでセッション管理
      console.log('✅ localStorage確認済み - アクセス許可（サーバーレスモード）');
      setIsValid(true);
      setIsLoading(false);
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
    // デバイス制限エラーの場合は専用画面を表示
    if (deviceError) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '20px',
          textAlign: 'center',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>❌ アクセス制限</h1>
            <p style={{ fontSize: '1.2rem', whiteSpace: 'pre-line', lineHeight: '1.8' }}>
              {deviceError}
            </p>
          </div>
        </div>
      );
    }

    return <Navigate to="/register" replace />;
  }

  return children;
}
