/**
 * トークン検証API
 */
import Redis from 'ioredis';

// Redis接続を作成する関数
function createRedisClient() {
  return new Redis({
    host: process.env.REDIS_HOST || 'redis-15687.c10.us-east-1-3.ec2.cloud.redislabs.com',
    port: parseInt(process.env.REDIS_PORT || '15687'),
    password: process.env.REDIS_PASSWORD,
    tls: {
      rejectUnauthorized: false
    },
    retryStrategy: (times) => {
      if (times > 3) return null; // 3回失敗したら諦める
      const delay = Math.min(times * 50, 2000);
      return delay;
    },
    connectTimeout: 10000,
    maxRetriesPerRequest: 3
  });
}

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

  let redis = null;

  try {
    const { token, email } = req.body;
    console.log('🔍 [API] validate-token リクエスト:', { token, email });

    // 入力検証
    if (!token || !email) {
      console.log('❌ [API] 入力不足:', { token: !!token, email: !!email });
      return res.status(400).json({
        error: 'トークンとメールアドレスが必要です',
        valid: false
      });
    }

    // メールアドレスフォーマット検証
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      console.log('❌ [API] 無効なメールアドレス:', email);
      return res.status(400).json({
        error: '無効なメールアドレスです',
        valid: false
      });
    }

    // トークンフォーマットチェック（TEST_, ADMIN_, UUID v4対応）
    const isValidFormat =
      token.startsWith('TEST_') ||
      token.startsWith('ADMIN_') ||
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);

    console.log('🔍 [API] トークンフォーマットチェック:', { token, isValidFormat });

    if (!isValidFormat) {
      console.log('❌ [API] 無効なトークンフォーマット:', token);
      return res.status(400).json({
        error: '無効な招待URLです',
        valid: false
      });
    }

    // Redis接続
    redis = createRedisClient();
    await redis.ping(); // 接続確認
    console.log('✅ [API] Redis接続成功');

    // トークン使用済みチェック
    const usedTokenStr = await redis.get(`token:${token}`);
    const usedToken = usedTokenStr ? JSON.parse(usedTokenStr) : null;
    console.log('🔍 [API] トークン使用済みチェック:', { token, usedToken });

    if (usedToken) {
      console.log('❌ [API] トークン使用済み:', token);
      await redis.quit();
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        valid: false
      });
    }

    // メールアドレス重複チェック
    const existingEmailStr = await redis.get(`email:${email}`);
    const existingEmail = existingEmailStr ? JSON.parse(existingEmailStr) : null;
    console.log('🔍 [API] メールアドレス重複チェック:', { email, existingEmail });

    if (existingEmail) {
      console.log('❌ [API] メールアドレス登録済み:', email);
      await redis.quit();
      return res.status(400).json({
        error: 'このメールアドレスは既に登録されています',
        valid: false
      });
    }

    // 検証成功
    console.log('✅ [API] 検証成功:', { token, email });
    await redis.quit();
    return res.status(200).json({
      valid: true,
      message: 'トークンとメールアドレスは有効です'
    });

  } catch (error) {
    console.error('❌ [API] validate-token エラー:', error);
    if (redis) {
      try {
        await redis.quit();
      } catch (quitError) {
        console.error('Redis quit error:', quitError);
      }
    }
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      valid: false,
      details: error.message
    });
  }
}
