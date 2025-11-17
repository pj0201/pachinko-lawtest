/**
 * シンプルなヘルスチェックエンドポイント
 */
export default async function handler(req, res) {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'pachinko-exam-backend',
    message: 'API is working!'
  });
}
