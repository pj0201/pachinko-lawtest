#!/usr/bin/env node

/**
 * 最高品質問題生成エンジンv2 - テスト版
 *
 * Phase 1: 50問の品質テスト実行
 * 機能: Anthropic Claude APIで高品質問題を生成
 * モード: テスト用（APIキーが設定されていても、ロジック検証用）
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Anthropic Claude API
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (!ANTHROPIC_API_KEY) {
  console.warn('⚠️ Warning: ANTHROPIC_API_KEY is not set');
  console.warn('   テストモード実行（モック生成）');
}

// ========================================
// テスト用設定
// ========================================

const CONFIG = {
  ocrDataPath: path.join(__dirname, '../data/ocr_results_corrected.json'),
  outputPath: path.join(__dirname, '../data/test_problems_phase1.json'),
  testProblems: 50,  // テスト: 50問
  categories: [
    '営業許可・申請手続き',
    '建物・設備基準',
    '従業員・管理者要件'
  ],
  patterns: {
    '1': '法律に明確に書いてあることをそのまま出題',
    '2': '「必ず」「絶対」などの絶対表現を含めて、例外を見落とさせるひっかけ',
    '3': '似た概念だが異なる法律用語の違いを理解させる'
  },
  patternDistribution: {
    '1': 0.5,
    '2': 0.3,
    '3': 0.2
  }
};

// ========================================
// 法律ロジック分析エンジン
// ========================================

class LawLogicAnalyzer {
  constructor() {
    this.exceptionPatterns = ['ただし', 'これを妨げない', 'この限りではない', '除外される'];
  }

  analyzeLaw(source) {
    return {
      main_rule: this.extractMainRule(source),
      exception_clauses: this.findExceptionClauses(source),
      key_terms: ['営業許可', '届け出', '義務'],
      time_sensitive: true
    };
  }

  extractMainRule(source) {
    const text = typeof source === 'string' ? source : source.text || '';
    const sentences = text.split(/[。、]/);
    return (sentences.find(s => s.includes('は')) || sentences[0] || '').trim().substring(0, 150);
  }

  findExceptionClauses(source) {
    const text = typeof source === 'string' ? source : source.text || '';
    const matches = [];
    for (const pattern of this.exceptionPatterns) {
      if (text.includes(pattern)) {
        matches.push(`${pattern}に関する規定`);
      }
    }
    return matches;
  }
}

// ========================================
// プロンプトビルダー
// ========================================

class PromptBuilder {
  buildPatternedPrompt(lawAnalysis, pattern, difficulty) {
    return `
日本の遊技機取扱主任者試験の出題専門家として、以下の条件で高品質な問題を生成してください。

【出題要件】
パターン${pattern}: ${CONFIG.patterns[pattern.toString()]}
難易度: ${difficulty}
主要ルール: ${lawAnalysis.main_rule}

【出力形式（JSON）】
{
  "statement": "問題文（完全な文章。主語+述語+具体的状況）",
  "answer": true,
  "pattern": ${pattern},
  "difficulty": "${difficulty}",
  "trapType": "absolute_expression",
  "trapExplanation": "ひっかけの説明",
  "explanation": "詳細な解説（150字以上）",
  "lawReference": "遊技機規制法第X条",
  "qualityScore": 0.95
}

高品質な問題を生成してください。`;
  }
}

// ========================================
// バリデーター
// ========================================

class QualityValidator {
  validateProblemQuality(problem, lawAnalysis) {
    const checks = {
      statement_complete: problem.statement && problem.statement.length > 20,
      has_answer: typeof problem.answer === 'boolean',
      has_pattern: problem.pattern >= 1 && problem.pattern <= 9,
      has_trap: problem.trapType !== 'none',
      has_explanation: problem.explanation && problem.explanation.length > 50,
      has_reference: problem.lawReference && problem.lawReference.length > 0
    };

    const score = Object.values(checks).filter(Boolean).length / Object.keys(checks).length;

    return {
      is_valid: score >= 0.80,
      checks,
      score: Math.round(score * 100)
    };
  }
}

// ========================================
// Anthropic Claude API呼び出し
// ========================================

async function generateWithClaude(prompt) {
  if (!ANTHROPIC_API_KEY) {
    // モック問題生成（テスト用）
    return generateMockProblem();
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
        system: '日本語の遊技機試験問題生成専門家。高品質な問題のみ生成します。'
      })
    });

    if (!response.ok) {
      console.error(`❌ API Error: ${response.status}`);
      return null;
    }

    const data = await response.json();
    const content = data.content[0].text;
    const jsonMatch = content.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    return null;
  } catch (error) {
    console.error('❌ Claude API Error:', error.message);
    return null;
  }
}

// ========================================
// モック問題生成（テスト用）
// ========================================

function generateMockProblem() {
  const templates = [
    {
      statement: "遊技機の設置許可を取得している場合、必ず営業時間内に客対応スタッフを配置しなければならない。",
      pattern: 1,
      trapType: "absolute_expression",
      trapExplanation: "「必ず」という絶対表現が使用されているが、実際には例外が存在する可能性がある"
    },
    {
      statement: "営業許可と営業届け出は、基本的に同じ手続きプロセスに従う必要がある。",
      pattern: 3,
      trapType: "word_difference",
      trapExplanation: "許可と届け出は異なる法的性質を持つプロセス"
    },
    {
      statement: "遊技機の設置届け出後、30日以内に営業を開始する必要がある。",
      pattern: 7,
      trapType: "time_sensitive",
      trapExplanation: "時間経過による法的ステータス変化に関するひっかけ"
    }
  ];

  const template = templates[Math.floor(Math.random() * templates.length)];

  return {
    statement: template.statement,
    answer: false,  // ひっかけ問題
    pattern: template.pattern,
    difficulty: "medium",
    trapType: template.trapType,
    trapExplanation: template.trapExplanation,
    explanation: `この問題は${template.trapExplanation}を狙った出題です。法律では例外規定が多く、絶対表現には注意が必要です。`,
    lawReference: "遊技機規制法",
    qualityScore: 0.85
  };
}

// ========================================
// メインエンジン（テスト版）
// ========================================

class TestProblemGenerator {
  constructor() {
    this.analyzer = new LawLogicAnalyzer();
    this.promptBuilder = new PromptBuilder();
    this.validator = new QualityValidator();
    this.problems = [];
    this.stats = {
      total: 0,
      valid: 0,
      invalid: 0
    };
  }

  selectPattern() {
    const rand = Math.random();
    if (rand < 0.5) return 1;
    if (rand < 0.8) return 2;
    return 3;
  }

  selectDifficulty() {
    const rand = Math.random();
    if (rand < 0.3) return 'easy';
    if (rand < 0.7) return 'medium';
    return 'hard';
  }

  async generateBatch(sources, category, count = 10) {
    console.log(`\n🔄 生成中: ${category} (${count}問)`);

    for (let i = 0; i < count; i++) {
      const source = sources[Math.floor(Math.random() * sources.length)];
      const lawAnalysis = this.analyzer.analyzeLaw(source);
      const pattern = this.selectPattern();
      const difficulty = this.selectDifficulty();
      const prompt = this.promptBuilder.buildPatternedPrompt(lawAnalysis, pattern, difficulty);

      const problem = await generateWithClaude(prompt);

      if (!problem) {
        this.stats.invalid++;
        continue;
      }

      const validation = this.validator.validateProblemQuality(problem, lawAnalysis);

      if (validation.is_valid) {
        problem.category = category;
        problem.id = `q_test_${this.problems.length + 1}`;
        problem.validation_score = validation.score;
        this.problems.push(problem);
        this.stats.valid++;

        console.log(`  ✅ [${this.stats.valid}/${count}] 品質: ${validation.score}% - Pattern${problem.pattern}`);
      } else {
        this.stats.invalid++;
      }

      this.stats.total++;
    }
  }

  async generateAll() {
    console.log('🚀 Phase 1: テスト生成開始');
    console.log(`目標: ${CONFIG.testProblems}問`);

    // OCRデータ読み込み
    console.log('\n📂 OCRデータ読み込み中...');
    try {
      const ocrData = JSON.parse(fs.readFileSync(CONFIG.ocrDataPath, 'utf-8'));
      // OCRデータは配列で、各要素が {text: "..."} の形式
      const sources = Array.isArray(ocrData) ? ocrData.map(p => p.text || p.content) : [];
      console.log(`✅ OCRデータ読み込み: ${sources.length}ページ`);

      if (sources.length === 0) {
        console.error('❌ OCRデータが空です');
        process.exit(1);
      }

      // 少数のカテゴリで生成
      const problemsPerCategory = Math.floor(CONFIG.testProblems / CONFIG.categories.length);

      for (const category of CONFIG.categories) {
        await this.generateBatch(sources, category, problemsPerCategory);
      }
    } catch (error) {
      console.error('❌ OCRデータ読み込みエラー:', error.message);
      process.exit(1);
    }

    // 結果保存
    const output = {
      metadata: {
        generated_at: new Date().toISOString(),
        phase: 'Phase 1 - Test',
        total_problems: this.problems.length,
        api_key_status: ANTHROPIC_API_KEY ? '✅ 設定済み' : '⚠️ モック実行',
        average_quality_score: this.problems.length > 0
          ? Math.round(this.problems.reduce((sum, p) => sum + (p.validation_score || 0), 0) / this.problems.length)
          : 0
      },
      stats: this.stats,
      problems: this.problems
    };

    fs.writeFileSync(CONFIG.outputPath, JSON.stringify(output, null, 2));

    console.log('\n✅ Phase 1 テスト完了！');
    console.log(`📊 統計:`);
    console.log(`  - 生成問題数: ${this.problems.length}`);
    console.log(`  - 有効問題数: ${this.stats.valid}`);
    console.log(`  - 無効問題数: ${this.stats.invalid}`);
    console.log(`  - 平均品質スコア: ${output.metadata.average_quality_score}%`);
    console.log(`  - APIキー状態: ${output.metadata.api_key_status}`);
    console.log(`📁 出力: ${CONFIG.outputPath}`);

    return this.problems;
  }
}

// ========================================
// 実行
// ========================================

const generator = new TestProblemGenerator();
generator.generateAll().catch(error => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
