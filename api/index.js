/**
 * Vercelサーバーレス関数 - メインAPIエンドポイント
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { kv } from '@vercel/kv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// ミドルウェア設定
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// デバッグ用：全リクエストをログ
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} (originalUrl: ${req.originalUrl})`);
  next();
});

// データディレクトリ（Vercel環境では相対パスを使用）
const DATA_DIR = path.join(__dirname, '../backend/db');

// ロギング機能
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMsg = `[${timestamp}] [${level}] ${message}`;
  console.log(logMsg);
}

// 問題データローダー
let cachedProblems = null;

function loadProblems() {
  if (cachedProblems) {
    return cachedProblems;
  }

  try {
    const PROBLEMS_FILE = path.join(DATA_DIR, 'problems.json');

    if (!fs.existsSync(PROBLEMS_FILE)) {
      console.error(`問題ファイルが見つかりません: ${PROBLEMS_FILE}`);
      return { problems: [], total_count: 0 };
    }

    const rawData = JSON.parse(fs.readFileSync(PROBLEMS_FILE, 'utf-8'));

    // データ構造を正規化
    const data = {
      problems: rawData.problems || [],
      total_count: rawData.total_count || (rawData.metadata && rawData.metadata.total_count) || 0,
      metadata: rawData.metadata
    };

    cachedProblems = data;
    console.log(`✅ 問題データ読み込み完了: ${data.total_count}問`);
    return data;
  } catch (error) {
    console.error('問題データの読み込みに失敗:', error);
    return { problems: [], total_count: 0 };
  }
}

// ==================== ヘルスチェック ====================
app.get('/api/health', (req, res) => {
  const data = loadProblems();
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'patshinko-exam-backend',
    problems_loaded: data.total_count,
    env_check: {
      KV_REST_API_URL: process.env.KV_REST_API_URL ? 'SET' : 'NOT SET',
      KV_REST_API_TOKEN: process.env.KV_REST_API_TOKEN ? 'SET' : 'NOT SET',
      KV_URL: process.env.KV_URL ? 'SET' : 'NOT SET'
    }
  });
});

// ==================== 問題データエンドポイント ====================
app.get('/api/problems', (req, res) => {
  try {
    const data = loadProblems();
    res.json({
      status: 'success',
      total_count: data.total_count,
      problems: data.problems
    });
  } catch (error) {
    log(`問題取得エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      message: '問題データの取得に失敗しました',
      error: error.message
    });
  }
});

app.get('/api/problems/theme/:themeId', (req, res) => {
  try {
    const themeId = parseInt(req.params.themeId);
    const data = loadProblems();
    const problems = data.problems.filter(p => p.theme_id === themeId);

    res.json({
      status: 'success',
      theme_id: themeId,
      count: problems.length,
      problems: problems
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'テーマ別問題取得に失敗しました',
      error: error.message
    });
  }
});

app.get('/api/problems/category/:category', (req, res) => {
  try {
    const category = req.params.category;
    const data = loadProblems();
    const problems = data.problems.filter(p => p.category === category);

    res.json({
      status: 'success',
      category: category,
      count: problems.length,
      problems: problems
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'カテゴリ別問題取得に失敗しました',
      error: error.message
    });
  }
});

app.get('/api/problems/count', (req, res) => {
  try {
    const data = loadProblems();
    res.json({
      status: 'success',
      total_count: data.total_count
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: '問題総数取得に失敗しました',
      error: error.message
    });
  }
});

app.post('/api/problems/quiz', (req, res) => {
  try {
    const { count = 10, difficulty } = req.body;
    const data = loadProblems();
    let problems = data.problems;

    // 難易度でフィルタリング
    if (difficulty) {
      problems = problems.filter(p => p.difficulty === difficulty);
    }

    // ランダムに指定数取得
    const selected = [];
    const used = new Set();
    while (selected.length < Math.min(count, problems.length)) {
      const randomIndex = Math.floor(Math.random() * problems.length);
      if (!used.has(randomIndex)) {
        selected.push(problems[randomIndex]);
        used.add(randomIndex);
      }
    }

    res.json({
      status: 'success',
      count: selected.length,
      problems: selected
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'クイズ問題取得に失敗しました',
      error: error.message
    });
  }
});

// ==================== 認証エンドポイント ====================

/**
 * POST /api/admin/init-tokens
 * 招待トークンを一括登録（管理者用）
 */
app.post('/api/admin/init-tokens', async (req, res) => {
  try {
    const tokens = [
      '039742a2-f799-4574-8530-a8e1d81960f1',
      'cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb',
      'd0b28ab3-44b6-45aa-897b-e72e0e0da116',
      'babcd6fb-b8a8-46a8-b3a6-fc00966d07a3',
      'b1b281a3-6b76-4659-9827-bf3a07b6c3ba',
      '12f622c2-cbf4-4631-abb7-7336c841b198',
      '3c756c94-0d98-4d8b-b466-17e99f1b3240',
      '2b1d54e2-97a0-4900-a513-fab986540358',
      'd47c9566-cabd-4d96-91d0-41afc10a59b6',
      'c502c94a-3e4e-471e-9835-2f05018751e4'
    ];

    const results = [];

    for (const token of tokens) {
      try {
        await kv.set(`invite:${token}`, {
          token,
          used: false,
          createdAt: new Date().toISOString()
        });
        results.push({ token, status: 'success' });
      } catch (error) {
        results.push({ token, status: 'error', error: error.message });
      }
    }

    log(`✅ 招待トークン初期化完了: ${results.filter(r => r.status === 'success').length}/${tokens.length}`, 'INFO');

    res.json({
      success: true,
      message: '招待トークンを初期化しました',
      total: tokens.length,
      initialized: results.filter(r => r.status === 'success').length,
      results
    });

  } catch (error) {
    log(`招待トークン初期化エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      success: false,
      error: 'トークン初期化に失敗しました',
      details: error.message
    });
  }
});

/**
 * GET /api/admin/check-kv
 * Vercel KVの接続確認
 */
app.get('/api/admin/check-kv', async (req, res) => {
  try {
    // テストキーで書き込み・読み込み
    const testKey = 'test:connection';
    const testValue = { timestamp: new Date().toISOString() };

    await kv.set(testKey, testValue);
    const retrieved = await kv.get(testKey);
    await kv.del(testKey);

    res.json({
      success: true,
      message: 'Vercel KV接続成功',
      test: {
        written: testValue,
        retrieved
      }
    });

  } catch (error) {
    log(`KV接続確認エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      success: false,
      error: 'Vercel KVへの接続に失敗しました',
      details: error.message
    });
  }
});

