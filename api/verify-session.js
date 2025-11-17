/**
 * セッション検証API
 */
import Redis from 'ioredis';

// Redis Cloud 接続設定
const redis = new Redis({
  host: process.env.REDIS_HOST || 'redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com',
  port: parseInt(process.env.REDIS_PORT || '15687'),
  password: process.env.REDIS_PASSWORD,
  tls: {
    rejectUnauthorized: false
  },
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  }
});

redis.on('error', (err) => {
  console.error('❌ Redis接続エラー:', err.message);
});

export default async function handler(req, res) {
  // CORS対応
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed', valid: false });
  }

  try {
    const { sessionToken, deviceId } = req.body;
    console.log('🔍 [API] verify-session リクエスト:', { sessionToken, deviceId });

    // 入力検証
    if (!sessionToken || !deviceId) {
      console.log('❌ [API] 入力不足:', { sessionToken: !!sessionToken, deviceId: !!deviceId });
      return res.status(400).json({
        valid: false,
        error: 'セッション情報が不足しています'
      });
    }

    // Redis Cloud からセッション情報を取得
    const sessionDataStr = await redis.get(`session:${sessionToken}`);
    const sessionData = sessionDataStr ? JSON.parse(sessionDataStr) : null;
    console.log('🔍 [API] セッションデータ取得:', { sessionToken, sessionData });

    if (!sessionData) {
      console.log('❌ [API] 無効なセッション:', sessionToken);
      return res.status(401).json({
        valid: false,
        error: '無効なセッションです'
      });
    }

    // デバイスIDチェック（アカウント流失防止）
    if (sessionData.deviceId !== deviceId) {
      console.log('❌ [API] デバイスID不一致:', { expected: sessionData.deviceId, actual: deviceId });
      return res.status(401).json({
        valid: false,
        error: 'このセッションは別のデバイスで作成されました'
      });
    }

    // セッション有効
    console.log('✅ [API] セッション検証成功:', { sessionToken });
    return res.status(200).json({
      valid: true,
      user: {
        username: sessionData.username,
        email: sessionData.email,
        registeredAt: sessionData.registeredAt
      }
    });

  } catch (error) {
    console.error('❌ [API] verify-session エラー:', error);
    return res.status(500).json({
      valid: false,
      error: 'サーバーエラーが発生しました',
      details: error.message
    });
  }
}
