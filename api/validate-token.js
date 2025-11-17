/**
 * トークン検証API - Vercel KV版
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
    return res.status(405).json({ error: 'Method not allowed', valid: false });
  }

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

    // メールアドレス形式チェック
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      console.log('❌ [API] 無効なメールアドレス形式:', email);
      return res.status(400).json({
        error: '有効なメールアドレスを入力してください',
        valid: false
      });
    }

    // トークンフォーマットチェック（TEST_, ADMIN_, UUID v4対応）
    const isValidFormat =
      token.startsWith('TEST_') ||
      token.startsWith('ADMIN_') ||
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);

    if (!isValidFormat) {
      console.log('❌ [API] 無効なトークンフォーマット:', token);
      return res.status(400).json({
        error: '無効な招待URLです',
        valid: false
      });
    }

    // Vercel KVからトークン情報を取得
    const tokenKey = `token:${token}`;
    const tokenData = await kv.get(tokenKey);
    console.log('🔍 [API] トークン情報取得:', { tokenKey, found: !!tokenData });

    // トークンが既に使用されているかチェック
    if (tokenData && tokenData.usedBy) {
      console.log('❌ [API] トークン既使用:', { token, usedBy: tokenData.usedBy });
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        valid: false
      });
    }

    // メールアドレスが既に登録されているかチェック
    const emailKey = `email:${email}`;
    const emailData = await kv.get(emailKey);
    console.log('🔍 [API] メールアドレス確認:', { emailKey, found: !!emailData });

    if (emailData) {
      console.log('❌ [API] メールアドレス既登録:', email);
      return res.status(400).json({
        error: 'このメールアドレスは既に登録されています',
        valid: false
      });
    }

    // 開発・テストモード
    if (token.startsWith('TEST_') || token.startsWith('ADMIN_')) {
      console.log('✅ [API] テスト/管理者トークン有効:', token);
      return res.status(200).json({
        valid: true,
        message: '有効な招待URLです'
      });
    }

    // 本番トークン（UUID）の場合
    // トークンが未使用なら有効
    console.log('✅ [API] トークン有効:', token);
    return res.status(200).json({
      valid: true,
      message: '有効な招待URLです'
    });

  } catch (error) {
    console.error('❌ [API] サーバーエラー:', error.message);
    console.error(error.stack);

    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      valid: false,
      details: error.message
    });
  }
}