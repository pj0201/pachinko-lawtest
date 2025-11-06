/**
 * RAG Bulk Problem Generator Executor
 *
 * 目的: OCR-corrected exam text を RAG ソースとして活用し、
 * 250-300個の実問題を生成する
 *
 * 実行方法: node generate-bulk-problems.js [options]
 * オプション:
 *   --llm <provider>  - LLMプロバイダー選択 (groq, openai, claude, mistral, ollama)
 *   --output <path>   - 出力ファイルパス (デフォルト: data/generated_problems.json)
 *   --limit <num>     - 最大問題数 (デフォルト: 300)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ChromaRAG, RAGInitializer } from './chroma-rag.js';
import { LLMProviderFactory } from './llm-provider.js';
import { RAGBulkProblemGenerator } from './rag-bulk-problem-generator.js';
import { CompleteQuestionGenerationPipeline } from './advanced-problem-generator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// デフォルト設定
const DEFAULT_CONFIG = {
  llmProvider: process.env.LLM_PROVIDER || 'groq',
  ocrDataPath: path.join(__dirname, '../data/ocr_results_corrected.json'),
  windEigyoLawPath: path.join(__dirname, '../../Claude-Code-Communication/resources/legal/wind_eikyo_law/wind_eikyo_law_v1.0.md'),
  outputPath: path.join(__dirname, '../data/generated_problems.json'),
  collectionName: 'patshinko_exam',
  maxProblems: 300,
  targetProblems: 250
};

/**
 * コマンドライン引数をパース
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--llm' && args[i + 1]) {
      config.llmProvider = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      config.outputPath = args[++i];
    } else if (args[i] === '--limit' && args[i + 1]) {
      config.maxProblems = parseInt(args[++i]);
    }
  }

  return config;
}

/**
 * OCR データをロード
 */
function loadOCRData(filePath) {
  console.log(`\n📂 Loading OCR exam textbook from: ${filePath}`);

  if (!fs.existsSync(filePath)) {
    throw new Error(`OCR data file not found: ${filePath}`);
  }

  const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  console.log(`✓ Loaded ${data.length} pages from OCR (exam textbook)`);

  return data;
}

/**
 * 風営法データをロード
 */
function loadWindEigyoLaw(filePath) {
  console.log(`\n📂 Loading Wind営法 from: ${filePath}`);

  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️  Wind営法 file not found: ${filePath}`);
    return null;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  console.log(`✓ Loaded Wind営法 v1.0 (${content.length} characters)`);

  return content;
}

/**
 * OCR データを RAG チャンクに変換
 */
function convertOCRToChunks(ocrData) {
  console.log(`\n🔄 Converting OCR data to chunks...`);

  const chunks = [];

  for (const page of ocrData) {
    if (page.text) {
      chunks.push({
        id: `ocr_page_${page.page_number}`,
        content: page.text,
        metadata: {
          source: 'ocr_exam_textbook',
          page_number: page.page_number,
          pdf_index: page.pdf_index,
          timestamp: page.timestamp
        }
      });
    }
  }

  console.log(`✓ Created ${chunks.length} chunks from OCR data`);
  return chunks;
}

/**
 * 風営法データを RAG チャンクに変換
 */
function convertWindEigyoLawToChunks(windLawContent) {
  console.log(`\n🔄 Converting Wind営法 to chunks...`);

  if (!windLawContent) {
    console.warn(`⚠️  No Wind営法 content to convert`);
    return [];
  }

  const chunks = [];

  // Section-based chunking
  const sections = windLawContent.split(/^## /m);

  sections.forEach((section, index) => {
    if (section.trim()) {
      // Split large sections further
      const subChunks = section.split(/\n\n+/).filter(s => s.trim());

      subChunks.forEach((subChunk, subIndex) => {
        if (subChunk.trim().length > 50) { // Only chunks with meaningful content
          chunks.push({
            id: `wind_law_section_${index}_${subIndex}`,
            content: subChunk.trim(),
            metadata: {
              source: 'wind_eikyo_law_v1.0',
              section_index: index,
              subsection_index: subIndex
            }
          });
        }
      });
    }
  });

  console.log(`✓ Created ${chunks.length} chunks from Wind営法 data`);
  return chunks;
}

/**
 * RAG システムを初期化
 */
async function initializeRAG(chunks, config) {
  console.log(`\n🗄️  Initializing ChromaRAG...`);

  const rag = new ChromaRAG();
  await rag.initialize(config.collectionName);

  console.log(`✓ ChromaRAG initialized`);
  console.log(`📥 Adding ${chunks.length} chunks to vector database...`);

  await rag.addChunks(chunks);

  const stats = await rag.getStats();
  console.log(`✓ RAG ready:`);
  console.log(`  - Collection: ${stats.collection}`);
  console.log(`  - Chunks: ${stats.total_chunks}`);
  console.log(`  - Last updated: ${stats.last_updated}`);

  return rag;
}

/**
 * LLM プロバイダーを初期化
 */
async function initializeLLM(providerName) {
  console.log(`\n🤖 Initializing LLM provider: ${providerName}`);

  const llm = await LLMProviderFactory.createFromEnv(providerName);
  console.log(`✓ LLM provider ready: ${llm.constructor.name}`);

  return llm;
}

/**
 * 大量問題生成エンジンを実行
 */
async function generateProblems(rag, llm, config) {
  console.log(`\n🚀 Starting bulk problem generation...`);
  console.log(`   Target: ${config.targetProblems}-${config.maxProblems} problems`);

  const generator = new RAGBulkProblemGenerator(rag, llm);
  const result = await generator.generateAllProblems();

  return result;
}

/**
 * 生成結果を検証
 */
function validateResults(result, config) {
  console.log(`\n✅ Generation Complete!`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`\n📊 Generation Statistics:`);
  console.log(`  Total problems: ${result.problems.length}`);
  console.log(`  Generation time: ${result.metadata.generation_time_minutes} minutes`);
  console.log(`  Target coverage: ${result.metadata.success_rate}`);

  console.log(`\n📋 Category Breakdown:`);
  for (const [categoryId, stats] of Object.entries(result.category_results)) {
    const target = stats.target;
    const generated = stats.generated;
    const percentage = ((generated / target) * 100).toFixed(1);
    const status = stats.success ? '✓' : '✗';
    console.log(`  ${status} ${stats.name}: ${generated}/${target} (${percentage}%)`);
  }

  const totalGenerated = result.problems.length;
  const targetMin = config.targetProblems;
  const targetMax = config.maxProblems;

  console.log(`\n🎯 Target Achievement:`);
  if (totalGenerated >= targetMin && totalGenerated <= targetMax) {
    console.log(`  ✅ Within target range: ${targetMin}-${targetMax}`);
  } else if (totalGenerated < targetMin) {
    console.log(`  ⚠️  Below target (${totalGenerated}/${targetMin})`);
  } else {
    console.log(`  ℹ️  Above target (${totalGenerated}/${targetMax})`);
  }

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

  return {
    success: totalGenerated >= targetMin,
    totalGenerated,
    targetMin,
    targetMax
  };
}

/**
 * 結果をファイルに保存
 */
function saveResults(result, outputPath) {
  console.log(`💾 Saving results to: ${outputPath}`);

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(
    outputPath,
    JSON.stringify(result, null, 2),
    'utf-8'
  );

  const stats = fs.statSync(outputPath);
  console.log(`✓ Saved: ${(stats.size / 1024).toFixed(2)} KB`);

  return outputPath;
}

/**
 * 生成された問題の品質サンプルを表示
 */
function displaySamples(result, sampleCount = 3) {
  console.log(`\n📚 Sample Generated Problems (showing ${Math.min(sampleCount, result.problems.length)}):`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

  const samples = result.problems.slice(0, sampleCount);

  for (let i = 0; i < samples.length; i++) {
    const problem = samples[i];
    console.log(`【問題 #${i + 1}】`);
    console.log(`カテゴリ: ${problem.category}`);
    console.log(`難易度: ${problem.difficulty}`);
    console.log(`パターン: Pattern${problem.pattern}`);
    console.log(`\n問題: ${problem.statement}`);
    console.log(`\n選択肢:`);
    console.log(`  ○ ${problem.option_correct}`);
    console.log(`  × ${problem.option_incorrect}`);
    console.log(`\n正答: ${problem.correct_answer === 'true' ? '○' : '×'}`);

    if (problem.explanation) {
      console.log(`\n解説: ${problem.explanation.substring(0, 200)}...`);
    }

    console.log(`\n${'━'.repeat(50)}\n`);
  }
}

