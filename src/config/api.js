/**
 * API設定ファイル
 * GitHub PagesとVercel環境両方に対応
 */

// API Base URLの決定
// 1. 環境変数が設定されていればそれを使用
// 2. GitHub Pagesの場合はVercel APIを使用
// 3. それ以外（ローカル開発など）は相対パスを使用
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (window.location.hostname === 'pj0201.github.io'
    ? 'https://pachinko-lawtest.vercel.app/api'
    : '/api');

// デバッグ用ログ
console.log('🔧 API Base URL:', API_BASE_URL);
console.log('🔧 Current hostname:', window.location.hostname);

/**
 * APIエンドポイント定義
 */
export const apiEndpoints = {
  // ヘルスチェック
  health: `${API_BASE_URL}/health`,

  // 認証関連
  validateToken: `${API_BASE_URL}/validate-token`,
  register: `${API_BASE_URL}/register`,
  verifySession: `${API_BASE_URL}/verify-session`,

  // 問題関連
  problems: `${API_BASE_URL}/problems`,
  problemsTheme: (themeId) => `${API_BASE_URL}/problems/theme/${themeId}`,
  problemsCategory: (category) => `${API_BASE_URL}/problems/category/${category}`,
  problemsCount: `${API_BASE_URL}/problems/count`,
  problemsQuiz: `${API_BASE_URL}/problems/quiz`,

  // 成績・履歴関連
  saveResult: `${API_BASE_URL}/save-result`,
  getHistory: `${API_BASE_URL}/history`
};

/**
 * 共通のfetchオプション
 */
export const fetchOptions = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

/**
 * APIリクエストヘルパー関数
 */
export async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, {
      ...fetchOptions,
      ...options,
      headers: {
        ...fetchOptions.headers,
        ...(options.headers || {})
      }
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('❌ APIエラー:', response.status, data);
      throw new Error(data.error || `APIエラー: ${response.status}`);
    }

    return { success: true, data };
  } catch (error) {
    console.error('❌ APIリクエストエラー:', error);
    return { success: false, error: error.message };
  }
}

export default {
  apiEndpoints,
  fetchOptions,
  apiRequest,
  API_BASE_URL
};