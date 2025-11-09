/**
 * カテゴリ名マッピング定数
 * 全画面で共通使用するカテゴリ名の定義
 */

// フルネーム（デスクトップ・詳細表示用）
export const CATEGORY_NAMES = {
  // 新カテゴリID
  'qualification_system': '遊技機取扱主任者制度と資格維持',
  'game_machine_technical_standards': '遊技機規制技術基準（射幸性・技術）',
  'supervisor_duties_and_guidance': '主任者の実務、指導及び業界要綱',
  'business_regulation_and_obligations': '風俗営業の一般規制と義務',
  'administrative_procedures_and_penalties': '行政手続、構造基準及び罰則',

  // 古いカテゴリID対応（ローカルストレージ互換性）
  'system_and_test': '遊技機取扱主任者制度と資格維持',
  'business_law': '風俗営業の一般規制と義務',
  'game_machine_standards': '遊技機規制技術基準（射幸性・技術）',
  'supervisor_duties': '主任者の実務、指導及び業界要綱',
  'final_problems': '行政手続、構造基準及び罰則'
};

// 短縮名（モバイル用）
export const SHORT_CATEGORY_NAMES = {
  // 新カテゴリID
  'qualification_system': '主任者制度',
  'game_machine_technical_standards': '技術基準',
  'supervisor_duties_and_guidance': '実務指導',
  'business_regulation_and_obligations': '営業規制',
  'administrative_procedures_and_penalties': '行政手続',

  // 古いカテゴリID対応
  'system_and_test': '主任者制度',
  'business_law': '営業規制',
  'game_machine_standards': '技術基準',
  'supervisor_duties': '実務指導',
  'final_problems': '行政手続'
};

// 極短縮名（狭小画面用・バッジ表示用）
export const MINI_CATEGORY_NAMES = {
  // 新カテゴリID
  'qualification_system': '制度',
  'game_machine_technical_standards': '技術',
  'supervisor_duties_and_guidance': '実務',
  'business_regulation_and_obligations': '規制',
  'administrative_procedures_and_penalties': '手続',

  // 古いカテゴリID対応
  'system_and_test': '制度',
  'business_law': '規制',
  'game_machine_standards': '技術',
  'supervisor_duties': '実務',
  'final_problems': '手続'
};
