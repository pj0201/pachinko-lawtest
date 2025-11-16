/**
 * データベース操作ルート
 * 問題管理、テスト結果、採点分析
 */

import express from 'express';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();
const DATA_DIR = path.join(__dirname, '../data');

// ==================== ロギング ====================
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${level}] ${message}`);
}

// ==================== 問題インポート ====================
/**
 * POST /api/db/questions/import
 * OCR結果から問題をデータベースにインポート
 */
router.post('/questions/import', async (req, res) => {
  try {
    log('問題インポート開始', 'INFO');

    // OCR結果を取得
    const ocrResultsFile = path.join(DATA_DIR, 'ocr_results.json');
    if (!fs.existsSync(ocrResultsFile)) {
      return res.status(400).json({
        status: 'error',
        message: 'OCR結果ファイルが見つかりません',
        error: 'ocr_results.json が必要です'
      });
    }

    // Pythonスクリプトでカテゴリー分類 + DB挿入を実行
    const classifierScript = path.join(__dirname, '../pdf_categorizer.py');

    return new Promise((resolve) => {
      const pythonProcess = spawn('python3', [classifierScript], {
        cwd: __dirname,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1'
        }
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          log('問題インポート成功', 'INFO');

          // 分類結果を読み込み
          const classifiedFile = path.join(DATA_DIR, 'classified_questions.json');
          const classified = JSON.parse(fs.readFileSync(classifiedFile, 'utf-8'));

          resolve(res.json({
            status: 'success',
            message: '問題インポート完了',
            data: {
              total_questions: classified.total_questions,
              by_category: classified.statistics,
              questions_file: classifiedFile
            }
          }));
        } else {
          log(`問題インポート失敗 (コード:${code})`, 'ERROR');
          resolve(res.status(500).json({
            status: 'error',
            message: '問題インポート失敗',
            error: stderr.substring(0, 200)
          }));
        }
      });
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      message: 'サーバーエラー',
      error: err.message
    });
  }
});

// ==================== 問題取得 ====================
/**
 * GET /api/db/questions
 * 全問題を取得
 */
router.get('/questions', (req, res) => {
  try {
    const classifiedFile = path.join(DATA_DIR, 'classified_questions.json');

    if (!fs.existsSync(classifiedFile)) {
      return res.status(404).json({
        status: 'error',
        message: '問題データが見つかりません'
      });
    }

    const data = JSON.parse(fs.readFileSync(classifiedFile, 'utf-8'));
    const limit = parseInt(req.query.limit) || 100;
    const offset = parseInt(req.query.offset) || 0;

    const paginated = {
      total: data.total_questions,
      limit,
      offset,
      count: data.questions.slice(offset, offset + limit).length,
      questions: data.questions.slice(offset, offset + limit)
    };

    res.json({
      status: 'success',
      data: paginated
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

// ==================== カテゴリー別問題取得 ====================
/**
 * GET /api/db/questions/category/:category
 * カテゴリー別に問題を取得
 */
router.get('/questions/category/:category', (req, res) => {
  try {
    const { category } = req.params;
    const classifiedFile = path.join(DATA_DIR, 'classified_questions.json');

    if (!fs.existsSync(classifiedFile)) {
      return res.status(404).json({
        status: 'error',
        message: '問題データが見つかりません'
      });
    }

    const data = JSON.parse(fs.readFileSync(classifiedFile, 'utf-8'));
    const filtered = data.questions.filter(q => q.category === category);

    res.json({
      status: 'success',
      data: {
        category,
        total: filtered.length,
        questions: filtered
      }
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

// ==================== テスト結果保存 ====================
/**
 * POST /api/db/test-results
 * テスト結果を保存
 */
router.post('/test-results', async (req, res) => {
  try {
    const { userId, answers, completionTime, testQuestions } = req.body;

    if (!answers || !testQuestions) {
      return res.status(400).json({
        status: 'error',
        message: 'answers と testQuestions は必須です'
      });
    }

    // Python採点スクリプトを実行
    const scoringScript = path.join(__dirname, '../scoring_analyzer.py');

    // テストデータをJSON形式で作成
    const testDataFile = path.join(DATA_DIR, `test_data_${Date.now()}.json`);
    fs.writeFileSync(testDataFile, JSON.stringify({
      user_id: userId || 'anonymous',
      questions: testQuestions,
      answers: answers,
      completion_time: completionTime
    }));

    return new Promise((resolve) => {
      const pythonProcess = spawn('python3', [scoringScript], {
        cwd: __dirname,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1',
          TEST_DATA_FILE: testDataFile
        }
      });

      let stdout = '';
      pythonProcess.stdout.on('data', (data) => { stdout += data.toString(); });
      pythonProcess.stderr.on('data', (data) => { log(data.toString(), 'PYTHON_ERROR'); });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          log('採点完了', 'INFO');

          resolve(res.json({
            status: 'success',
            message: '采点完了',
            data: {
              test_id: `test_${Date.now()}`,
              user_id: userId || 'anonymous'
            }
          }));

          // 一時ファイルを削除
          fs.unlink(testDataFile, () => {});
        } else {
          resolve(res.status(500).json({
            status: 'error',
            message: '采点失敗'
          }));
        }
      });
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

// ==================== 統計情報 ====================
/**
 * GET /api/db/statistics
 * 全体統計情報を取得
 */
router.get('/statistics', (req, res) => {
  try {
    const classifiedFile = path.join(DATA_DIR, 'classified_questions.json');

    if (!fs.existsSync(classifiedFile)) {
      return res.json({
        status: 'success',
        data: {
          total_questions: 0,
          by_category: {},
          message: 'データなし'
        }
      });
    }

    const data = JSON.parse(fs.readFileSync(classifiedFile, 'utf-8'));

    res.json({
      status: 'success',
      data: {
        total_questions: data.total_questions,
        by_category: data.statistics,
        last_updated: data.timestamp
      }
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

// ==================== ランダム問題取得 ====================
/**
 * GET /api/db/questions/random
 * ランダムに問題を取得（テスト用）
 */
router.get('/questions/random', (req, res) => {
  try {
    const count = parseInt(req.query.count) || 10;
    const category = req.query.category;

    const classifiedFile = path.join(DATA_DIR, 'classified_questions.json');

    if (!fs.existsSync(classifiedFile)) {
      return res.status(404).json({
        status: 'error',
        message: '問題データが見つかりません'
      });
    }

    let data = JSON.parse(fs.readFileSync(classifiedFile, 'utf-8'));
    let questions = data.questions;

    // カテゴリーフィルター
    if (category) {
      questions = questions.filter(q => q.category === category);
    }

    // ランダムに選択
    const shuffled = questions.sort(() => 0.5 - Math.random()).slice(0, count);

    res.json({
      status: 'success',
      data: {
        count: shuffled.length,
        questions: shuffled
      }
    });

  } catch (err) {
    log(`エラー: ${err.message}`, 'ERROR');
    res.status(500).json({
      status: 'error',
      error: err.message
    });
  }
});

export default router;
