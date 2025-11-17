/**
 * ユーザー登録API - Vercel KV版
 */
import { kv } from '@vercel/kv';

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
      console.log('❌ [API] 入力不足');
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
    const usedToken = await kv.get(`token:${token}`);
    console.log('🔍 [API] トークン使用済みチェック:', { token, usedToken });

    if (usedToken) {
      console.log('❌ [API] トークン使用済み:', token);
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        success: false
      });
    }

    // メールアドレス重複チェック（二重チェック）
    const existingEmail = await kv.get(`email:${email}`);
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

    console.log('🔍 [API] Vercel KVに保存中:', { email, token, sessionToken });

    // Vercel KV に保存（永続化）
    await Promise.all([
      kv.set(`email:${email}`, userData),
      kv.set(`token:${token}`, {
        usedBy: email,
        usedAt: new Date().toISOString()
      }),
      kv.set(`session:${sessionToken}`, userData)
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
