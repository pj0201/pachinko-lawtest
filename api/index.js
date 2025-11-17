/**
 * Vercelサーバーレス関数 - メインAPIエンドポイント
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import Redis from 'ioredis';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Redis接続（REDIS_URLまたはKV_URLを使用）
const redis = new Redis(process.env.REDIS_URL || process.env.KV_URL || {
  host: 'localhost',
  port: 6379
});

const app = express();

// ミドルウェア設定
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

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
    problems_loaded: data.total_count
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

// ==================== 認証・登録エンドポイント ====================

/**
 * トークン検証 API
 * Vercel KV でトークンとメールアドレスの重複をチェック
 */
app.post('/api/validate-token', async (req, res) => {
  try {
    const { token, email } = req.body;
    console.log('🔍 [API] validate-token リクエスト:', { token, email });

    // 入力検証
    if (!token || !email) {
      console.error('❌ [API] トークンまたはメールアドレスが欠落');
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

    // トークンフォーマットチェック（TEST_、ADMIN_、またはUUID形式）
    const isValidFormat =
      token.startsWith('TEST_') ||
      token.startsWith('ADMIN_') ||
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);

    console.log('🔍 [API] トークン形式チェック:', { token, isValidFormat });

    if (!isValidFormat) {
      console.error('❌ [API] 無効なトークン形式:', token);
      return res.status(400).json({
        error: '無効な招待URLです',
        valid: false
      });
    }

    // トークン使用済みチェック
    const usedTokenStr = await redis.get(`token:${token}`);
    if (usedTokenStr) {
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        valid: false
      });
    }

    // メールアドレス重複チェック
    const existingEmailStr = await redis.get(`email:${email}`);
    if (existingEmailStr) {
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
    log(`トークン検証エラー: ${error.message}`, 'ERROR');
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      valid: false
    });
  }
});

/**
 * ユーザー登録 API
 * Vercel KV でアカウントの独自性を担保
 */
app.post('/api/register', async (req, res) => {
  try {
    const { email, username, token, deviceId } = req.body;

    // 入力検証
    if (!email || !username || !token || !deviceId) {
      return res.status(400).json({
        error: '必須項目が入力されていません',
        success: false
      });
    }

    // メールアドレスフォーマット検証
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        error: '無効なメールアドレスです',
        success: false
      });
    }

    // トークンフォーマットチェック（TEST_、ADMIN_、またはUUID形式）
    const isValidFormat =
      token.startsWith('TEST_') ||
      token.startsWith('ADMIN_') ||
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(token);

    if (!isValidFormat) {
      return res.status(400).json({
        error: '無効な招待URLです',
        success: false
      });
    }

    // トークン使用済みチェック（二重チェック）
    const usedTokenStr = await redis.get(`token:${token}`);
    if (usedTokenStr) {
      return res.status(400).json({
        error: 'この招待URLは既に使用されています',
        success: false
      });
    }

    // メールアドレス重複チェック（二重チェック）
    const existingEmailStr = await redis.get(`email:${email}`);
    if (existingEmailStr) {
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

    // Redis に保存（永続化）
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

    log(`✅ ユーザー登録成功: ${email}`, 'INFO');

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
    log(`登録エラー: ${error.message}`, 'ERROR');
    return res.status(500).json({
      error: 'サーバーエラーが発生しました',
      success: false
    });
  }
});

/**
 * セッション検証 API
 * Vercel KV でセッションとデバイスIDを検証
 */
app.post('/api/verify-session', async (req, res) => {
  try {
    const { sessionToken, deviceId } = req.body;

    if (!sessionToken || !deviceId) {
      return res.status(400).json({
        valid: false,
        error: 'セッション情報が不足しています'
      });
    }

    // Redis からセッション情報を取得
    const sessionDataStr = await redis.get(`session:${sessionToken}`);

    if (!sessionDataStr) {
      return res.status(401).json({
        valid: false,
        error: '無効なセッションです'
      });
    }

    const sessionData = JSON.parse(sessionDataStr);

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
    log(`セッション検証エラー: ${error.message}`, 'ERROR');
    return res.status(500).json({
      valid: false,
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
