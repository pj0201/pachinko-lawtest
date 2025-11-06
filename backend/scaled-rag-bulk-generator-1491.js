/**
 * Scaled RAG Bulk Problem Generator - 1491問生成版
 *
 * 元々の RAG Bulk Generator を拡張
 * - ターゲット: 1491問
 * - 戦略: Advanced Generator + RAG を活用
 * - 安定性: バッチ処理+チェックポイント
 *
 * 実装日: 2025-10-22
 */

import { CompleteQuestionGenerationPipeline } from './advanced-problem-generator.js';
import fs from 'fs';
import path from 'path';

class ScaledRAGBulkGenerator {
  constructor(rag, llmProvider, config = {}) {
    this.rag = rag;
    this.llm = llmProvider;
    this.pipeline = new CompleteQuestionGenerationPipeline(rag, llmProvider);

    // ターゲット総問数（デフォルト: 1491）
    this.targetTotal = config.targetTotal || 1491;

    // 各カテゴリの目標問数を自動計算
    this.categories = this._initializeScaledCategories();

    // 複数シードプロンプト
    this.promptSeeds = [
      '基本的な正誤判断',
      'ひっかけ問題（絶対表現）',
      '言葉遣いの違い',
      '複数条件の組み合わせ'
    ];

    // チェックポイント設定
    this.checkpointDir = config.checkpointDir || '/tmp/generation_checkpoint';
    this.batchSize = config.batchSize || 10; // 1バッチの問数
    this._ensureCheckpointDir();

    // 統計情報
    this.stats = {
      generated: 0,
      failed: 0,
      startTime: null,
      endTime: null
    };
  }

  /**
   * スケール済みカテゴリ初期化
   * 1491問を7カテゴリに均等配分
   */
  _initializeScaledCategories() {
    const baseCategories = [
      {
        id: 'permits',
        name: '営業許可・申請手続き',
        keywords: ['許可', '申請', '届け出', '営業', '要件'],
        baseCount: 40
      },
      {
        id: 'business_hours',
        name: '営業時間・営業場所',
        keywords: ['営業時間', '営業場所', '施設', '基準', '構造'],
        baseCount: 40
      },
      {
        id: 'gaming_machines',
        name: '遊技機規制',
        keywords: ['遊技機', '検定', '改造', '検査', '基準'],
        baseCount: 40
      },
      {
        id: 'employees',
        name: '従業者の要件・禁止事項',
        keywords: ['主任者', '従業員', '資格', '禁止', '雇用'],
        baseCount: 40
      },
      {
        id: 'customer_protection',
        name: '顧客保護・規制遵守',
        keywords: ['顧客', '未成年', '景品', '交換', '保護'],
        baseCount: 40
      },
      {
        id: 'violations',
        name: '法令違反と行政処分',
        keywords: ['違反', '処分', '停止', '取消', '行政'],
        baseCount: 30
      },
      {
        id: 'practical',
        name: '実務的対応',
        keywords: ['対応', '報告', '記録', '管理', '実務'],
        baseCount: 30
      }
    ];

    // 比率を保ったまま、targetTotal に合わせてスケーリング
    const baseTotal = baseCategories.reduce((sum, cat) => sum + cat.baseCount, 0);
    const scaleFactor = this.targetTotal / baseTotal;

    return baseCategories.map(cat => ({
      ...cat,
      targetCount: Math.ceil(cat.baseCount * scaleFactor)
    }));
  }

  /**
   * チェックポイントディレクトリ確保
   */
  _ensureCheckpointDir() {
    if (!fs.existsSync(this.checkpointDir)) {
      fs.mkdirSync(this.checkpointDir, { recursive: true });
    }
  }

  /**
   * チェックポイントファイルパス取得
   */
  _getCheckpointPath(categoryId) {
    return path.join(this.checkpointDir, `${categoryId}_checkpoint.json`);
  }

  /**
   * チェックポイント読み込み
   */
  _loadCheckpoint(categoryId) {
    const checkpointPath = this._getCheckpointPath(categoryId);
    if (fs.existsSync(checkpointPath)) {
      try {
        return JSON.parse(fs.readFileSync(checkpointPath, 'utf-8'));
      } catch (error) {
        console.warn(`⚠️ チェックポイント読み込み失敗: ${categoryId}`);
        return { problems: [], status: 'pending' };
      }
    }
    return { problems: [], status: 'pending' };
  }

  /**
   * チェックポイント保存
   */
  _saveCheckpoint(categoryId, data) {
    const checkpointPath = this._getCheckpointPath(categoryId);
    try {
      fs.writeFileSync(
        checkpointPath,
        JSON.stringify(data, null, 2),
        'utf-8'
      );
    } catch (error) {
      console.error(`❌ チェックポイント保存失敗: ${categoryId}`);
    }
  }

