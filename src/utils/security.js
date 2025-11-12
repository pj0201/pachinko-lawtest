/**
 * シンプルなセキュリティユーティリティ - スマホアプリ向け
 * 最低限の保護のみ実装
 */

// ===== XSS対策 =====

/**
 * HTMLエスケープ（XSS防止）
 */
export function escapeHtml(str) {
  if (typeof str !== 'string') return '';

  const htmlEscapes = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };

  return str.replace(/[&<>"'/]/g, (match) => htmlEscapes[match]);
}

/**
 * 問題テキストのサニタイズ
 */
export function sanitizeProblemText(text) {
  if (!text || typeof text !== 'string') return '';

  // スクリプトタグを完全に削除
  let sanitized = text.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');

  // イベントハンドラを削除
  sanitized = sanitized.replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '');

  return sanitized;
}

// ===== シンプルなセッション管理 =====

/**
 * セッショントークンの保存
 */
export function saveSession(token, deviceId) {
  if (!token || !deviceId) {
    console.error('🔒 無効なセッション情報');
    return;
  }

  try {
    localStorage.setItem('session_token', token);
    localStorage.setItem('device_id', deviceId);
    console.log('✅ セッションが保存されました');
  } catch (error) {
    console.error('🔒 セッション保存エラー:', error);
  }
}

/**
 * セッショントークンの取得
 */
export function getSession() {
  try {
    const token = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');

    if (!token || !deviceId) return null;

    return { token, deviceId };
  } catch (error) {
    console.error('🔒 セッション取得エラー:', error);
    return null;
  }
}

/**
 * セッションのクリア
 */
export function clearSession() {
  try {
    localStorage.removeItem('session_token');
    localStorage.removeItem('device_id');
    console.log('✅ セッションがクリアされました');
  } catch (error) {
    console.error('🔒 セッションクリアエラー:', error);
  }
}

// ===== 基本的な入力検証 =====

/**
 * メールアドレスの検証
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 254;
}

/**
 * ユーザー入力の長さ制限
 */
export function limitInputLength(input, maxLength = 1000) {
  if (!input || typeof input !== 'string') return '';
  return input.slice(0, maxLength);
}

// ===== 初期化 =====

/**
 * セキュリティ初期化（アプリ起動時に実行）
 */
export function initSecurity() {
  console.log('✅ セキュリティが初期化されました（シンプル版）');
}

// ===== エクスポート =====

export default {
  // XSS対策
  escapeHtml,
  sanitizeProblemText,

  // セッション管理
  saveSession,
  getSession,
  clearSession,

  // 入力検証
  validateEmail,
  limitInputLength,

  // 初期化
  initSecurity
};
