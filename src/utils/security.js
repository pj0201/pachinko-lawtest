/**
 * フロントエンドセキュリティユーティリティ
 * プロアクティブディフェンス実装
 */

// ===== XSS対策 =====

/**
 * HTMLエスケープ（XSS防止）
 *
 * @param {string} str - エスケープする文字列
 * @returns {string} エスケープされた文字列
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
 * URLのサニタイズ（JavaScriptプロトコル防止）
 *
 * @param {string} url - チェックするURL
 * @returns {string|null} 安全なURL、または危険な場合はnull
 */
export function sanitizeUrl(url) {
  if (!url) return null;

  // 危険なプロトコルをブロック
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:', 'file:'];
  const lowerUrl = url.toLowerCase().trim();

  for (const protocol of dangerousProtocols) {
    if (lowerUrl.startsWith(protocol)) {
      console.warn('🔒 危険なURLがブロックされました:', url);
      return null;
    }
  }

  return url;
}

// ===== 入力検証 =====

/**
 * メールアドレスの検証
 *
 * @param {string} email - 検証するメールアドレス
 * @returns {boolean} 有効な場合true
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false;

  // 基本的なメール形式チェック
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 254;
}

/**
 * パスワードの強度チェック
 *
 * @param {string} password - チェックするパスワード
 * @returns {object} {valid: boolean, strength: string, message: string}
 */
export function validatePassword(password) {
  if (!password || typeof password !== 'string') {
    return { valid: false, strength: 'weak', message: 'パスワードを入力してください' };
  }

  // 最小長チェック
  if (password.length < 8) {
    return { valid: false, strength: 'weak', message: 'パスワードは8文字以上必要です' };
  }

  // 強度チェック
  let strength = 0;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^a-zA-Z0-9]/.test(password)) strength++;

  if (strength >= 4) {
    return { valid: true, strength: 'strong', message: '強力なパスワードです' };
  } else if (strength >= 3) {
    return { valid: true, strength: 'medium', message: '中程度の強度です' };
  } else {
    return { valid: false, strength: 'weak', message: '大文字、小文字、数字、記号を組み合わせてください' };
  }
}

/**
 * デバイスIDの検証
 *
 * @param {string} deviceId - 検証するデバイスID
 * @returns {boolean} 有効な場合true
 */
export function validateDeviceId(deviceId) {
  if (!deviceId || typeof deviceId !== 'string') return false;

  // UUID形式または英数字のみ許可
  const validPattern = /^[a-zA-Z0-9\-_]+$/;
  return validPattern.test(deviceId) && deviceId.length >= 16 && deviceId.length <= 128;
}

// ===== セッション管理 =====

/**
 * セッショントークンの安全な保存
 *
 * @param {string} token - セッショントークン
 * @param {string} deviceId - デバイスID
 */
export function saveSession(token, deviceId) {
  if (!token || !deviceId) {
    console.error('🔒 無効なセッション情報');
    return;
  }

  try {
    // localStorage に暗号化して保存（簡易実装）
    const sessionData = {
      token,
      deviceId,
      createdAt: new Date().toISOString(),
      lastAccess: new Date().toISOString()
    };

    localStorage.setItem('session_token', token);
    localStorage.setItem('device_id', deviceId);
    localStorage.setItem('session_data', JSON.stringify(sessionData));

    console.log('✅ セッションが保存されました');
  } catch (error) {
    console.error('🔒 セッション保存エラー:', error);
  }
}

/**
 * セッショントークンの取得
 *
 * @returns {object|null} {token, deviceId} または null
 */
export function getSession() {
  try {
    const token = localStorage.getItem('session_token');
    const deviceId = localStorage.getItem('device_id');
    const sessionDataStr = localStorage.getItem('session_data');

    if (!token || !deviceId) return null;

    // セッション有効期限チェック（30日）
    if (sessionDataStr) {
      const sessionData = JSON.parse(sessionDataStr);
      const createdAt = new Date(sessionData.createdAt);
      const now = new Date();
      const daysSinceCreation = (now - createdAt) / (1000 * 60 * 60 * 24);

      if (daysSinceCreation > 30) {
        console.warn('🔒 セッションが期限切れです');
        clearSession();
        return null;
      }

      // 最終アクセス日時を更新
      sessionData.lastAccess = now.toISOString();
      localStorage.setItem('session_data', JSON.stringify(sessionData));
    }

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
    localStorage.removeItem('session_data');
    console.log('✅ セッションがクリアされました');
  } catch (error) {
    console.error('🔒 セッションクリアエラー:', error);
  }
}

// ===== CSRF対策 =====

/**
 * CSRFトークンの生成
 *
 * @returns {string} CSRFトークン
 */
