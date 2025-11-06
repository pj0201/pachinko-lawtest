/**
 * RAG System Setup Script
 *
 * 使用法: node backend/setup.js [--init-rag] [--test]
 */

import { RAGInitializer } from './chroma-rag.js';
import { LLMProviderFactory } from './llm-provider.js';
import { RAGPipelineFactory } from './rag-pipeline.js';
import dotenv from 'dotenv';
import fs from 'fs';

dotenv.config({ path: './backend/.env' });

async function main() {
  const args = process.argv.slice(2);
  const shouldInitRAG = args.includes('--init-rag');
  const shouldTest = args.includes('--test');

  console.log('\n' + '='.repeat(60));
  console.log('🚀 パチンコ遊技機取扱主任者講習 - RAGシステムセットアップ');
  console.log('='.repeat(60) + '\n');

  // 1. 環境確認
  console.log('📋 ステップ 1: 環境確認');
  console.log('─'.repeat(60));

  const envVars = ['LLM_PROVIDER', 'GROQ_API_KEY', 'CHROMA_PATH', 'OCR_RESULTS_PATH'];
  const missingVars = [];

  for (const envVar of envVars) {
    const value = process.env[envVar];
    const status = value ? '✓' : '✗';
    console.log(`  ${status} ${envVar}: ${value ? '設定済み' : '未設定'}`);
    if (!value && envVar !== 'GROQ_API_KEY') {
      missingVars.push(envVar);
    }
  }

  if (missingVars.length > 0 && !shouldTest) {
    console.error(`\n❌ エラー: 以下の環境変数が必要です: ${missingVars.join(', ')}`);
    console.error('backend/.env ファイルを確認してください\n');
    process.exit(1);
  }

  // 2. ファイル確認
  console.log('\n📁 ステップ 2: 必須ファイル確認');
  console.log('─'.repeat(60));

  const requiredFiles = [
    { path: process.env.OCR_RESULTS_PATH, label: 'OCR補正結果' },
    { path: process.env.WIND_EIKYO_LAW_PATH, label: '風営法ドキュメント' }
  ];

  for (const file of requiredFiles) {
    if (file.path) {
      const exists = fs.existsSync(file.path);
      const status = exists ? '✓' : '✗';
      console.log(`  ${status} ${file.label}: ${file.path}`);
      if (!exists) {
        console.warn(`    ⚠️ ファイルが見つかりません`);
      }
    }
  }

  // 3. LLMプロバイダ確認
  console.log('\n🤖 ステップ 3: LLMプロバイダ確認');
  console.log('─'.repeat(60));

  const provider = process.env.LLM_PROVIDER || 'groq';
  const apiKey = process.env[`${provider.toUpperCase()}_API_KEY`];

  console.log(`  プロバイダ: ${provider.toUpperCase()}`);

  if (provider === 'ollama') {
    console.log(`  ✓ Ollama (ローカル, APIキー不要)`);
  } else if (apiKey) {
    const maskedKey = apiKey.substring(0, 6) + '*'.repeat(Math.max(0, apiKey.length - 10));
    console.log(`  ✓ APIキー: ${maskedKey}`);
  } else {
    console.warn(`  ⚠️ APIキーが設定されていません`);
  }

  // 4. RAG初期化（オプション）
  if (shouldInitRAG) {
    console.log('\n⚙️  ステップ 4: RAG初期化');
    console.log('─'.repeat(60));

    try {
      const result = await RAGInitializer.initialize({
        ocrPath: process.env.OCR_RESULTS_PATH,
        windPath: process.env.WIND_EIKYO_LAW_PATH
      });

      console.log(`✅ RAG初期化完了`);
      console.log(`   ドキュメント数: ${result.stats.documentCount}`);
    } catch (error) {
      console.error(`❌ RAG初期化失敗: ${error.message}`);
      process.exit(1);
    }
  }

  // 5. テスト実行（オプション）
  if (shouldTest) {
    console.log('\n🧪 ステップ 5: テスト実行');
    console.log('─'.repeat(60));

    try {
      // LLMプロバイダテスト
      console.log('\n  テスト 1: LLMプロバイダ接続...');
      const llm = LLMProviderFactory.createFromEnv();
      console.log(`  ✓ ${llm.constructor.name} 接続成功`);

      // テスト質問生成
      if (process.env.GROQ_API_KEY || provider === 'ollama') {
        console.log('\n  テスト 2: 簡単な問い合わせ...');
        const response = await llm.generateResponse(
          '「風営法」とは何か、日本語で簡潔に説明してください。',
          { maxTokens: 100 }
        );
        console.log(`  ✓ 応答受け取り: "${response.substring(0, 50)}..."`);
      }
    } catch (error) {
      console.error(`  ❌ テスト失敗: ${error.message}`);
    }
  }

  // 6. 最終メッセージ
  console.log('\n' + '='.repeat(60));
  console.log('✅ セットアップ確認完了');
  console.log('='.repeat(60));

  console.log('\n📝 次のステップ:');
  console.log('\n  1. RAG初期化（初回のみ）:');
  console.log('     node backend/setup.js --init-rag\n');

  console.log('  2. サーバー起動:');
  console.log('     npm start\n');

  console.log('  3. APIドキュメント:');
  console.log('     http://localhost:3000/api/health\n');

  console.log('  4. テスト実行:');
  console.log('     curl -X POST http://localhost:3000/api/questions/generate \\');
  console.log('       -H "Content-Type: application/json" \\');
  console.log('       -d \'{"topic": "遊技機の定義", "count": 2}\'\n');
}

main().catch(console.error);
