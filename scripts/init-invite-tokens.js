/**
 * Vercel KVに招待トークンを登録するスクリプト
 * 使用方法: node scripts/init-invite-tokens.js
 */

import { kv } from '@vercel/kv';

// 招待トークン一覧（10個）
const INVITE_TOKENS = [
  '039742a2-f799-4574-8530-a8e1d81960f1',
  'cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb',
  'd0b28ab3-44b6-45aa-897b-e72e0e0da116',
  'babcd6fb-b8a8-46a8-b3a6-fc00966d07a3',
  'b1b281a3-6b76-4659-9827-bf3a07b6c3ba',
  '12f622c2-cbf4-4631-abb7-7336c841b198',
  '3c756c94-0d98-4d8b-b466-17e99f1b3240',
  '2b1d54e2-97a0-4900-a513-fab986540358',
  'd47c9566-cabd-4d96-91d0-41afc10a59b6',
  'c502c94a-3e4e-471e-9835-2f05018751e4'
];

async function initTokens() {
  console.log('🚀 招待トークンの初期化を開始します...\n');

  let successCount = 0;
  let errorCount = 0;

  for (const token of INVITE_TOKENS) {
    try {
      // トークンデータを作成
      const tokenData = {
        token,
        used: false,
        createdAt: new Date().toISOString()
      };

      // Vercel KVに保存
      await kv.set(`invite:${token}`, tokenData);

      console.log(`✅ トークン登録成功: ${token}`);
      successCount++;
    } catch (error) {
      console.error(`❌ トークン登録失敗: ${token}`, error.message);
      errorCount++;
    }
  }

  console.log(`\n📊 登録結果:`);
  console.log(`   成功: ${successCount}件`);
  console.log(`   失敗: ${errorCount}件`);
  console.log(`\n✅ 招待トークンの初期化が完了しました！`);
}

// スクリプト実行
initTokens().catch(error => {
  console.error('❌ エラーが発生しました:', error);
  process.exit(1);
});
