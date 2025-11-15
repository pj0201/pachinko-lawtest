/**
 * デバイス検証 - スマホのみ許可
 */

export function isMobileDevice() {
  // 1. User-Agent チェック
  const userAgent = navigator.userAgent.toLowerCase();
  const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);

  // 2. タッチスクリーン対応チェック
  const hasTouchScreen = (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0
  );

  // 3. 画面サイズチェック（横幅が768px以下）
  const isSmallScreen = window.innerWidth <= 768;

  // すべての条件を満たす必要がある
  return isMobileUA && hasTouchScreen && isSmallScreen;
}

export function checkDeviceRestriction() {
  if (!isMobileDevice()) {
    return {
      allowed: false,
      message: 'このアプリはスマートフォン専用です。\nスマートフォンからアクセスしてください。'
    };
  }

  return {
    allowed: true,
    message: ''
  };
}
