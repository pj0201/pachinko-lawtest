/**
 * Advanced Problem Generator - ワーカー2仕様に基づく改善版
 *
 * ワーカー2が提供した6ステップアルゴリズムの詳細実装：
 * - Step 0: 初期化フェーズ
 * - Step 1: 問題ソース選定
 * - Step 2: 法律ロジック分析（詳細化）
 * - Step 3: パターン別問題生成（疑似コード実装）
 * - Step 4: 解説自動生成
 * - Step 5: 難易度検証・調整（詳細指標）
 * - Step 6: 高度なバリデーション
 */

/**
 * Step 2: 法律ロジック分析エンジン
 * 選定された法律条文のロジック構造を詳細分析
 */
class LawLogicAnalyzer {
  constructor() {
    // 例外キーワードパターン
    this.exceptionPatterns = [
      'ただし',
      'これを妨げない',
      'この限りではない',
      '除外される',
      '例外',
      '特例',
      '但し',
      'ただし'
    ];

    // 法律用語リスト
    this.legalTerms = {
      '許可': { category: '申請', weight: 0.8 },
      '届け出': { category: '申請', weight: 0.7 },
      '義務': { category: '要件', weight: 0.9 },
      '禁止': { category: '禁止事項', weight: 0.9 },
      '申請': { category: '申請', weight: 0.8 },
      '報告': { category: '申請', weight: 0.6 },
      '取消': { category: '処分', weight: 0.9 },
      '停止': { category: '処分', weight: 0.8 }
    };
  }

  /**
   * Step 2A: 主要ルール抽出
   * @param {Object} source - RAGコンテキスト
   * @returns {string}
   */
  extractMainRule(source) {
    // テキストの最初の文を主要ルールとして抽出
    const sentences = source.text.split(/[。、]/);
    if (sentences.length > 0) {
      // 「～は...」の形式の文を優先
      const mainSentence = sentences.find(s => s.includes('は')) || sentences[0];
      return mainSentence.trim().substring(0, 100);
    }
    return source.text.substring(0, 100);
  }

  /**
   * Step 2B: 例外条項の特定
   * @param {Object} source - RAGコンテキスト
   * @returns {Array}
   */
  findExceptionClauses(source) {
    const exceptions = [];
    const text = source.text;

    for (const pattern of this.exceptionPatterns) {
      const regex = new RegExp(`${pattern}([^。]*)[。]`, 'g');
      let match;
      while ((match = regex.exec(text)) !== null) {
        exceptions.push(match[1].trim());
      }
    }

    return exceptions;
  }

  /**
   * Step 2C: 関連条文の特定
   * @param {Object} source - RAGコンテキスト
   * @returns {Array}
   */
  findRelatedArticles(source) {
    const articles = [];

    // 「第〇条」パターンを抽出
    const articlePattern = /第(\d+)条/g;
    let match;
    const text = source.text;

    while ((match = articlePattern.exec(text)) !== null) {
      articles.push({
        article_number: parseInt(match[1]),
        reference: match[0]
      });
    }

    return articles;
  }

  /**
   * Step 2D: キーとなる法律用語の抽出
   * @param {Object} source - RAGコンテキスト
   * @returns {Array}
   */
  extractKeyTerms(source) {
    const keyTerms = [];
    const text = source.text.toLowerCase();

    for (const [term, info] of Object.entries(this.legalTerms)) {
      if (text.includes(term)) {
        keyTerms.push({
          term: term,
          category: info.category,
          weight: info.weight
        });
      }
    }

    // 重みでソート（重要な用語が先）
    return keyTerms.sort((a, b) => b.weight - a.weight);
  }

  /**
   * Step 2E: 判定ツリーの作成
   * @param {Object} analysis - 分析結果
   * @returns {Object}
   */
  buildDecisionTree(analysis) {
    const tree = {
      root: {
        condition: analysis.main_rule,
        children: []
      }
    };

    // 例外条項をツリーノードとして追加
    if (analysis.exception_clauses && analysis.exception_clauses.length > 0) {
      tree.root.children.push({
        condition: '例外条項が存在するか',
        branches: {
          'yes': analysis.exception_clauses,
          'no': '主要ルールが適用'
        }
      });
    }

    // キーとなる用語に基づく条件分岐
    if (analysis.key_terms && analysis.key_terms.length > 0) {
      for (const term of analysis.key_terms) {
        tree.root.children.push({
          condition: `「${term.term}」の定義は正確か`,
          category: term.category
        });
      }
    }

    return tree;
  }

