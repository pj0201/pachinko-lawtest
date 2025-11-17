/**
 * セッション検証API - Vercel KV版
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
    const { sessionToken, deviceId } = req.body;
    console.log('🔍 [API] verify-session リクエスト:', { sessionToken, deviceId });

    // 入力検証
    if (!sessionToken || !deviceId) {
      console.log('❌ [API] 入力不足');
      return res.status(400).json({
        valid: false,
        error: 'セッション情報が不足しています'
      });
    }

    // Vercel KV からセッション情報を取得
    const sessionData = await kv.get(`session:${sessionToken}`);
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