/**
 * メイン実行関数
 */
async function main() {
  try {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`  🎰 パチンコ試験 RAG Bulk Problem Generator`);
    console.log(`  250-300問の実問題自動生成`);
    console.log(`${'='.repeat(60)}`);

    // 設定をロード
    const config = parseArgs();
    console.log(`\n⚙️  Configuration:`);
    console.log(`  LLM Provider: ${config.llmProvider}`);
    console.log(`  Data Sources:`);
    console.log(`    - OCR Exam: ${config.ocrDataPath}`);
    console.log(`    - Wind営法: ${config.windEigyoLawPath}`);
    console.log(`  Output: ${config.outputPath}`);
    console.log(`  Target: ${config.targetProblems}-${config.maxProblems} problems`);

    // データソースをロード
    console.log(`\n📚 Loading Data Sources...`);
    const ocrData = loadOCRData(config.ocrDataPath);
    const windLawData = loadWindEigyoLaw(config.windEigyoLawPath);

    // 両方のデータをチャンク化して結合
    console.log(`\n🔗 Combining chunks from both sources...`);
    const ocrChunks = convertOCRToChunks(ocrData);
    const windLawChunks = convertWindEigyoLawToChunks(windLawData);
    const chunks = [...ocrChunks, ...windLawChunks];

    console.log(`\n📊 Data Source Summary:`);
    console.log(`  OCR Textbook: ${ocrChunks.length} chunks`);
    console.log(`  Wind営法: ${windLawChunks.length} chunks`);
    console.log(`  Total: ${chunks.length} chunks`);

    // RAG を初期化
    const rag = await initializeRAG(chunks, config);

    // LLM を初期化
    const llm = await initializeLLM(config.llmProvider);

    // 問題を生成
    const result = await generateProblems(rag, llm, config);

    // 結果を検証
    const validation = validateResults(result, config);

    // 結果をファイルに保存
    const savedPath = saveResults(result, config.outputPath);

    // サンプル問題を表示
    if (result.problems.length > 0) {
      displaySamples(result, 2);
    }

    // 最終メッセージ
    console.log(`\n✨ RAG Bulk Problem Generation Complete!`);
    console.log(`\n📝 Next Steps:`);
    console.log(`  1. Review generated problems: ${savedPath}`);
    console.log(`  2. Test problem quality and coverage`);
    console.log(`  3. Deploy to frontend application`);
    console.log(`  4. Run ExamScreen component with ${validation.totalGenerated} problems`);

    console.log(`\n${'='.repeat(60)}\n`);

  } catch (error) {
    console.error(`\n❌ Error during execution:`);
    console.error(`  ${error.message}`);
    console.error(`\n📋 Stack trace:`);
    console.error(error.stack);
    process.exit(1);
  }
}

// 実行
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