  /**
   * 完全な法律ロジック分析
   */
  analyzeComprehensive(source) {
    const analysis = {
      main_rule: this.extractMainRule(source),
      exception_clauses: this.findExceptionClauses(source),
      related_articles: this.findRelatedArticles(source),
      key_terms: this.extractKeyTerms(source),
      decision_tree: null
    };

    analysis.decision_tree = this.buildDecisionTree(analysis);

    return analysis;
  }
}

/**
 * Step 3-6: 詳細な問題生成・検証エンジン
 */
class AdvancedQuestionGenerator {
  constructor(lawAnalyzer) {
    this.lawAnalyzer = lawAnalyzer;
  }

  /**
   * Step 4: 解説の構造化生成
   */
  generateStructuredExplanation(problem, analysis) {
    const explanation = {
      core_point: '',
      correct_reasoning: '',
      common_mistakes: [],
      law_citation: ''
    };

    // コアポイント
    if (problem.answer === true) {
      explanation.core_point = `✅ 正しい: ${analysis.main_rule}`;
    } else {
      const error = analysis.exception_clauses[0] || 'ルール違反';
      explanation.core_point = `❌ 誤り: ${error}があるため、問題文の内容は不適切です`;
    }

    // 正しい理由（詳述）
    explanation.correct_reasoning = this._buildCorrectReasoning(problem, analysis);

    // よくある誤解
    explanation.common_mistakes = [
      ...analysis.key_terms.map(t => `「${t.term}」の定義を誤解する`),
      ...(analysis.exception_clauses.length > 0 ? ['例外条項を見落とす'] : []),
      ...(analysis.related_articles.length > 0 ? [`関連条文（第${analysis.related_articles[0].article_number}条）との整合性を見落とす`] : [])
    ];

    // 法律引用
    if (analysis.related_articles.length > 0) {
      explanation.law_citation = `参照: ${analysis.related_articles.map(a => a.reference).join(', ')}`;
    } else {
      explanation.law_citation = '風営法および関連法令参照';
    }

    return explanation;
  }

  /**
   * 正しい理由を構築
   */
  _buildCorrectReasoning(problem, analysis) {
    if (problem.answer === true) {
      return `${analysis.main_rule}のため、この記述は正しい。${
        analysis.key_terms.length > 0
          ? `特に「${analysis.key_terms[0].term}」の概念が重要。`
          : ''
      }`;
    } else {
      if (analysis.exception_clauses.length > 0) {
        return `問題文では「${analysis.main_rule}」とされていますが、実は「${analysis.exception_clauses[0]}」という例外があります。`;
      }
      return `主要ルールに矛盾があります。詳細な法律解釈が必要です。`;
    }
  }

  /**
   * Step 5: 詳細な難易度スコア計算
   * ワーカー2が提供した指標ベースの計算
   */
  calculateDetailedDifficultyScore(problem, analysis) {
    // 各指標を計算
    const indicators = {
      term_complexity: this._calculateTermComplexity(analysis.key_terms),
      sentence_length: Math.min(problem.statement.length / 100, 1.0) * 0.15,
      condition_count: Math.min(analysis.decision_tree?.root.children?.length || 0, 3) * 0.10,
      trap_subtlety: problem.trap_mechanism ? 0.20 : 0.0,
      exception_presence: (analysis.exception_clauses.length > 0) ? 0.10 : 0.0
    };

    // ワーカー2の指標に基づいた加重平均
    const difficultyScore = (
      indicators.term_complexity * 0.25 +
      indicators.sentence_length * 0.15 +
      indicators.condition_count * 0.30 +
      indicators.trap_subtlety * 0.20 +
      indicators.exception_presence * 0.10
    );

    // 推定正答率を逆算（ワーカー2の式）
    const estimatedCorrectRate = Math.max(0, 1.0 - difficultyScore);

    // 難易度分類
    let difficulty = 'easy';
    if (estimatedCorrectRate < 0.50) {
      difficulty = 'hard';
    } else if (estimatedCorrectRate < 0.70) {
      difficulty = 'medium';
    }

    return {
      score: parseFloat(difficultyScore.toFixed(3)),
      estimated_correct_rate: parseFloat(estimatedCorrectRate.toFixed(3)),
      difficulty: difficulty,
      indicators: indicators
    };
  }