/**
 * GET /api/admin/list-tokens
 * 登録済み招待トークン一覧を表示
 */
app.get('/api/admin/list-tokens', async (req, res) => {
  try {
    const tokens = [
      '039742a2-f799-4574-8530-a8e1d81960f1',
      'cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb',
      'd0b28ab3-44b6-45aa-897b-e72e0e0da116',
      'babcd6fb-b8a8-46a8-b3a6-fc00966d07a3',
      'b1b281a3-6b76-4659-9827-bf3a07b6c3ba',
      '12f622c2-cbf4-4631-abb7-7336c841b198',
      '3c756c94-0d98-4d8b-b466-17e99f1b3240',
      '2b1d54e2-97a0-4900-a513-fab986540358',
      'd47c9566-cabd-4d96-91d0-41afc10a59b6',
      'c502c94a-3e4e-471e-9835-2f05018751e4'
    ];

    const results = [];

    for (const token of tokens) {
      const data = await kv.get(`invite:${token}`);
      results.push({
        token,
        exists: !!data,
        data: data || null
      });
    }

    res.json({
      success: true,
      total: tokens.length,
      registered: results.filter(r => r.exists).length,
      tokens: results
    });

  } catch (error) {
    log(`トークン一覧取得エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      success: false,
      error: 'トークン一覧の取得に失敗しました',
      details: error.message
    });
  }
});

/**
 * POST /api/validate-token
 * 招待トークンの検証
 */
app.post('/api/validate-token', async (req, res) => {
  try {
    const { token, email } = req.body;

    if (!token) {
      return res.status(400).json({
        valid: false,
        error: 'トークンが指定されていません'
      });
    }

    // Vercel KVからトークン情報を取得
    const tokenData = await kv.get(`invite:${token}`);

    if (!tokenData) {
      return res.status(400).json({
        valid: false,
        error: 'この招待URLは無効です'
      });
    }

    // トークンが既に使用済みかチェック
    if (tokenData.used) {
      return res.status(400).json({
        valid: false,
        error: 'この招待URLは既に使用されています'
      });
    }

    // メールアドレスの重複チェック
    if (email) {
      const existingUser = await kv.get(`user:email:${email}`);
      if (existingUser) {
        return res.status(400).json({
          valid: false,
          error: 'このメールアドレスは既に登録されています'
        });
      }
    }

    res.json({
      valid: true,
      message: '有効な招待URLです'
    });

  } catch (error) {
    log(`トークン検証エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      valid: false,
      error: 'サーバーエラーが発生しました'
    });
  }
});

/**
 * POST /api/register
 * ユーザー登録
 */
app.post('/api/register', async (req, res) => {
  try {
    const { email, username, token, deviceId } = req.body;

    if (!email || !username || !token || !deviceId) {
      return res.status(400).json({
        success: false,
        error: '必須項目が入力されていません'
      });
    }

    // トークン検証
    const tokenData = await kv.get(`invite:${token}`);

    if (!tokenData || tokenData.used) {
      return res.status(400).json({
        success: false,
        error: '無効または使用済みの招待URLです'
      });
    }

    // メールアドレスの重複チェック
    const existingUser = await kv.get(`user:email:${email}`);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        error: 'このメールアドレスは既に登録されています'
      });
    }

    // セッショントークン生成
    const sessionToken = `session_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    // ユーザーデータ作成
    const user = {
      email,
      username,
      deviceId,
      inviteToken: token,
      sessionToken,
      registeredAt: new Date().toISOString()
    };

    // データ保存
    await kv.set(`user:email:${email}`, user);
    await kv.set(`user:device:${deviceId}`, user);
    await kv.set(`session:${sessionToken}`, user);

    // トークンを使用済みにマーク
    await kv.set(`invite:${token}`, {
      ...tokenData,
      used: true,
      usedBy: email,
      usedAt: new Date().toISOString()
    });

    log(`✅ ユーザー登録成功: ${email}`, 'INFO');

    res.json({
      success: true,
      sessionToken,
      user: {
        username: user.username,
        email: user.email,
        registeredAt: user.registeredAt
      }
    });

  } catch (error) {
    log(`登録エラー: ${error.message}`, 'ERROR');
    res.status(500).json({
      success: false,
      error: 'サーバーエラーが発生しました'
    });
  }
});

// ==================== エラーハンドリング ====================
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'エンドポイントが見つかりません',
    error: `${req.method} ${req.path}`
  });
});

app.use((err, req, res, next) => {
  log(`エラーハンドラー: ${err.message}`, 'ERROR');
  res.status(500).json({
    status: 'error',
    message: 'サーバーエラー',
    error: err.message
  });
});

// Vercelサーバーレス関数としてエクスポート
export default app;
