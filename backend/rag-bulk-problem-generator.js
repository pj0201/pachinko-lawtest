/**
 * RAG Bulk Problem Generator - 大規模問題生成エンジン
 *
 * 目標: 250-300問を生成
 * 戦略: 各カテゴリから複数のコンテキストを検索 → 複数シードで問題生成
 *
 * 生成公式:
 * - チャンク数: 68-94個
 * - 1チャンク あたり 3-4問生成
 * - 合計: 204-376問（目標: 250-300問）
 */

import { CompleteQuestionGenerationPipeline } from './advanced-problem-generator.js';

class RAGBulkProblemGenerator {
  constructor(rag, llmProvider) {
    this.rag = rag;
    this.llm = llmProvider;
    this.pipeline = new CompleteQuestionGenerationPipeline(rag, llmProvider);

    // カテゴリ定義（ワーカー2分析ベース）
    this.categories = [
      {
        id: 'permits',
        name: '営業許可・申請手続き',
        keywords: ['許可', '申請', '届け出', '営業', '要件'],
        targetCount: 40  // 40問目標
      },
      {
        id: 'business_hours',
        name: '営業時間・営業場所',
        keywords: ['営業時間', '営業場所', '施設', '基準', '構造'],
        targetCount: 40
      },
      {
        id: 'gaming_machines',
        name: '遊技機規制',
        keywords: ['遊技機', '検定', '改造', '検査', '基準'],
        targetCount: 40
      },
      {
        id: 'employees',
        name: '従業者の要件・禁止事項',
        keywords: ['主任者', '従業員', '資格', '禁止', '雇用'],
        targetCount: 40
      },
      {
        id: 'customer_protection',
        name: '顧客保護・規制遵守',
        keywords: ['顧客', '未成年', '景品', '交換', '保護'],
        targetCount: 40
      },
      {
        id: 'violations',
        name: '法令違反と行政処分',
        keywords: ['違反', '処分', '停止', '取消', '行政'],
        targetCount: 30
      },
      {
        id: 'practical',
        name: '実務的対応',
        keywords: ['対応', '報告', '記録', '管理', '実務'],
        targetCount: 30
      }
    ];

    // 複数シードプロンプトテンプレート
    this.promptSeeds = [
      '基本的な正誤判断',
      'ひっかけ問題（絶対表現）',
      '言葉遣いの違い',
      '複数条件の組み合わせ'
    ];
  }

  /**
   * カテゴリから複数コンテキストを検索
   * @param {string} category
   * @param {number} limit
   * @returns {Array}
   */
  async searchCategoryContexts(category, limit = 5) {
    const searchQueries = category.keywords.map(kw => `${category.name} ${kw}`);
    const allResults = [];

    for (const query of searchQueries) {
      try {
        const results = await this.rag.search(query, Math.ceil(limit / searchQueries.length));
        allResults.push(...results);
      } catch (error) {
        console.warn(`Search failed for "${query}":`, error.message);
      }
    }

    // 重複排除
    const uniqueResults = Array.from(
      new Map(allResults.map(r => [r.id, r])).values()
    ).slice(0, limit);

    return uniqueResults;
  }

  /**
   * 1つのコンテキストから複数の問題を生成（複数シード）
   * @param {Object} context
   * @param {string} categoryName
   * @param {number} seedCount - 生成する問題数（通常3-4）
   * @returns {Array}
   */
  async generateMultipleProblemsFromContext(context, categoryName, seedCount = 4) {
    const problems = [];

    for (let i = 0; i < seedCount; i++) {
      try {
        // パターンを順序に選択（1,2,3,4を循環）
        const pattern = (i % 4) + 1;

        // 難易度を分散
        const difficulties = ['easy', 'medium', 'hard'];
        const difficulty = difficulties[i % difficulties.length];

        // 生成実行
        const result = await this.pipeline.executeCompleteFlow(
          context,
          pattern,
          difficulty
        );

        if (result.success && result.problem) {
          result.problem.category = categoryName;
          result.problem.pattern = pattern;
          result.problem.source_context_id = context.id;
          result.problem.seed_index = i;

          problems.push(result.problem);
          console.log(`✓ Generated: ${categoryName} - Pattern${pattern} - ${difficulty}`);
        }
      } catch (error) {
        console.warn(`Failed to generate problem: ${error.message}`);
      }

      // レート制限対策（LLM呼び出しの間隔）
      if (i < seedCount - 1) {
        await this._delay(800);
      }
    }

    return problems;
  }

