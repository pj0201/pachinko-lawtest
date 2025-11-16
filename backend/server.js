/**
 * 主任者試験アプリ バックエンドサーバー
 * PDF OCR処理エンドポイント提供
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import databaseRoutes from './database_routes.js';
import * as dbLoader from './db-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3001;

// ミドルウェア設定
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// ロギング機能
const DATA_DIR = path.join(__dirname, '../data');
const LOG_FILE = path.join(DATA_DIR, 'backend.log');

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMsg = `[${timestamp}] [${level}] ${message}`;
  console.log(logMsg);
  fs.appendFileSync(LOG_FILE, logMsg + '\n', { encoding: 'utf-8' });
}

// ==================== 問題データエンドポイント ====================
/**
 * GET /api/problems
 * 全問題データを取得
 */
app.get('/api/problems', (req, res) => {
  try {
    const problems = dbLoader.getAllProblems();
    res.json({
      status: 'success',
      total_count: dbLoader.getTotalCount(),
      problems: problems
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

/**
 * GET /api/problems/theme/:themeId
 * 特定のテーマの問題を取得
 */
app.get('/api/problems/theme/:themeId', (req, res) => {
  try {
    const themeId = parseInt(req.params.themeId);
    const problems = dbLoader.getProblemsByTheme(themeId);
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

/**
 * GET /api/problems/category/:category
 * 特定のカテゴリの問題を取得
 */
app.get('/api/problems/category/:category', (req, res) => {
  try {
    const category = req.params.category;
    const problems = dbLoader.getProblemsByCategory(category);
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

/**
 * GET /api/problems/count
 * 問題総数を取得
 */
app.get('/api/problems/count', (req, res) => {
  try {
    const count = dbLoader.getTotalCount();
    res.json({
      status: 'success',
      total_count: count
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: '問題総数取得に失敗しました',
      error: error.message
    });
  }
});

/**
 * POST /api/problems/quiz
 * 難易度指定で問題を取得（クイズモード用）
 */
app.post('/api/problems/quiz', (req, res) => {
  try {
    const { count = 10, difficulty } = req.body;
    let problems = dbLoader.getAllProblems();

    // 難易度でフィルタリング（難易度フィールドがある場合）
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

// ==================== ヘルスチェック ====================
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'patshinko-exam-backend',
    problems_loaded: dbLoader.getTotalCount()
  });
});

// ==================== OCR処理エンドポイント ====================
/**
 * POST /api/pdf-ocr
 * 3つのPDFを全て OCR処理して JSON形式で返す
 *
 * Request body: なし（PDFパスはサーバー側で固定）
 *
 * Response:
 * {
 *   "status": "success|processing|error",
 *   "message": "説明",
 *   "data": {
 *     "total_pages": 400,
 *     "processed_pages": 50,
 *     "output_file": "/path/to/ocr_results.json"
 *   },
 *   "error": null
 * }
 */
app.post('/api/pdf-ocr', async (req, res) => {
  const requestId = Math.random().toString(36).substr(2, 9);
  log(`[${requestId}] OCR処理リクエスト受信`, 'INFO');

  try {
    const ocrScript = path.join(__dirname, '../pdf_ocr_robust.py');
    const outputFile = path.join(DATA_DIR, 'ocr_results.json');

    // 既存の結果がある場合はスキップ
    if (fs.existsSync(outputFile)) {
      log(`[${requestId}] 既存の結果ファイルを使用`, 'INFO');
      const results = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
      return res.json({
        status: 'success',
        message: 'OCR処理完了（キャッシュ）',
        data: {
          total_pages: results.length,
          processed_pages: results.length,
          output_file: outputFile
        },
        error: null
      });
    }

    // Python スクリプト実行（非同期）
    log(`[${requestId}] Python OCR処理開始`, 'INFO');

    return new Promise((resolve) => {
      const pythonProcess = spawn('python3', [ocrScript], {
        cwd: __dirname,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1'
        },
        timeout: 3600000  // 1時間のタイムアウト
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        // ログをバックエンドログにも記録
        data.toString().split('\n').forEach(line => {
          if (line.trim()) {
            log(`[${requestId}] ${line}`, 'PYTHON');
          }
        });
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        log(`[${requestId}] STDERR: ${data.toString()}`, 'ERROR');
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          log(`[${requestId}] Python処理成功（コード:${code}）`, 'INFO');

          // 結果ファイル確認
          if (fs.existsSync(outputFile)) {
            const results = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
            log(`[${requestId}] 結果: ${results.length}ページ処理完了`, 'INFO');

            resolve(res.json({
              status: 'success',
              message: 'OCR処理完了',
              data: {
                total_pages: results.length,
                processed_pages: results.length,
                output_file: outputFile
              },
              error: null
            }));
          } else {
            log(`[${requestId}] 結果ファイルが見つかりません`, 'ERROR');
            resolve(res.status(500).json({
              status: 'error',
              message: '結果ファイル生成失敗',
              data: null,
              error: '結果ファイルが見つかりません'
            }));
          }
        } else {
          log(`[${requestId}] Python処理失敗（コード:${code}）`, 'ERROR');
          log(`[${requestId}] STDERR: ${stderr}`, 'ERROR');
          resolve(res.status(500).json({
            status: 'error',
            message: 'OCR処理エラー',
            data: null,
            error: `Python処理エラー (コード:${code}): ${stderr.substring(0, 200)}`
          }));
        }
      });

      pythonProcess.on('error', (err) => {
        log(`[${requestId}] プロセスエラー: ${err}`, 'ERROR');
        resolve(res.status(500).json({
          status: 'error',
          message: 'プロセス実行エラー',
          data: null,
          error: err.message
        }));
      });
    });

  } catch (err) {
    log(`[${requestId}] エラー: ${err.message}`, 'ERROR');
    log(err.stack, 'ERROR');

    res.status(500).json({
      status: 'error',
      message: 'サーバーエラー',
      data: null,
      error: err.message
    });
  }
});

// ==================== 結果取得エンドポイント ====================
/**
 * GET /api/pdf-ocr/results
 * OCR処理結果を取得
 */
app.get('/api/pdf-ocr/results', (req, res) => {
  try {
    const outputFile = path.join(DATA_DIR, 'ocr_results.json');

    if (!fs.existsSync(outputFile)) {
      return res.status(404).json({
        status: 'error',
        message: 'OCR結果がまだ存在しません',
        data: null,
        error: '結果ファイルが見つかりません'
      });
    }

    const results = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));

    res.json({
      status: 'success',
      message: 'OCR結果取得成功',
      data: {
        total_pages: results.length,
        results: results
      },
      error: null
    });

  } catch (err) {
    log(`結果取得エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      message: 'OCR結果取得エラー',
      data: null,
      error: err.message
    });
  }
});

// ==================== 統計情報エンドポイント ====================
/**
 * GET /api/pdf-ocr/stats
 * OCR処理の統計情報取得
 */
app.get('/api/pdf-ocr/stats', (req, res) => {
  try {
    const outputFile = path.join(DATA_DIR, 'ocr_results.json');

    if (!fs.existsSync(outputFile)) {
      return res.json({
        status: 'success',
        message: 'OCR処理未実行',
        data: {
          total_pages: 0,
          processed_pages: 0,
          avg_chars_per_page: 0,
          status: 'not_started'
        }
      });
    }

    const results = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
    const totalChars = results.reduce((sum, r) => sum + (r.text || '').length, 0);

    res.json({
      status: 'success',
      message: 'OCR統計情報取得成功',
      data: {
        total_pages: results.length,
        processed_pages: results.length,
        avg_chars_per_page: results.length > 0 ? Math.round(totalChars / results.length) : 0,
        total_chars: totalChars,
        status: 'completed'
      }
    });

  } catch (err) {
    log(`統計取得エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      message: '統計取得エラー',
      error: err.message
    });
  }
});

// ==================== ログ取得エンドポイント ====================
app.get('/api/logs', (req, res) => {
  try {
    if (!fs.existsSync(LOG_FILE)) {
      return res.json({ logs: [] });
    }

    const logs = fs.readFileSync(LOG_FILE, 'utf-8').split('\n').filter(line => line.trim());
    const last50 = logs.slice(-50);  // 最後の50行

    res.json({
      status: 'success',
      logs: last50
    });

  } catch (err) {
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

// ==================== データベースルート ====================
// /api/db 配下にすべてのDB操作エンドポイントをマウント
app.use('/api/db', databaseRoutes);

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

// ==================== サーバー起動 ====================
app.listen(PORT, () => {
  log(`🚀 バックエンドサーバー起動: http://localhost:${PORT}`, 'INFO');
  log(`📁 データディレクトリ: ${DATA_DIR}`, 'INFO');
  log(`📊 ログファイル: ${LOG_FILE}`, 'INFO');
});