  /**
   * 用語複雑度の計算
   */
  _calculateTermComplexity(keyTerms) {
    if (keyTerms.length === 0) return 0.0;
    if (keyTerms.length === 1) return 0.25;
    if (keyTerms.length === 2) return 0.50;
    return 0.75;
  }

  /**
   * Step 6: 高度なバリデーション
   */
  validateProblemQuality(problem, analysis) {
    const issues = [];

    // チェック1: 曖昧性の検出
    if (this._hasAmbiguity(problem.statement)) {
      issues.push('曖昧な表現が含まれている可能性があります');
    }

    // チェック2: 複数解釈の検出
    const interpretations = this._extractPossibleInterpretations(problem.statement);
    if (interpretations.length > 1) {
      issues.push(`複数の解釈が可能: ${interpretations.join(', ')}`);
    }

    // チェック3: 法律的正確性の検証
    if (!this._verifyLawAccuracy(problem, analysis)) {
      issues.push('法律的に不正確な可能性があります');
    }

    // チェック4: 解説の完全性
    if (!problem.explanation?.law_citation) {
      issues.push('法律引用が不足しています');
    }

    // チェック5: ひっかけの正当性
    if (problem.trap_mechanism && !this._validateTrapJustification(problem.trap_mechanism, analysis)) {
      issues.push('ひっかけが不当である可能性があります');
    }

    return {
      is_valid: issues.length === 0,
      issues: issues,
      severity: issues.length === 0 ? 'pass' : (issues.length <= 2 ? 'warning' : 'error')
    };
  }

  /**
   * 曖昧性検出
   */
  _hasAmbiguity(statement) {
    const ambiguousPatterns = [
      /ある程度/,
      /だいたい/,
      /ほぼ/,
      /可能性がある/,
      /かもしれない/
    ];

    return ambiguousPatterns.some(pattern => pattern.test(statement));
  }

  /**
   * 複数解釈の検出
   */
  _extractPossibleInterpretations(statement) {
    const interpretations = [];

    // 複数の「または」を含む場合
    if ((statement.match(/または/g) || []).length > 1) {
      interpretations.push('複数選択肢による解釈の多様性');
    }

    // 複数の「と」を含む場合（列挙）
    if ((statement.match(/と/g) || []).length > 2) {
      interpretations.push('複数の条件による複雑な解釈');
    }

    return interpretations;
  }

  /**
   * 法律的正確性の検証
   */
  _verifyLawAccuracy(problem, analysis) {
    // 主要ルールが問題文に含まれているか
    if (problem.statement.includes(analysis.main_rule.substring(0, 30))) {
      return true;
    }

    // 関連条文が参照されているか
    if (analysis.related_articles.length > 0) {
      return true;
    }

    return false;
  }

  /**
   * ひっかけの正当性検証
   */
  _validateTrapJustification(trapMechanism, analysis) {
    // ひっかけが例外条項に基づいているか
    if (trapMechanism.includes('例外') && analysis.exception_clauses.length > 0) {
      return true;
    }

    // ひっかけが用語定義に基づいているか
    if (trapMechanism.includes('定義') && analysis.key_terms.length > 0) {
      return true;
    }

    // その他の正当なひっかけ
    if (trapMechanism.includes('誤解') || trapMechanism.includes('見落とし')) {
      return true;
    }

    return false;
  }
}

/**
 * 統合: Step 0-6の完全なフロー
 */
class CompleteQuestionGenerationPipeline {
  constructor(rag, llmProvider) {
    this.rag = rag;
    this.llm = llmProvider;
    this.lawAnalyzer = new LawLogicAnalyzer();
    this.questionGenerator = new AdvancedQuestionGenerator(this.lawAnalyzer);
  }

  /**
   * Step 0: 初期化フェーズ
   */
  initializeGenerationContext(totalQuestions = 50) {
    return {
      total_questions: totalQuestions,
      difficulty_distribution: {
        easy: Math.round(totalQuestions * 0.30),
        medium: Math.round(totalQuestions * 0.50),
        hard: Math.round(totalQuestions * 0.20)
      },
      pattern_distribution: {
        pattern_1: Math.round(totalQuestions * 0.30),
        pattern_2: Math.round(totalQuestions * 0.20),
        pattern_3: Math.round(totalQuestions * 0.15),
        pattern_4: Math.round(totalQuestions * 0.20),
        pattern_5: Math.round(totalQuestions * 0.12),
        pattern_6: Math.round(totalQuestions * 0.08)
      },
      category_distribution: {
        category_1: 8,  // 営業許可
        category_2: 8,  // 営業時間
        category_3: 8,  // 遊技機規制
        category_4: 8,  // 従業者要件
        category_5: 8,  // 顧客保護
        category_6: 6,  // 法令違反
        category_7: 4   // 実務対応
      },
      generated_problems: [],
      usage_tracking: {}  // 問題ソースの使用回数追跡
    };
  }

