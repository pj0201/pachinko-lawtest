/**
 * ユーザー登録 API
 * Vercel KV でアカウントの独自性を担保
 */
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { email, username, token, deviceId } = req.body;

    // 入力検証
    if (!email || !username || !token || !deviceId) {
      return res.status(400).json({
        error: '必須項目が入力されていません',
        success: false
      });
    }

    // トークンフォーマットチェック
    if (!token.startsWith('TEST_') && !token.startsWith('ADMIN_')) {
      return res.status(400).json({
        error: '無効な招待URLです',
        success: false
      });
    }

    // トークン使用済みチェック（二重チェック）
    const usedToken = await kv.get(`token:${token}`);
    if (usedToken) {
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        success: false
      });
    }

    // メールアドレス重複チェック（二重チェック）
    const existingEmail = await kv.get(`email:${email}`);
    if (existingEmail) {
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

    // KV に保存（永続化）
    await Promise.all([
      // メールアドレスをキーに保存（重複防止）
      kv.set(`email:${email}`, userData),
      // トークンを使用済みに（重複防止）
      kv.set(`token:${token}`, {
        usedBy: email,
        usedAt: new Date().toISOString()
      }),
      // セッショントークンでも保存（ログイン検証用）
      kv.set(`session:${sessionToken}`, userData)
    ]);

    // 登録成功
    return res.status(200).json({
      success: true,
      sessionToken,
      user: {
        username,
        email,
        registeredAt: userData.registeredAt
      }
    });

  } catch (error) {
    console.error('Registration error:', error);
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      success: false
    });
  }
}
