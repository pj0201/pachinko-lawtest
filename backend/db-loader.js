/**
 * データベースローダー
 * バックエンド起動時に問題データを読み込む
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_DIR = path.join(__dirname, './db');
const PROBLEMS_FILE = path.join(DATA_DIR, 'problems.json');

let cachedProblems = null;

/**
 * 問題データを読み込む
 */
function loadProblems() {
  if (cachedProblems) {
    return cachedProblems;
  }

  try {
    if (!fs.existsSync(PROBLEMS_FILE)) {
      console.error(`問題ファイルが見つかりません: ${PROBLEMS_FILE}`);
      return { problems: [], total_count: 0 };
    }

    const rawData = JSON.parse(fs.readFileSync(PROBLEMS_FILE, 'utf-8'));

    // データ構造を正規化（metadata.total_countまたはtotal_countをサポート）
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

/**
 * 全問題を取得
 */
function getAllProblems() {
  const data = loadProblems();
  return data.problems || [];
}

/**
 * 特定のテーマの問題を取得
 */
function getProblemsByTheme(themeId) {
  const problems = getAllProblems();
  return problems.filter(p => p.theme_id === themeId);
}

/**
 * 特定のカテゴリの問題を取得
 */
function getProblemsByCategory(category) {
  const problems = getAllProblems();
  return problems.filter(p => p.category === category);
}

/**
 * 問題総数を取得
 */
function getTotalCount() {
  const data = loadProblems();
  return data.total_count || 0;
}

/**
 * キャッシュをクリア
 */
function clearCache() {
  cachedProblems = null;
}

export {
  loadProblems,
  getAllProblems,
  getProblemsByTheme,
  getProblemsByCategory,
  getTotalCount,
  clearCache
};