  /**
   * レート制限付き遅延
   */
  async _delay(ms = 800) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * カテゴリから複数コンテキスト検索
   */
  async searchCategoryContexts(category, limit = 71) {
    const searchQueries = category.keywords.map(kw => `${category.name} ${kw}`);
    const allResults = [];

    for (const query of searchQueries) {
      try {
        const results = await this.rag.search(query, Math.ceil(limit / searchQueries.length));
        allResults.push(...results);
      } catch (error) {
        console.warn(`⚠️ 検索失敗 "${query}": ${error.message}`);
      }
    }

    // 重複排除
    const uniqueResults = Array.from(
      new Map(allResults.map(r => [r.id, r])).values()
    ).slice(0, limit);

    return uniqueResults;
  }

  /**
   * 1つのコンテキストから複数問題生成
   */
  async generateMultipleProblemsFromContext(context, categoryName, seedCount = 4) {
    const problems = [];

    for (let i = 0; i < seedCount; i++) {
      try {
        const pattern = (i % 4) + 1;
        const difficulties = ['easy', 'medium', 'hard'];
        const difficulty = difficulties[i % difficulties.length];

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
          console.log(`✓ 生成: ${categoryName} - Pattern${pattern} - ${difficulty}`);
          this.stats.generated++;
        } else {
          this.stats.failed++;
        }
      } catch (error) {
        console.warn(`⚠️ 問題生成失敗: ${error.message}`);
        this.stats.failed++;
      }

      // レート制限
      if (i < seedCount - 1) {
        await this._delay(800);
      }
    }

    return problems;
  }

  /**
   * カテゴリの問題生成（チェックポイント対応）
   */
  async generateCategoryProblems(category) {
    console.log(`\n📚 ${category.name} - 目標: ${category.targetCount}問`);

    // 既存チェックポイント確認
    const checkpoint = this._loadCheckpoint(category.id);
    if (checkpoint.status === 'completed') {
      console.log(`✅ 既に完了: ${checkpoint.problems.length}問`);
      return checkpoint.problems;
    }

    // コンテキスト検索
    const contextLimit = Math.ceil(category.targetCount / 3);
    const contexts = await this.searchCategoryContexts(category, contextLimit);

    if (contexts.length === 0) {
      console.warn(`⚠️ コンテキストなし: ${category.name}`);
      return [];
    }

    console.log(`   ${contexts.length}個のコンテキストを検出`);

    // 各コンテキストから複数問題生成
    const allProblems = [...checkpoint.problems]; // 既存問題を含める
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
      const progress = Math.round(((i + 1) / contexts.length) * 100);
      console.log(`   進捗: ${progress}% (${allProblems.length}問生成)`);

      // チェックポイント保存（定期的に）
      if ((i + 1) % 5 === 0) {
        this._saveCheckpoint(category.id, {
          problems: allProblems,
          status: 'in_progress',
          lastContext: i,
          timestamp: new Date().toISOString()
        });
        console.log(`   💾 チェックポイント保存`);
      }

      // コンテキスト間の遅延
      if (i < contexts.length - 1) {
        await this._delay(1000);
      }
    }

    // 完了マーク
    const finalProblems = allProblems.slice(0, category.targetCount);
    this._saveCheckpoint(category.id, {
      problems: finalProblems,
      status: 'completed',
      timestamp: new Date().toISOString()
    });

    console.log(`   ✅ 完了: ${finalProblems.length}/${category.targetCount}問`);
    return finalProblems;
  }

  /**
   * 全カテゴリの1491問を生成
   */
  async generateAllProblems() {
    console.log('\n🚀 1491問生成を開始\n');
    this.stats.startTime = Date.now();

    const allProblems = [];
    const categoryResults = {};

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
        console.error(`❌ 生成失敗 ${category.name}: ${error.message}`);
        categoryResults[category.id] = {
          name: category.name,
          target: category.targetCount,
          generated: 0,
          success: false,
          error: error.message
        };
      }

      // カテゴリ間の遅延
      await this._delay(2000);
    }

    this.stats.endTime = Date.now();
    const duration = ((this.stats.endTime - this.stats.startTime) / 1000 / 60).toFixed(2);

    // 結果集計
    const result = {
      metadata: {
        generated_at: new Date().toISOString(),
        generation_time_minutes: duration,
        total_problems: allProblems.length,
        total_categories: this.categories.length,
        target_count: this.targetTotal,
        success_rate: `${Math.round((allProblems.length / this.targetTotal) * 100)}%`,
        stats: {
          generated: this.stats.generated,
          failed: this.stats.failed
        }
      },
      category_results: categoryResults,
      problems: allProblems
    };

    return result;
  }

  /**
   * 結果をファイルに保存
   */
  async saveResults(result, outputPath) {
    try {
      fs.writeFileSync(
        outputPath,
        JSON.stringify(result, null, 2),
        'utf-8'
      );
      console.log(`\n✅ 結果保存: ${outputPath}`);
      console.log(`📊 生成問数: ${result.metadata.total_problems}/${result.metadata.target_count}`);
      console.log(`⏱️ 所要時間: ${result.metadata.generation_time_minutes}分`);
    } catch (error) {
      console.error('❌ 結果保存失敗:', error);
      throw error;
    }
  }
}

export { ScaledRAGBulkGenerator };
