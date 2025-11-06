#!/usr/bin/env node

/**
 * Quick Problem Generator - Groq利用
 * 既存のlldm-providerを活用した高速問題生成
 *
 * 実行: GROQ_API_KEY=... node quick-problem-generator.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GROQ_API_KEY = process.env.GROQ_API_KEY;
if (!GROQ_API_KEY) {
  console.error('❌ GROQ_API_KEY not set');
  process.exit(1);
}

const CONFIG = {
  ocrDataPath: path.join(__dirname, '../data/ocr_results_corrected.json'),
  outputPath: path.join(__dirname, '../data/generated_problems.json'),
  targetProblems: 300,
  problemsPerBatch: 10,
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

async function callGroqAPI(prompt) {
  try {
    const response = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      {
        model: 'gemma-7b-it',  // 利用可能なモデルに変更
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 0.9
      },
      {
        headers: {
          'Authorization': `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('❌ Groq API error:', error.response?.data || error.message);
    throw error;
  }
}

function loadOCRData() {
  try {
    const rawData = fs.readFileSync(CONFIG.ocrDataPath, 'utf-8');
    const data = JSON.parse(rawData);

    let text = '';

    // データ形式を判定（pages配列 or 直接配列）
    const pages = Array.isArray(data) ? data : (data.pages || []);

    pages.forEach(page => {
      text += `【ページ ${page.page_number}】\n${page.text || page.content}\n\n`;
    });

    if (text.length === 0) {
      console.error('❌ No text extracted from OCR data');
      process.exit(1);
    }

    return text.substring(0, 100000);
  } catch (error) {
    console.error('❌ Failed to load OCR:', error.message);
    process.exit(1);
  }
}

async function generateProblems(ocrText) {
  const allProblems = [];
  let batchNum = 0;

  for (const category of CONFIG.categories) {
    for (let i = 0; i < 2; i++) {  // 各カテゴリ2バッチ
      batchNum++;
      console.log(`\n🔄 Batch ${batchNum}: ${category}`);

      const prompt = `以下の試験テキストに基づいて、${CONFIG.problemsPerBatch}個の○×問題を生成してください。

【カテゴリ】${category}

【テキスト参考】
${ocrText.substring(batchNum * 5000, batchNum * 5000 + 40000)}

以下のJSON形式で返してください。JSON のみ返してください。
[
  {"id": "q${batchNum.toString().padStart(3, '0')}_001", "statement": "問題文", "answer": true, "difficulty": "medium", "explanation": "解説", "category": "${category}"},
  ...
]`;

      try {
        const response = await callGroqAPI(prompt);
        const jsonMatch = response.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
          const problems = JSON.parse(jsonMatch[0]);
          allProblems.push(...problems);
          console.log(`✅ Added ${problems.length} problems (Total: ${allProblems.length})`);
        }
      } catch (error) {
        console.warn(`⚠️  Batch ${batchNum} failed, skipping`);
      }

      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 2000));

      if (allProblems.length >= CONFIG.targetProblems) break;
    }

    if (allProblems.length >= CONFIG.targetProblems) break;
  }

  return allProblems.slice(0, CONFIG.targetProblems);
}

async function main() {
  console.log(`
============================================================
  🎰 Quick Problem Generator with Groq
============================================================
`);

  try {
    // 1. Load OCR data
    console.log('📚 Loading OCR textbook...');
    const ocrText = loadOCRData();
    console.log(`✅ Loaded ${ocrText.length} characters`);

    // 2. Generate problems
    console.log(`\n🚀 Generating ~${CONFIG.targetProblems} problems...`);
    const problems = await generateProblems(ocrText);

    // 3. Save
    const output = {
      generatedAt: new Date().toISOString(),
      totalProblems: problems.length,
      problems: problems
    };

    fs.writeFileSync(CONFIG.outputPath, JSON.stringify(output, null, 2));
    console.log(`\n✅ Generated ${problems.length} problems`);
    console.log(`📝 Saved to: ${CONFIG.outputPath}`);

    // Statistics
    const stats = {
      easy: problems.filter(p => p.difficulty === 'easy').length,
      medium: problems.filter(p => p.difficulty === 'medium').length,
      hard: problems.filter(p => p.difficulty === 'hard').length
    };
    console.log(`\n📊 Difficulty:`);
    console.log(`  Easy: ${stats.easy} (${Math.round(stats.easy/problems.length*100)}%)`);
    console.log(`  Medium: ${stats.medium} (${Math.round(stats.medium/problems.length*100)}%)`);
    console.log(`  Hard: ${stats.hard} (${Math.round(stats.hard/problems.length*100)}%)`);

  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    process.exit(1);
  }
}

main();
