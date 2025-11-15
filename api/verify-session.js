/**
 * セッション検証 API
 * Vercel KV でセッションとデバイスIDを検証
 */
import { kv } from '@vercel/kv';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { sessionToken, deviceId } = req.body;

    if (!sessionToken || !deviceId) {
      return res.status(400).json({
        valid: false,
        error: 'セッション情報が不足しています'
      });
    }

    // KV からセッション情報を取得
    const sessionData = await kv.get(`session:${sessionToken}`);

    if (!sessionData) {
      return res.status(401).json({
        valid: false,
        error: '無効なセッションです'
      });
    }

    // デバイスIDチェック（アカウント流失防止）
    if (sessionData.deviceId !== deviceId) {
      return res.status(403).json({
        valid: false,
        error: 'このアカウントは別のデバイスで登録されています'
      });
    }

    // セッション有効
    return res.status(200).json({
      valid: true,
      user: {
        username: sessionData.username,
        email: sessionData.email,
        registeredAt: sessionData.registeredAt
      }
    });

  } catch (error) {
    return res.status(500).json({
      valid: false,
      error: 'サーバーエラーが発生しました'
    });
  }
}
