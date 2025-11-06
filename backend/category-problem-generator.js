#!/usr/bin/env node

/**
 * Category-based Problem Generator
 *
 * 7カテゴリ × 150-200問 = 1,200問生成
 * 難易度分布: Easy 30% / Medium 55% / Hard 15%
 *
 * 使用: OPENAI_API_KEY=sk-... node category-problem-generator.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_API_KEY) {
  console.error('❌ OPENAI_API_KEY environment variable is required');
  process.exit(1);
}

// 7つのカテゴリ定義
const CATEGORIES = {
  '営業許可・申請手続き': {
    targetProblems: 180,
    sources: ['風営法第6条', '風営法第7条', '施行規則第1条', '申請手続き'],
    description: '営業許可、変更届、条件など'
  },
  '建物・設備基準': {
    targetProblems: 200,
    sources: ['構造基準', '照度基準', '防音基準', '設備配置', '内装基準'],
    description: '建物構造、設備、内装に関する技術基準'
  },
  '従業員・管理者要件': {
    targetProblems: 140,
    sources: ['取扱主任者資格', '管理者要件', '従業者義務', '資格要件'],
    description: '主任者資格、管理者条件、従業者義務'
  },
  '営業時間・休業': {
    targetProblems: 110,
    sources: ['営業時間規制', '休業日', '定休日設定', '時間帯制限'],
    description: '営業時間制限、休業日規定'
  },
  '景品・景慮基準': {
    targetProblems: 180,
    sources: ['景品上限', '景慮基準', '景品種類', '交換ルール', '表示基準'],
    description: '景品・景慮の上限、基準、種類'
  },
  '法律・規制違反': {
    targetProblems: 230,
    sources: ['風営法違反', '罰則', '禁止事項', '不正行為', '許可取消要件'],
    description: '違反事項、罰則規定、禁止事項'
  },
  '実務・業務管理': {
    targetProblems: 200,
    sources: ['日常管理', '記録義務', '報告義務', '検査対応', '不正防止'],
    description: '日常業務、記録管理、検査対応'
  }
};

// OCRテキストから該当セクションを抽出
function extractRelevantText(ocrText, keywords) {
  const sections = ocrText.split('\n\n');
  const relevantSections = [];

  for (const keyword of keywords) {
    const matches = sections.filter(s =>
      s.includes(keyword) || s.includes(keyword.split('第')[0])
    );
    relevantSections.push(...matches.slice(0, 2)); // 最大2セクション
  }

  return relevantSections.slice(0, 5).join('\n\n').substring(0, 3000); // 3000文字まで
}

// OpenAI APIで問題生成
async function generateProblemsForCategory(categoryName, categoryConfig, ocrText, index) {
  const relevantText = extractRelevantText(ocrText, categoryConfig.sources);

  const prompt = `あなたは日本の遊技機取扱主任者試験の問題作成専門家です。

【カテゴリ】${categoryName}
【説明】${categoryConfig.description}

【テキスト参考】
${relevantText}

【指示】
以下のJSON形式で、正答/不正答の○×形式の試験問題を${categoryConfig.targetProblems}個生成してください。

各問題は以下の構造でJSON配列として返してください：
[
  {
    "id": "cat${index.toString().padStart(2, '0')}_q001",
    "statement": "問題文（簡潔、1文）",
    "answer": true,
    "difficulty": "easy",
    "category": "${categoryName}",
    "explanation": "解説（50-100字）",
    "source": "関連規定（例：風営法第6条）"
  },
  ...
]

【難易度分布（重要）】
全${categoryConfig.targetProblems}問中：
  - Easy (基本知識): 30% = ${Math.floor(categoryConfig.targetProblems * 0.3)}問
  - Medium (応用・複合): 55% = ${Math.floor(categoryConfig.targetProblems * 0.55)}問
  - Hard (引っかかりやすい・例外): 15% = ${Math.floor(categoryConfig.targetProblems * 0.15)}問

【要件】
- 実務的で現実的な内容
- 引っかかりやすい表現（トラップ）を含む
- 日本語は正確に
- JSONのみを返してください（説明や前置きは不要）

JSONのみ返してください。`;

  try {
    console.log(`🔄 ${categoryName} を生成中...`);

    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 8000,
        top_p: 0.9
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const content = response.data.choices[0]?.message?.content || '';

    // JSON抽出
    const jsonMatch = content.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
      console.warn(`⚠️ ${categoryName}: JSON not found in response`);
      return [];
    }

    const problems = JSON.parse(jsonMatch[0]);
    console.log(`✅ ${categoryName}: ${problems.length}問生成完了`);
    return problems;

  } catch (error) {
    console.error(`❌ ${categoryName} 生成エラー:`, error.response?.data?.error?.message || error.message);
    return [];
  }
}

// OCRデータ読み込み
function loadOCRData() {
  try {
    const data = JSON.parse(fs.readFileSync(
      path.join(__dirname, '../data/ocr_results_corrected.json'),
      'utf-8'
    ));

    let text = '';
    const pages = Array.isArray(data) ? data : (data.pages || []);
    pages.forEach(page => {
      text += `【ページ ${page.page_number}】\n${page.text || page.content}\n\n`;
    });

    return text.substring(0, 150000); // 150KB
  } catch (error) {
    console.error('❌ OCRデータ読み込み失敗:', error.message);
    process.exit(1);
  }
}

// メイン処理
async function main() {
  console.log(`
============================================================
  🎰 カテゴリ別問題生成エンジン
  1,200問の試験問題自動生成
============================================================
`);

  try {
    // 1. OCRデータ読み込み
    console.log('📚 OCRテキスト読み込み中...');
    const ocrText = loadOCRData();
    console.log(`✅ ${ocrText.length}文字読み込み完了\n`);

    // 2. カテゴリ別生成
    const allProblems = [];
    const categoryEntries = Object.entries(CATEGORIES);

    for (let i = 0; i < categoryEntries.length; i++) {
      const [categoryName, categoryConfig] = categoryEntries[i];
      const problems = await generateProblemsForCategory(
        categoryName,
        categoryConfig,
        ocrText,
        i + 1
      );

      allProblems.push(...problems);

      // レート制限対応
      if (i < categoryEntries.length - 1) {
        console.log('⏳ API レート制限対応: 2秒待機...\n');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    // 3. データ構築と保存
    const output = {
      generatedAt: new Date().toISOString(),
      totalProblems: allProblems.length,
      categories: Object.keys(CATEGORIES),
      problems: allProblems
    };

    fs.writeFileSync(
      path.join(__dirname, '../data/generated_problems.json'),
      JSON.stringify(output, null, 2),
      'utf-8'
    );

    console.log(`
============================================================
  📊 生成結果
============================================================
✅ 総問題数: ${output.totalProblems}問
📝 保存先: data/generated_problems.json

【カテゴリ別内訳】`);

    // カテゴリ別統計
    const categoryStats = {};
    allProblems.forEach(p => {
      categoryStats[p.category] = (categoryStats[p.category] || 0) + 1;
    });

    Object.entries(categoryStats).forEach(([cat, count]) => {
      const target = CATEGORIES[cat]?.targetProblems || 0;
      const percentage = Math.round(count / target * 100);
      console.log(`  ${cat}: ${count}問 (目標: ${target}問, ${percentage}%)`);
    });

    // 難易度分布
    const difficultyStats = {
      easy: allProblems.filter(p => p.difficulty === 'easy').length,
      medium: allProblems.filter(p => p.difficulty === 'medium').length,
      hard: allProblems.filter(p => p.difficulty === 'hard').length
    };

    console.log(`
【難易度分布】
  Easy: ${difficultyStats.easy}問 (${Math.round(difficultyStats.easy/output.totalProblems*100)}%)
  Medium: ${difficultyStats.medium}問 (${Math.round(difficultyStats.medium/output.totalProblems*100)}%)
  Hard: ${difficultyStats.hard}問 (${Math.round(difficultyStats.hard/output.totalProblems*100)}%)

============================================================`);

  } catch (error) {
    console.error('❌ 致命的エラー:', error.message);
    process.exit(1);
  }
}

main();
