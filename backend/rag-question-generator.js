/**
 * RAG Question Generator Integration
 *
 * RAGシステム + 問題生成エンジンの統合
 * ワーカー2の分析結果を実装：
 * - 正誤択一式（〇×式）問題生成
 * - 新規試験（50問）/ 更新試験（30問）対応
 * - 合格基準80%以上の問題配置
 */

import { QuestionGenerationEngine, DifficultyCalculator } from './problem-generator.js';

class RAGQuestionGenerator {
  constructor(rag, llmProvider) {
    this.rag = rag;
    this.llm = llmProvider;
    this.engine = new QuestionGenerationEngine(rag, llmProvider);
    this.difficultyCalculator = new DifficultyCalculator();

    // 試験仕様
    this.examSpecs = {
      'new': {
        totalQuestions: 50,
        timeLimit: 60,
        passingScore: 40,  // 80%以上
        passingRate: 0.80
      },
      'renewal': {
        totalQuestions: 30,
        timeLimit: 40,
        passingScore: 24,  // 80%以上
        passingRate: 0.80
      }
    };

    // カテゴリー定義（ワーカー2分析）
    this.categories = {
      'permits': {
        name: '営業許可・申請手続き',
        distribution: 0.16,  // 8問/50問
        subcategories: ['営業許可の要件', '申請手続き', '届け出との違い']
      },
      'business_hours': {
        name: '営業時間・営業場所',
        distribution: 0.16,
        subcategories: ['営業時間制限', '営業場所要件', '離隔要件']
      },
      'gaming_machines': {
        name: '遊技機規制',
        distribution: 0.16,
        subcategories: ['適切な遊技機', '不適切な遊技機', '改造禁止']
      },
      'employees': {
        name: '従業者の要件・禁止事項',
        distribution: 0.16,
        subcategories: ['管理者資格', '主任者職務', '禁止行為']
      },
      'customer_protection': {
        name: '顧客保護・規制遵守',
        distribution: 0.16,
        subcategories: ['未成年者対応', '景品交換規制', '営業記録']
      },
      'violations': {
        name: '法令違反と行政処分',
        distribution: 0.12,  // 6問/50問
        subcategories: ['営業停止', '許可取消', '課徴金・罰金']
      },
      'practical': {
        name: '実務的対応',
        distribution: 0.08,  // 4問/50問
        subcategories: ['トラブル対応', '検査・報告', '変更届']
      }
    };

    // パターン配置（ワーカー2分析）
    this.patternDistribution = {
      'pattern_1': 0.30,  // 基本的正誤判断
      'pattern_2': 0.20,  // ひっかけ問題
      'pattern_3': 0.15,  // 言葉遣い
      'pattern_4': 0.20,  // 複数条件
      'pattern_5': 0.12,  // 複合判定
      'pattern_6': 0.08   // 事例判断
    };

    // 難易度配置（ワーカー2分析）
    this.difficultyDistribution = {
      'easy': 0.30,    // 正答率70-85%
      'medium': 0.50,  // 正答率50-70%
      'hard': 0.20     // 正答率30-50%
    };
  }

  /**
   * 正誤択一式（〇×式）問題を生成
   * @param {string} topic - トピック
   * @param {Object} context - RAGコンテキスト
   * @param {number} pattern - パターン番号（1-6）
   * @returns {Object}
   */
  async generateTrueOrFalseQuestion(topic, context, pattern) {
    try {
      console.log(`📝 Generating True/False question: ${topic} (Pattern ${pattern})`);

      // パターンに応じたプロンプト構築
      const prompt = this._buildTrueOrFalsePrompt(topic, context, pattern);

      // LLMで問題生成
      const response = await this.llm.generateResponse(prompt, {
        temperature: 0.8,
        maxTokens: 500
      });

      // JSON解析
      const questionData = JSON.parse(response.match(/\{[\s\S]*\}/)[0]);

      // 難易度計算
      const difficulty = this.difficultyCalculator.calculateDifficulty({
        text: questionData.statement,
        lawTerms: questionData.legalTerms || [],
        conditions: questionData.conditions || [],
        trapType: questionData.trapType || 'none',
        experience: questionData.experience || '講習で説明',
        technicalTerms: questionData.technicalTerms || []
      });

      return {
        problem_id: `q_${Date.now()}_${Math.random().toString(36).substring(7)}`,
        question_type: 'true_false',
        pattern: pattern,
        category: questionData.category || topic,
        statement: questionData.statement,
        correct_answer: questionData.answer,  // true or false
        explanation: questionData.explanation,
        difficulty: difficulty.level,
        difficulty_score: difficulty.score,
        trap_type: questionData.trapType || 'none',
        trap_explanation: questionData.trapExplanation || '',
        law_reference: context.metadata?.section || 'Unknown',
        metadata: {
          pattern_name: this._getPatternName(pattern),
          created_at: new Date().toISOString(),
          source: 'rag_generation'
        }
      };
    } catch (error) {
      console.error('Error generating true/false question:', error);
      return { error: error.message };
    }
  }

