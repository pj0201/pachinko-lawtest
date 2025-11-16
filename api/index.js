/**
 * Vercelサーバーレス関数 - メインAPIエンドポイント
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
