/**
 * トークン検証 API
 * Vercel KV でトークンとメールアドレスの重複をチェック
 */
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { token, email } = req.body;

    // 入力検証
    if (!token || !email) {
      return res.status(400).json({
        error: 'トークンとメールアドレスが必要です',
        valid: false
      });
    }

    // メールアドレスフォーマット検証
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        error: '無効なメールアドレスです',
        valid: false
      });
    }

    // トークンフォーマットチェック
    if (!token.startsWith('TEST_') && !token.startsWith('ADMIN_')) {
      return res.status(400).json({
        error: '無効な招待URLです',
        valid: false
      });
    }

    // トークン使用済みチェック
    const usedToken = await kv.get(`token:${token}`);
    if (usedToken) {
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        valid: false
      });
    }

    // メールアドレス重複チェック
    const existingEmail = await kv.get(`email:${email}`);
    if (existingEmail) {
      return res.status(400).json({
        error: 'このメールアドレスは既に登録されています',
        valid: false
      });
    }

    // 検証成功
    return res.status(200).json({
      valid: true,
      message: 'トークンとメールアドレスは有効です'
    });

  } catch (error) {
    console.error('Validation error:', error);
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      valid: false
    });
  }
}