  /**
   * カテゴリ全体の問題生成
   * @param {Object} category
   * @returns {Array}
   */
  async generateCategoryProblems(category) {
    console.log(`\n📚 Generating problems for: ${category.name}`);
    console.log(`   Target: ${category.targetCount} problems`);

    // 1. コンテキスト検索
    const contextLimit = Math.ceil(category.targetCount / 3); // 1コンテキスト = 3-4問
    const contexts = await this.searchCategoryContexts(category, contextLimit);

    if (contexts.length === 0) {
      console.warn(`No contexts found for ${category.name}`);
      return [];
    }

    console.log(`   Found ${contexts.length} contexts`);

    // 2. 各コンテキストから複数問題生成
    const allProblems = [];
    const problemsPerContext = Math.ceil(category.targetCount / contexts.length);

    for (let i = 0; i < contexts.length; i++) {
      const context = contexts[i];
      const problems = await this.generateMultipleProblemsFromContext(
        context,
        category.name,
        Math.min(problemsPerContext, 4)
      );

      allProblems.push(...problems);

      // 進捗表示
      const progress = Math.round((i + 1) / contexts.length * 100);
      console.log(`   Progress: ${progress}% (${problems.length} problems generated)`);

      // コンテキスト間の遅延
      if (i < contexts.length - 1) {
        await this._delay(1000);
      }
    }

    console.log(`   ✅ Total: ${allProblems.length}/${category.targetCount} problems`);
    return allProblems.slice(0, category.targetCount); // 目標数で制限
  }

  /**
   * 全カテゴリの問題を一括生成
   * @returns {Object}
   */
  async generateAllProblems() {
    console.log('\n🚀 RAG Bulk Problem Generation Starting\n');
    console.log(`Target: 250-300 problems`);
    console.log(`Categories: ${this.categories.length}\n`);

    const allProblems = [];
    const categoryResults = {};

    const startTime = Date.now();

    for (const category of this.categories) {
      try {
        const problems = await this.generateCategoryProblems(category);
        allProblems.push(...problems);
        categoryResults[category.id] = {
          name: category.name,
          target: category.targetCount,
          generated: problems.length,
          success: true
        };
      } catch (error) {
        console.error(`Failed to generate ${category.name}:`, error.message);
        categoryResults[category.id] = {
          name: category.name,
          target: category.targetCount,
          generated: 0,
          success: false,
          error: error.message
        };
      }
    }

    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000 / 60).toFixed(2);

    // 結果集計
    const result = {
      metadata: {
        generated_at: new Date().toISOString(),
        generation_time_minutes: duration,
        total_problems: allProblems.length,
        total_categories: this.categories.length,
        target_count: 250,
        success_rate: `${Math.round((allProblems.length / 280) * 100)}%`
      },
      category_results: categoryResults,
      problems: allProblems
    };

    console.log(`\n✅ Generation Complete!`);
    console.log(`   Total: ${allProblems.length} problems`);
    console.log(`   Time: ${duration} minutes`);
    console.log(`   Coverage: ${Math.round((allProblems.length / 280) * 100)}%\n`);

    return result;
  }

  /**
   * 遅延ユーティリティ
   */
  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * 生成実行スクリプト
 */
export class BulkGenerationExecutor {
  static async execute(rag, llmProvider, outputPath) {
    const generator = new RAGBulkProblemGenerator(rag, llmProvider);
    const result = await generator.generateAllProblems();

    // 結果をJSONで保存
    import('fs').then(({ writeFileSync }) => {
      writeFileSync(
        outputPath,
        JSON.stringify(result, null, 2),
        'utf-8'
      );
      console.log(`💾 Saved to: ${outputPath}`);
    });

    return result;
  }
}

export { RAGBulkProblemGenerator };