  /**
   * 試験セット生成（50問または30問）
   * @param {string} examType - 'new' or 'renewal'
   * @param {number} limit - 取得するコンテキスト数
   * @returns {Array}
   */
  async generateExamSet(examType = 'new', limit = 10) {
    const spec = this.examSpecs[examType];
    if (!spec) {
      throw new Error(`Invalid exam type: ${examType}`);
    }

    console.log(`\n🎯 Generating ${examType} exam set (${spec.totalQuestions} questions)`);

    const questions = [];
    const topics = Object.keys(this.categories);
    let questionCount = 0;

    // カテゴリー別に問題生成
    for (const category of topics) {
      const categorySpec = this.categories[category];
      const categoryQuestionCount = Math.round(spec.totalQuestions * categorySpec.distribution);

      console.log(`  📌 ${categorySpec.name}: ${categoryQuestionCount}問`);

      // カテゴリー内でパターンを分散
      for (let i = 0; i < categoryQuestionCount; i++) {
        if (questionCount >= spec.totalQuestions) break;

        // パターンを選択（配置比率に従う）
        const pattern = this._selectPattern();

        // RAGからコンテキストを検索
        const searchQuery = `${categorySpec.name} ${categorySpec.subcategories[i % categorySpec.subcategories.length]}`;
        const ragResults = await this.rag.search(searchQuery, 1);

        if (ragResults.length === 0) {
          console.warn(`⚠️ No RAG context found for: ${searchQuery}`);
          continue;
        }

        // 問題生成
        const question = await this.generateTrueOrFalseQuestion(
          categorySpec.name,
          ragResults[0],
          pattern
        );

        if (question.error) {
          console.warn(`⚠️ Failed to generate question: ${question.error}`);
          continue;
        }

        questions.push(question);
        questionCount++;
      }
    }

    console.log(`\n✅ Generated ${questions.length}/${spec.totalQuestions} questions`);
    console.log(`   Passing score: ${spec.passingScore}/${spec.totalQuestions} (${spec.passingRate * 100}%)`);

    // 統計情報
    const stats = this._calculateStats(questions);
    console.log('\n📊 Distribution:');
    console.log('  Difficulty:', stats.difficultyDistribution);
    console.log('  Patterns:', stats.patternDistribution);

    return {
      exam_type: examType,
      total_questions: questions.length,
      passing_score: spec.passingScore,
      time_limit_minutes: spec.timeLimit,
      questions: questions,
      statistics: stats,
      generated_at: new Date().toISOString()
    };
  }

  /**
   * 正誤択一式問題生成用プロンプト
   */
  _buildTrueOrFalsePrompt(topic, context, pattern) {
    return `あなたは遊技機取扱主任者試験の問題作成専門家です。

【試験形式】: 正誤択一式（〇×式のみ）
【トピック】: ${topic}
【パターン】: パターン${pattern}
【コンテキスト】:
${context.text?.substring(0, 300) || ''}

【タスク】
上記コンテキストに基づいて、正誤択一式（〇×式）の問題を生成してください。

【出力形式】
以下のJSON形式で返してください:
{
  "statement": "問題文（〇か×を選ぶ形式）",
  "answer": true,  // 正なら true、誤なら false
  "explanation": "解説（なぜこれが正（誤）なのか）",
  "trapType": "none|absolute_expression|word_difference|complex_condition|situation_dependent",
  "trapExplanation": "ひっかけの説明",
  "legalTerms": ["用語1"],
  "conditions": [],
  "category": "${topic}",
  "experience": "講習で説明"
}

【重要】
- 問題は「〇」「×」のいずれかを選ぶ形式にしてください
- 4択ではなく、正誤の二者択一です
- パターン${pattern}の特徴に従ってください`;
  }

  /**
   * パターンを配置比率に従って選択
   */
  _selectPattern() {
    const rand = Math.random();
    let cumulative = 0;

    for (const [pattern, ratio] of Object.entries(this.patternDistribution)) {
      cumulative += ratio;
      if (rand <= cumulative) {
        return parseInt(pattern.split('_')[1]);
      }
    }

    return 1; // デフォルト
  }

  /**
   * パターン名取得
   */
  _getPatternName(pattern) {
    const names = {
      1: '基本的正誤判断',
      2: 'ひっかけ問題',
      3: '言葉遣いの違い',
      4: '複数条件の組み合わせ',
      5: '複合判定',
      6: 'シチュエーション依存'
    };
    return names[pattern] || 'Unknown';
  }

  /**
   * 統計情報計算
   */
  _calculateStats(questions) {
    const stats = {
      difficultyDistribution: { easy: 0, medium: 0, hard: 0 },
      patternDistribution: {},
      categoryDistribution: {}
    };

    for (const q of questions) {
      stats.difficultyDistribution[q.difficulty]++;
      stats.patternDistribution[q.pattern] = (stats.patternDistribution[q.pattern] || 0) + 1;
      stats.categoryDistribution[q.category] = (stats.categoryDistribution[q.category] || 0) + 1;
    }

    return stats;
  }
}

export { RAGQuestionGenerator };