export function generateCSRFToken() {
  // ランダムなトークン生成
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * CSRFトークンの保存
 *
 * @param {string} token - CSRFトークン
 */
export function saveCSRFToken(token) {
  sessionStorage.setItem('csrf_token', token);
}

/**
 * CSRFトークンの取得
 *
 * @returns {string|null} CSRFトークン
 */
export function getCSRFToken() {
  return sessionStorage.getItem('csrf_token');
}

// ===== API呼び出しラッパー =====

/**
 * 安全なAPIリクエスト（セキュリティヘッダー付与）
 *
 * @param {string} url - APIエンドポイント
 * @param {object} options - fetchオプション
 * @returns {Promise<Response>} レスポンス
 */
export async function secureApiRequest(url, options = {}) {
  // セッション情報を取得
  const session = getSession();

  // デフォルトヘッダー
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  // セッショントークンがある場合は追加
  if (session) {
    headers['Authorization'] = `Bearer ${session.token}`;
  }

  // CSRF トークンを追加（POST, PUT, DELETE の場合）
  if (['POST', 'PUT', 'DELETE'].includes(options.method?.toUpperCase())) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      headers['X-CSRF-Token'] = csrfToken;
    }
  }

  // リクエスト実行
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    // 401 (Unauthorized) の場合はセッションをクリア
    if (response.status === 401) {
      console.warn('🔒 認証エラー: セッションをクリアします');
      clearSession();
    }

    return response;
  } catch (error) {
    console.error('🔒 APIリクエストエラー:', error);
    throw error;
  }
}

// ===== コンテンツセキュリティ =====

/**
 * 問題テキストのサニタイズ
 *
 * @param {string} text - 問題テキスト
 * @returns {string} サニタイズされたテキスト
 */
export function sanitizeProblemText(text) {
  if (!text || typeof text !== 'string') return '';

  // HTMLタグを除去（許可されたタグ以外）
  const allowedTags = ['b', 'i', 'u', 'br'];
  let sanitized = text;

  // スクリプトタグを完全に削除
  sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');

  // イベントハンドラを削除
  sanitized = sanitized.replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '');

  return sanitized;
}

/**
 * ユーザー入力の長さ制限
 *
 * @param {string} input - ユーザー入力
 * @param {number} maxLength - 最大長
 * @returns {string} 制限された文字列
 */
export function limitInputLength(input, maxLength = 1000) {
  if (!input || typeof input !== 'string') return '';
  return input.slice(0, maxLength);
}

// ===== デバッグ・監視 =====

/**
 * セキュリティイベントのログ記録
 *
 * @param {string} eventType - イベントタイプ
 * @param {object} details - 詳細情報
 */
export function logSecurityEvent(eventType, details = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    eventType,
    details,
    userAgent: navigator.userAgent,
    url: window.location.href
  };

  // コンソールに出力（開発環境）
  if (process.env.NODE_ENV === 'development') {
    console.log('🔒 [SECURITY]', logEntry);
  }

  // 本番環境では外部ログサービスに送信推奨
  // 例: Sentry, LogRocket, etc.
}

// ===== セキュリティチェック =====

/**
 * ブラウザセキュリティ機能のチェック
 *
 * @returns {object} セキュリティ機能の有効状態
 */
export function checkBrowserSecurity() {
  return {
    localStorage: typeof localStorage !== 'undefined',
    sessionStorage: typeof sessionStorage !== 'undefined',
    crypto: typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function',
    https: window.location.protocol === 'https:',
    cookieEnabled: navigator.cookieEnabled
  };
}

/**
 * セキュリティ初期化（アプリ起動時に実行）
 */
export function initSecurity() {
  // ブラウザセキュリティチェック
  const securityStatus = checkBrowserSecurity();

  console.log('🔒 セキュリティ機能チェック:', securityStatus);

  // HTTPS警告（本番環境）
  if (process.env.NODE_ENV === 'production' && !securityStatus.https) {
    console.warn('⚠️ 警告: HTTPSを使用していません。本番環境ではHTTPSを推奨します。');
  }

  // 古いセッションのクリーンアップ
  try {
    const session = getSession();
    if (!session) {
      clearSession();
    }
  } catch (error) {
    console.error('🔒 セッション初期化エラー:', error);
  }

  console.log('✅ フロントエンドセキュリティが初期化されました');
}

// ===== エクスポート =====

export default {
  // XSS対策
  escapeHtml,
  sanitizeUrl,

  // 入力検証
  validateEmail,
  validatePassword,
  validateDeviceId,

  // セッション管理
  saveSession,
  getSession,
  clearSession,

  // CSRF対策
  generateCSRFToken,
  saveCSRFToken,
  getCSRFToken,

  // API呼び出し
  secureApiRequest,

  // コンテンツセキュリティ
  sanitizeProblemText,
  limitInputLength,

  // 監視
  logSecurityEvent,
  checkBrowserSecurity,
  initSecurity
};