  /**
   * Step 1: 問題ソース選定（シミュレーション）
   */
  selectProblemSource(context, category, pattern) {
    // 実装では、データベースから選定
    // ここではRAGからの検索結果を使用
    return {
      category: category,
      pattern: pattern,
      use_count: (context.usage_tracking[category] || 0)
    };
  }

  /**
   * 完全なフロー実行（Step 0-6）
   */
  async executeCompleteFlow(ragContext, pattern, selectedDifficulty) {
    try {
      // Step 0: 初期化
      const context = this.initializeGenerationContext();

      // Step 2: 法律ロジック分析
      const lawAnalysis = this.lawAnalyzer.analyzeComprehensive(ragContext);

      // Step 3: パターン別問題生成
      const problemData = await this._generatePatternedQuestion(
        lawAnalysis,
        pattern,
        selectedDifficulty
      );

      // Step 4: 解説生成
      problemData.explanation = this.questionGenerator.generateStructuredExplanation(
        problemData,
        lawAnalysis
      );

      // Step 5: 難易度検証・調整
      const difficultyAnalysis = this.questionGenerator.calculateDetailedDifficultyScore(
        problemData,
        lawAnalysis
      );
      problemData.difficulty_score = difficultyAnalysis.score;
      problemData.estimated_correct_rate = difficultyAnalysis.estimated_correct_rate;
      problemData.difficulty = difficultyAnalysis.difficulty;

      // Step 6: バリデーション
      const validation = this.questionGenerator.validateProblemQuality(
        problemData,
        lawAnalysis
      );
      problemData.validation = validation;

      return {
        success: validation.is_valid,
        problem: problemData,
        analysis: lawAnalysis,
        validation: validation
      };
    } catch (error) {
      console.error('Pipeline error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * パターン別問題生成（LLM連携）
   */
  async _generatePatternedQuestion(lawAnalysis, pattern, difficulty) {
    const prompt = this._buildPatternedPrompt(lawAnalysis, pattern, difficulty);

    const response = await this.llm.generateResponse(prompt, {
      temperature: 0.7,
      maxTokens: 600
    });

    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (e) {
      console.warn('Failed to parse LLM response');
    }

    return { statement: 'エラー', answer: null };
  }

  /**
   * パターン別プロンプト構築
   */
  _buildPatternedPrompt(lawAnalysis, pattern, difficulty) {
    const patternGuides = {
      1: '法律に明確に書いてあることをそのまま出題してください。',
      2: '「必ず」「絶対」などの絶対表現を含めて、例外を見落とさせるひっかけを仕掛けてください。',
      3: `「${lawAnalysis.key_terms[0]?.term}」など、似た概念だが異なる法律用語の違いを理解させてください。`,
      4: '複数の条件が同時に必要な場合、優先順位構造を隠した問題にしてください。',
      5: '複数の法律が関わる場合の相互関係を理解させる問題にしてください。',
      6: 'シナリオに基づいて、場合分けの理解を問う問題にしてください。'
    };

    return `
遊技機取扱主任者試験の問題を生成してください。

【パターン${pattern}】: ${patternGuides[pattern]}

【法律分析結果】
主要ルール: ${lawAnalysis.main_rule}
例外条項: ${lawAnalysis.exception_clauses.length > 0 ? lawAnalysis.exception_clauses[0] : 'なし'}
キー用語: ${lawAnalysis.key_terms.map(t => t.term).join(', ')}

【難易度】: ${difficulty}

【出力】
JSON形式で以下を返してください:
{
  "statement": "問題文",
  "answer": true/false,
  "trap_mechanism": "ひっかけの説明",
  "statement_structure": {"premise": "前置き", "body": "本文"}
}
    `;
  }
}

export {
  LawLogicAnalyzer,
  AdvancedQuestionGenerator,
  CompleteQuestionGenerationPipeline
};
