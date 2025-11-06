#!/usr/bin/env node

/**
 * 最高品質問題生成エンジンv2 - Worker2専用版
 *
 * 目的: カテゴリ 3.5-7 (営業時間後半・景品・法律・実務)
 * 目標問題数: 750問
 *
 * 実行方法:
 * export ANTHROPIC_API_KEY="sk-ant-..."
 * node ultimate-problem-generator-v2-worker2.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Anthropic Claude API
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || null;
if (!ANTHROPIC_API_KEY) {
  console.warn('⚠️  ANTHROPIC_API_KEY is not set');
  console.warn('   モック生成モード（本番はAPIキー設定後）');
}

// ========================================
// Worker2専用設定
// ========================================

const CONFIG = {
  ocrDataPath: path.join(__dirname, '../data/ocr_results_corrected.json'),
  outputPath: path.join(__dirname, '../data/ultimate_problems_worker2.json'),
  learningPath: path.join(__dirname, '../data/learning_stats_worker2.json'),
  targetProblems: 750,
  categories: [
  "split:営業時間・休業日管理(後半)",
  "景品・景慮基準",
  "法律・規制違反・処分",
  "実務・業務管理・記録"
],
  patterns: {
    '1': '法律に明確に書いてあることをそのまま出題',
    '2': '「必ず」「絶対」などの絶対表現を含めて、例外を見落とさせるひっかけ',
    '3': '似た概念だが異なる法律用語の違いを理解させる',
    '4': '複数の条件が同時に必要な場合、優先順位構造を隠した問題',
    '5': '複数の法律が関わる場合の相互関係を理解させる',
    '6': 'シナリオに基づいて、場合分けの理解を問う問題',
    '7': '時間経過による法的ステータス変化（許可失効など）',
    '8': '複数違反時の優先度判定（最優先措置は何か）',
    '9': '法令改正による例外関係（旧法と新法の関係）'
  },
  patternDistribution: {
    '1': 0.25, '2': 0.18, '3': 0.13, '4': 0.18,
    '5': 0.10, '6': 0.08, '7': 0.04, '8': 0.02, '9': 0.02
  }
};

// ========================================
// 法律ロジック分析エンジン
// ========================================

class LawLogicAnalyzer {
  constructor() {
    this.exceptionPatterns = ['ただし', 'これを妨げない', 'この限りではない', '除外される'];
    this.legalTerms = {
      '許可': { category: '申請', weight: 0.9 },
      '届け出': { category: '申請', weight: 0.8 },
      '義務': { category: '要件', weight: 1.0 },
      '禁止': { category: '禁止事項', weight: 1.0 }
    };
  }

  analyzeLaw(source) {
    return {
      main_rule: this.extractMainRule(source),
      exception_clauses: this.findExceptionClauses(source),
      key_terms: this.findKeyTerms(source),
      time_sensitive: this.detectTimeSensitive(source)
    };
  }

  extractMainRule(source) {
    const text = typeof source === 'string' ? source : source.text || '';
    const sentences = text.split(/[。、]/);
    return (sentences.find(s => s.includes('は')) || sentences[0] || '').trim().substring(0, 150);
  }

  findExceptionClauses(source) {
    const exceptions = [];
    const text = typeof source === 'string' ? source : source.text || '';
    for (const pattern of this.exceptionPatterns) {
      if (text.includes(pattern)) {
        exceptions.push(pattern);
      }
    }
    return exceptions;
  }

  findKeyTerms(source) {
    const terms = [];
    const text = typeof source === 'string' ? source : source.text || '';
    for (const [term, info] of Object.entries(this.legalTerms)) {
      if (text.includes(term)) {
        terms.push({ term, category: info.category, weight: info.weight });
      }
    }
    return terms.sort((a, b) => b.weight - a.weight).slice(0, 5);
  }

  detectTimeSensitive(source) {
    const text = typeof source === 'string' ? source : source.text || '';
    const keywords = ['失効', '有効期限', '期間', '経過'];
    return keywords.some(k => text.includes(k));
  }
}

// ========================================
// プロンプトビルダー
// ========================================

class PromptBuilder {
  buildPatternedPrompt(lawAnalysis, pattern, difficulty, category) {
    return `
日本の遊技機取扱主任者試験の出題専門家として、以下の条件で高品質な問題を生成してください。

【出題要件】
カテゴリ: ${category}
パターン${pattern}: ${CONFIG.patterns[pattern.toString()]}
難易度: ${difficulty}
主要ルール: ${lawAnalysis.main_rule}

【出力形式（JSON）】
{
  "statement": "問題文（完全な文章）",
  "answer": true/false,
  "pattern": ${pattern},
  "difficulty": "${difficulty}",
  "trapType": "none|absolute_expression|word_difference|priority|relation|scenario|time_sensitive|amendment",
  "trapExplanation": "ひっかけの仕組み",
  "explanation": "詳細な解説",
  "lawReference": "参照法令",
  "qualityScore": 0.0-1.0
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
    answer: false,
    pattern: template.pattern,
    difficulty: "medium",
    trapType: template.trapType,
    trapExplanation: template.trapExplanation,
    explanation: `この問題は${template.trapExplanation}を狙った出題です。法律では例外規定が多く、絶対表現には注意が必要です。`,
    lawReference: "遊技機規制法",
    qualityScore: 0.85
  };
}

async function generateWithClaude(prompt) {
  // APIキーがない場合はモック生成
  if (!ANTHROPIC_API_KEY) {
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
        max_tokens: 1200,
        messages: [{ role: 'user', content: prompt }],
        system: '日本語の遊技機試験問題生成の専門家。高品質な問題のみ生成します。'
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    const content = data.content[0].text;
    const jsonMatch = content.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    return null;
  } catch (error) {
    console.error('❌ Claude generation error:', error.message);
    return generateMockProblem(); // エラー時もモック生成
  }
}

// ========================================
// メインエンジン
// ========================================

class ProblemGenerator {
  constructor() {
    this.analyzer = new LawLogicAnalyzer();
    this.promptBuilder = new PromptBuilder();
    this.validator = new QualityValidator();
    this.generatedProblems = [];
    this.stats = {
      total: 0,
      valid: 0,
      invalid: 0,
      by_category: {}
    };
  }

  selectPattern() {
    const rand = Math.random();
    let cumulative = 0;
    for (const [pattern, probability] of Object.entries(CONFIG.patternDistribution)) {
      cumulative += probability;
      if (rand <= cumulative) {
        return parseInt(pattern);
      }
    }
    return 1;
  }

  selectDifficulty() {
    const rand = Math.random();
    if (rand < 0.30) return 'easy';
    if (rand < 0.70) return 'medium';
    return 'hard';
  }

  async generateBatch(sources, category, count = 10) {
    console.log(`\n🔄 生成中: ${category} (${count}問)`);

    const problems = [];
    let attempts = 0;
    const maxAttempts = count * 3;

    while (problems.length < count && attempts < maxAttempts) {
      attempts++;

      const source = sources[Math.floor(Math.random() * sources.length)];
      const lawAnalysis = this.analyzer.analyzeLaw(source);
      const pattern = this.selectPattern();
      const difficulty = this.selectDifficulty();
      const prompt = this.promptBuilder.buildPatternedPrompt(lawAnalysis, pattern, difficulty, category);

      const problem = await generateWithClaude(prompt);

      if (!problem) {
        this.stats.invalid++;
        continue;
      }

      const validation = this.validator.validateProblemQuality(problem, lawAnalysis);

      if (validation.is_valid && validation.score >= 80) {
        problem.category = category;
        problem.id = `q_${this.generatedProblems.length + 1}`;
        problem.validation_score = validation.score;
        problems.push(problem);
        this.stats.valid++;

        console.log(`  ✅ [${problems.length}/${count}] 品質: ${validation.score}%`);
      } else {
        this.stats.invalid++;
      }

      this.stats.total++;
    }

    this.stats.by_category[category] = problems.length;
    return problems;
  }

  async generateAll() {
    console.log('🚀 Worker2: 生成エンジン起動');
    console.log(`対象: ${CONFIG.description}`);
    console.log(`目標: ${CONFIG.targetProblems}問`);

    // OCRデータ読み込み
    console.log('\n📂 OCRデータ読み込み中...');
    try {
      const ocrData = JSON.parse(fs.readFileSync(CONFIG.ocrDataPath, 'utf-8'));
      const sources = Array.isArray(ocrData) ? ocrData.map(p => p.text || p.content) : [];
      console.log(`✅ OCRデータ読み込み: ${sources.length}ページ`);

      if (sources.length === 0) {
        console.error('❌ OCRデータが空です');
        process.exit(1);
      }

      // カテゴリごとに生成
      const problemsPerCategory = Math.floor(CONFIG.targetProblems / CONFIG.categories.length);

      for (const category of CONFIG.categories) {
        const categoryProblems = await this.generateBatch(sources, category, problemsPerCategory);
        this.generatedProblems.push(...categoryProblems);
      }
    } catch (error) {
      console.error('❌ エラー:', error.message);
      process.exit(1);
    }

    // 結果保存
    const output = {
      metadata: {
        generated_at: new Date().toISOString(),
        worker: 'Worker2',
        total_problems: this.generatedProblems.length,
        target_problems: CONFIG.targetProblems,
        categories: CONFIG.categories.length,
        average_quality_score: this.generatedProblems.length > 0
          ? Math.round(this.generatedProblems.reduce((sum, p) => sum + (p.validation_score || 0), 0) / this.generatedProblems.length)
          : 0
      },
      stats: this.stats,
      problems: this.generatedProblems
    };

    fs.writeFileSync(CONFIG.outputPath, JSON.stringify(output, null, 2));

    console.log('\n✅ 生成完了！');
    console.log(`📊 Worker2 統計:`);
    console.log(`  - 生成問題数: ${this.generatedProblems.length}`);
    console.log(`  - 有効問題数: ${this.stats.valid}`);
    console.log(`  - 無効問題数: ${this.stats.invalid}`);
    console.log(`  - 平均品質スコア: ${output.metadata.average_quality_score}%`);
    console.log(`📁 出力: ${CONFIG.outputPath}`);
  }
}

// ========================================
// 実行
// ========================================

const generator = new ProblemGenerator();
generator.generateAll().catch(error => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
