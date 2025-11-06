#!/usr/bin/env node

/**
 * シンプル Groq 問題生成エンジン
 * RAG不要で直接OCRテキスト → Groq → 問題生成
 *
 * 実行: node simple-groq-generator.js
 */

import Groq from 'groq';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GROQ_API_KEY = process.env.GROQ_API_KEY;
if (!GROQ_API_KEY) {
  console.error('❌ Error: GROQ_API_KEY is not set');
  process.exit(1);
}

const groq = new Groq({ apiKey: GROQ_API_KEY });

const CONFIG = {
  ocrDataPath: path.join(__dirname, '../data/ocr_results_corrected.json'),
  outputPath: path.join(__dirname, '../data/generated_problems.json'),
  targetProblems: 300,
  batchSize: 20,  // 1バッチあたり20問
  categories: [
    '営業許可・申請手続き',
    '建物・設備基準',
    '従業員・管理者要件',
    '営業時間・休業',
    '景品・景慮基準',
    '法律・規制違反',
    '実務・業務管理'
  ]
};

async function loadOCRData() {
  try {
    console.log(`📂 Loading OCR data from: ${CONFIG.ocrDataPath}`);
    const rawData = fs.readFileSync(CONFIG.ocrDataPath, 'utf-8');
    const data = JSON.parse(rawData);
    console.log(`✅ Loaded ${data.pages.length} pages`);

    // テキストを抽出
    let fullText = '';
    data.pages.forEach((page, idx) => {
      fullText += `【ページ ${page.page_number}】\n`;
      fullText += page.content + '\n\n';
    });

    return fullText.substring(0, 80000);  // トークン制限対応で8万文字まで
  } catch (error) {
    console.error('❌ Failed to load OCR data:', error.message);
    process.exit(1);
  }
}

async function generateProblemsForCategory(ocrText, category, batchNumber) {
  const prompt = `
あなたは日本の遊技機取扱主任者試験の問題作成専門家です。

【テーマ】${category}

【テキスト参考】
${ocrText.substring(0, 40000)}

【指示】
以下のJSON形式で、正答/不正答の○×形式の試験問題を${CONFIG.batchSize}個生成してください。

各問題は以下の構造でJSON配列として返してください：
[
  {
    "id": "batch${batchNumber}_q001",
    "statement": "問題文（簡潔、1文）",
    "answer": true or false,
    "difficulty": "easy" or "medium" or "hard",
    "explanation": "解説（50-100字）",
    "category": "${category}",
    "reference": "関連法または参考資料（例：風営法第6条）"
  },
  ...
]

【要件】
- 難易度分布: 30% easy, 50% medium, 20% hard
- 実務的で現実的な内容
- 引っかかりやすい表現（トラップ）を含む
- 日本語は正確に

JSONのみを返してください。説明や前置きは不要です。
`;

  try {
    console.log(`🔄 Generating batch ${batchNumber} for category: ${category}`);

    const response = await groq.chat.completions.create({
      model: 'mixtral-8x7b-32768',
      messages: [{
        role: 'user',
        content: prompt
      }],
      temperature: 0.7,
      max_tokens: 3000,
      top_p: 0.9
    });

    const content = response.choices[0]?.message?.content || '';

    // JSON抽出
    const jsonMatch = content.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
      console.warn(`⚠️  No JSON found in response for batch ${batchNumber}`);
      return [];
    }

    const problems = JSON.parse(jsonMatch[0]);
    console.log(`✅ Generated ${problems.length} problems for batch ${batchNumber}`);
    return problems;
  } catch (error) {
    console.error(`❌ Error generating batch ${batchNumber}:`, error.message);
    return [];
  }
}

async function main() {
  console.log(`
============================================================
  🎰 シンプル Groq 問題生成エンジン
  ${CONFIG.targetProblems}問の試験問題自動生成
============================================================
`);

  try {
    // 1. OCRデータ読み込み
    const ocrText = await loadOCRData();
    console.log(`✅ OCR text loaded: ${ocrText.length} characters`);

    // 2. 問題生成
    console.log(`\n📚 Generating problems for ${CONFIG.categories.length} categories...`);
    const allProblems = [];
    const batchesPerCategory = Math.ceil(CONFIG.targetProblems / CONFIG.categories.length / CONFIG.batchSize);

    for (const category of CONFIG.categories) {
      for (let i = 0; i < batchesPerCategory; i++) {
        const batchNumber = allProblems.length / CONFIG.batchSize + 1;
        const problems = await generateProblemsForCategory(ocrText, category, batchNumber);
        allProblems.push(...problems);

        if (allProblems.length >= CONFIG.targetProblems) {
          break;
        }

        // API レート制限対応: 各リクエスト間に遅延
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      if (allProblems.length >= CONFIG.targetProblems) {
        break;
      }
    }

    // 3. 結果保存
    const output = {
      generatedAt: new Date().toISOString(),
      totalProblems: allProblems.length,
      categories: CONFIG.categories,
      problems: allProblems.slice(0, CONFIG.targetProblems)
    };

    fs.writeFileSync(CONFIG.outputPath, JSON.stringify(output, null, 2), 'utf-8');
    console.log(`\n✅ Generated ${output.totalProblems} problems`);
    console.log(`📝 Saved to: ${CONFIG.outputPath}`);

    // 統計情報
    const stats = {
      easy: output.problems.filter(p => p.difficulty === 'easy').length,
      medium: output.problems.filter(p => p.difficulty === 'medium').length,
      hard: output.problems.filter(p => p.difficulty === 'hard').length
    };
    console.log(`\n📊 Difficulty Distribution:`);
    console.log(`  Easy: ${stats.easy} (${Math.round(stats.easy/output.totalProblems*100)}%)`);
    console.log(`  Medium: ${stats.medium} (${Math.round(stats.medium/output.totalProblems*100)}%)`);
    console.log(`  Hard: ${stats.hard} (${Math.round(stats.hard/output.totalProblems*100)}%)`);

  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    process.exit(1);
  }
}

main();
