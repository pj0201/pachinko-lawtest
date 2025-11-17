/**
 * ユーザー登録API
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
    return res.status(405).json({ error: 'Method not allowed', success: false });
  }

  try {
    const { email, username, token, deviceId } = req.body;
    console.log('🔍 [API] register リクエスト:', { email, username, token, deviceId });

    // 入力検証
    if (!email || !username || !token || !deviceId) {
      console.log('❌ [API] 入力不足:', { email: !!email, username: !!username, token: !!token, deviceId: !!deviceId });
      return res.status(400).json({
        error: '必須項目が入力されていません',
        success: false
      });
    }

    // メールアドレスフォーマット検証
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      console.log('❌ [API] 無効なメールアドレス:', email);
      return res.status(400).json({
        error: '無効なメールアドレスです',
        success: false
      });
    }

    // トークンフォーマットチェック
    const isValidFormat =
      token.startsWith('TEST_') ||
      token.startsWith('ADMIN_') ||
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);

    if (!isValidFormat) {
      console.log('❌ [API] 無効なトークンフォーマット:', token);
      return res.status(400).json({
        error: '無効な招待URLです',
        success: false
      });
    }

    // トークン使用済みチェック（二重チェック）
    const usedTokenStr = await redis.get(`token:${token}`);
    const usedToken = usedTokenStr ? JSON.parse(usedTokenStr) : null;
    console.log('🔍 [API] トークン使用済みチェック:', { token, usedToken });

    if (usedToken) {
      console.log('❌ [API] トークン使用済み:', token);
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        success: false
      });
    }

    // メールアドレス重複チェック（二重チェック）
    const existingEmailStr = await redis.get(`email:${email}`);
    const existingEmail = existingEmailStr ? JSON.parse(existingEmailStr) : null;
    console.log('🔍 [API] メールアドレス重複チェック:', { email, existingEmail });

    if (existingEmail) {
      console.log('❌ [API] メールアドレス登録済み:', email);
      return res.status(400).json({
        error: 'このメールアドレスは既に登録されています',
        success: false
      });
    }

    // セッショントークン生成
    const sessionToken = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);

    // ユーザーデータ
    const userData = {
      username,
      email,
      deviceId,
      inviteToken: token,
      sessionToken,
      registeredAt: new Date().toISOString()
    };

    console.log('🔍 [API] Redis Cloudに保存中:', { email, token, sessionToken });

    // Redis Cloud に保存（永続化）
    await Promise.all([
      // メールアドレスをキーに保存（重複防止）
      redis.set(`email:${email}`, JSON.stringify(userData)),
      // トークンを使用済みに（重複防止）
      redis.set(`token:${token}`, JSON.stringify({
        usedBy: email,
        usedAt: new Date().toISOString()
      })),
      // セッショントークンでも保存（ログイン検証用）
      redis.set(`session:${sessionToken}`, JSON.stringify(userData))
    ]);

    console.log('✅ [API] 登録成功:', { email, sessionToken });

    return res.status(200).json({
      success: true,
      message: '登録が完了しました',
      sessionToken,
      user: {
        username,
        email,
        registeredAt: userData.registeredAt
      }
    });

  } catch (error) {
    console.error('❌ [API] register エラー:', error);
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      success: false,
      details: error.message
    });
  }
}
