/**
 * ProtectedRoute.jsx - セッション検証ミドルウェア
 * ログイン済みユーザーのみアクセス可能
 */

import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { checkDeviceRestriction } from '../utils/deviceCheck';
import { apiEndpoints } from '../config/api';

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

      // localStorage からセッション情報取得
      const sessionToken = localStorage.getItem('session_token');
      const deviceId = localStorage.getItem('device_id');

      // セッション情報がない場合は即座に登録ページへ
      if (!sessionToken || !deviceId) {
        setIsValid(false);
        setIsLoading(false);
        return;
      }

      try {
        // Vercel KV API でセッション検証（デバイスIDバインディング含む）
        const response = await fetch(apiEndpoints.verifySession, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sessionToken, deviceId })
        });

        const data = await response.json();

        if (!response.ok || !data.valid) {
          // 無効なセッションの場合、localStorage をクリア
          localStorage.clear();
          setIsValid(false);
          setIsLoading(false);
          return;
        }

        // セッション有効
        setIsValid(true);
        setIsLoading(false);
      } catch (error) {
        // ネットワークエラー等
        localStorage.clear();
        setIsValid(false);
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
