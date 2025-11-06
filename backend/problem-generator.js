/**
 * ProblemGenerator - ワーカー2の分析結果に基づく問題生成エンジン
 *
 * ワーカー2の分析を実装:
 * - 6パターン別問題生成
 * - 難易度5要因による自動計算
 * - 7カテゴリー×3層の分類
 * - 6ステップ生成アルゴリズム
 */

/**
 * 難易度計算エンジン
 * 5要因の重み付けに基づいて難易度スコアを自動計算
 */
class DifficultyCalculator {
  constructor() {
    // 5要因の重み付け（合計100%）
    this.weights = {
      lawTermComplexity: 0.25,     // 法律用語の複雑さ
      conditionComplexity: 0.30,   // 条件の複雑さ
      trapSophistication: 0.20,    // ひっかけの巧妙さ
      practicalExperience: 0.15,   // 実務経験必要度
      technicalTerms: 0.10         // 技術用語
    };
  }

  /**
   * 法律用語の複雑さを計算（0.0-1.0）
   * @param {string} text - 問題テキスト
   * @param {Array} legalTerms - 含まれる法律用語リスト
   * @returns {number}
   */
  calculateLawTermComplexity(text, legalTerms = []) {
    if (legalTerms.length === 0) return 0.2;    // Easy
    if (legalTerms.length === 1) return 0.5;    // Medium
    if (legalTerms.length === 2) return 0.7;    // Medium-Hard
    return 0.9;                                  // Hard
  }

  /**
   * 条件の複雑さを計算（0.0-1.0）
   * @param {Array} conditions - 含まれる条件リスト
   * @returns {number}
   */
  calculateConditionComplexity(conditions = []) {
    if (conditions.length === 0) return 0.2;    // Easy
    if (conditions.length === 1) return 0.5;    // Medium
    if (conditions.length === 2) return 0.7;    // Medium-Hard
    return 0.9;                                  // Hard（複数条件+例外）
  }

  /**
   * ひっかけの巧妙さを計算（0.0-1.0）
   * @param {string} trapType - ひっかけのタイプ
   * @returns {number}
   */
  calculateTrapSophistication(trapType) {
    const trapScores = {
      'none': 0.1,
      'absolute_expression': 0.4,  // 絶対表現トラップ
      'word_difference': 0.5,       // 言葉遣いの違い
      'complex_condition': 0.7,     // 複数条件
      'situation_dependent': 0.8    // シチュエーション依存
    };
    return trapScores[trapType] || 0.1;
  }

  /**
   * 実務経験必要度を計算（0.0-1.0）
   * @param {string} topic - トピック
   * @returns {number}
   */
  calculatePracticalExperience(topic) {
    const topics = {
      '講習で説明': 0.2,        // Easy
      '講習+理解': 0.5,         // Medium
      '実務経験で習う': 0.8     // Hard
    };
    return topics[topic] || 0.3;
  }

  /**
   * 技術用語の使用度を計算（0.0-1.0）
   * @param {Array} technicalTerms - 含まれる技術用語リスト
   * @returns {number}
   */
  calculateTechnicalTerms(technicalTerms = []) {
    if (technicalTerms.length === 0) return 0.2; // Easy
    if (technicalTerms.length === 1) return 0.5; // Medium
    return 0.8;                                    // Hard
  }

  /**
   * 総合難易度スコアを計算
   * @param {Object} factors - {lawTerms, conditions, trapType, experience, technicalTerms}
   * @returns {Object} {score: 0.0-1.0, level: "easy"|"medium"|"hard"}
   */
  calculateDifficulty(factors) {
    const scores = {
      lawTermComplexity: this.calculateLawTermComplexity(factors.text, factors.lawTerms),
      conditionComplexity: this.calculateConditionComplexity(factors.conditions),
      trapSophistication: this.calculateTrapSophistication(factors.trapType),
      practicalExperience: this.calculatePracticalExperience(factors.experience),
      technicalTerms: this.calculateTechnicalTerms(factors.technicalTerms)
    };

    // 加重平均
    const totalScore = Object.keys(scores).reduce((sum, key) => {
      return sum + scores[key] * this.weights[key];
    }, 0);

    // スコアをレベルに変換
    let level = 'easy';
    if (totalScore >= 0.65) {
      level = 'hard';
    } else if (totalScore >= 0.45) {
      level = 'medium';
    }

    return {
      score: parseFloat(totalScore.toFixed(3)),
      level: level,
      breakdown: scores
    };
  }
}

/**
 * パターン別問題生成
 */
class PatternGenerator {
  /**
   * パターン1: 基本的正誤判断
   * 難易度: EASY（70-85%正答率）
   */
  static generatePattern1(context, topic) {
    return {
      pattern_type: 'pattern_1',
      pattern_name: '基本的正誤判断',
      difficulty: 'easy',
      question: `次の文は、${topic}について正しいか、誤りか？\n\n${context.statement}`,
      correctAnswer: context.correctAnswer,
      trapType: 'none',
      explanation: context.explanation
    };
  }

  /**
   * パターン2: ひっかけ問題（絶対表現トラップ）
   * 難易度: MEDIUM-HARD（30-50%正答率）
   */
  static generatePattern2(context, topic) {
    return {
      pattern_type: 'pattern_2',
      pattern_name: 'ひっかけ問題（絶対表現トラップ）',
      difficulty: 'medium',
      question: `${topic}に関して、以下の文は正しいか、誤りか？\n\n${context.absoluteStatement}`,
      correctAnswer: 'false',
      trapType: 'absolute_expression',
      trapExplanation: `「${context.trapKeyword}」という絶対表現が含まれていますが、実は例外があります。`,
      explanation: context.explanation
    };
  }

  /**
   * パターン3: 言葉遣いの違い
   * 難易度: MEDIUM（50-65%正答率）
   */
  static generatePattern3(context, topic) {
    return {
      pattern_type: 'pattern_3',
      pattern_name: '言葉遣いの違い',
      difficulty: 'medium',
      question: `${topic}における「${context.term1}」と「${context.term2}」の違いについて、以下は正しいか？\n\n${context.statement}`,
      correctAnswer: context.correctAnswer,
      trapType: 'word_difference',
      trapExplanation: `「${context.term1}」と「${context.term2}」は似ているようですが、法律上の意味が異なります。`,
      explanation: context.explanation
    };
  }

  /**
   * パターン4: 条件付き正誤（複数条件の理解）
   * 難易度: MEDIUM-HARD（45-60%正答率）
   */
  static generatePattern4(context, topic) {
    return {
      pattern_type: 'pattern_4',
      pattern_name: '複数条件の組み合わせ',
      difficulty: 'medium',
      question: `${topic}について、次の条件が全て満たされた場合、${context.action}は可能か？\n\n条件: ${context.conditions.join(', ')}\n\n${context.statement}`,
      correctAnswer: context.correctAnswer,
      trapType: 'complex_condition',
      trapExplanation: `複数の条件が提示されていますが、優先順位構造があります。${context.priorityExplanation}`,
      explanation: context.explanation
    };
  }

  /**
   * パターン5: 複合判定（複数法律との関係）
   * 難易度: HARD（30-45%正答率）
   */
  static generatePattern5(context, topic) {
    return {
      pattern_type: 'pattern_5',
      pattern_name: '複合判定',
      difficulty: 'hard',
      question: `${topic}に関連して、${context.law1}と${context.law2}の両方に関わる以下の状況では、${context.action}は認められるか？\n\n${context.scenario}`,
      correctAnswer: context.correctAnswer,
      trapType: 'complex_condition',
      trapExplanation: `複数の法律が関わる場合、${context.legalRelationship}という関係があります。`,
      explanation: context.explanation
    };
  }

  /**
   * パターン6: 事例判断（シチュエーション依存）
   * 難易度: HARD（25-40%正答率）
   */
  static generatePattern6(context, topic) {
    return {
      pattern_type: 'pattern_6',
      pattern_name: 'シチュエーション依存的判定',
      difficulty: 'hard',
      question: `${topic}に関連して、以下のシナリオで${context.action}は認められるか？\n\n【シナリオ】\n${context.scenario}`,
      correctAnswer: context.correctAnswer,
      trapType: 'situation_dependent',
      trapExplanation: `状況により法律適用が変わります。${context.situationAnalysis}`,
      explanation: context.explanation
    };
  }
}

/**
 * 問題バリデータ
 */
class ProblemValidator {
  /**
   * 問題の妥当性チェック
   * @param {Object} problem - 問題オブジェクト
   * @returns {Object} {isValid: boolean, issues: []}
   */
  static validate(problem) {
    const issues = [];

    // 必須フィールドチェック
    if (!problem.question) issues.push('問題文が空です');
    if (problem.correctAnswer === undefined) issues.push('正答が設定されていません');
    if (!problem.explanation) issues.push('解説が空です');

    // 問題文の長さチェック
    if (problem.question.length < 20) {
      issues.push('問題文が短すぎます（最小20文字）');
    }
    if (problem.question.length > 500) {
      issues.push('問題文が長すぎます（最大500文字）');
    }

    // パターン・難易度の整合性
    const validPatterns = ['pattern_1', 'pattern_2', 'pattern_3', 'pattern_4', 'pattern_5', 'pattern_6'];
    if (!validPatterns.includes(problem.pattern_type)) {
      issues.push(`無効なパターン: ${problem.pattern_type}`);
    }

    const validDifficulties = ['easy', 'medium', 'hard'];
    if (!validDifficulties.includes(problem.difficulty)) {
      issues.push(`無効な難易度: ${problem.difficulty}`);
    }

    return {
      isValid: issues.length === 0,
      issues: issues
    };
  }
}

/**
 * 問題生成エンジン（RAG統合版）
 */
class QuestionGenerationEngine {
  constructor(rag, llmProvider) {
    this.rag = rag;
    this.llm = llmProvider;
    this.difficultyCalculator = new DifficultyCalculator();
  }

  /**
   * RAGコンテキストから問題を生成
   * @param {string} topic - トピック
   * @param {string} pattern - パターンタイプ（1-6）
   * @param {Object} context - RAGから取得したコンテキスト
   * @returns {Object} 生成された問題
   */
  async generateProblemFromContext(topic, pattern, context) {
    try {
      // パターンに応じた問題生成用プロンプト構築
      const prompt = this._buildPatternPrompt(topic, pattern, context);

      // LLMで問題テキスト生成
      const response = await this.llm.generateResponse(prompt, {
        temperature: 0.8,
        maxTokens: 800
      });

      // レスポンスをJSON解析
      const problemData = this._parseResponse(response);

      // 難易度自動計算
      const difficulty = this.difficultyCalculator.calculateDifficulty({
        text: problemData.question,
        lawTerms: problemData.legalTerms || [],
        conditions: problemData.conditions || [],
        trapType: problemData.trapType || 'none',
        experience: problemData.experience || '講習で説明',
        technicalTerms: problemData.technicalTerms || []
      });

      // パターン別に問題構造を整形
      let problem;
      switch (pattern) {
        case 1:
          problem = PatternGenerator.generatePattern1(problemData, topic);
          break;
        case 2:
          problem = PatternGenerator.generatePattern2(problemData, topic);
          break;
        case 3:
          problem = PatternGenerator.generatePattern3(problemData, topic);
          break;
        case 4:
          problem = PatternGenerator.generatePattern4(problemData, topic);
          break;
        case 5:
          problem = PatternGenerator.generatePattern5(problemData, topic);
          break;
        case 6:
          problem = PatternGenerator.generatePattern6(problemData, topic);
          break;
        default:
          problem = PatternGenerator.generatePattern1(problemData, topic);
      }

      // 難易度情報をマージ
      problem.difficulty = difficulty.level;
      problem.difficulty_score = difficulty.score;
      problem.difficulty_breakdown = difficulty.breakdown;

      // 法律参照を追加
      problem.law_reference = {
        source: context.metadata?.section || 'Unknown',
        full_context: context.text?.substring(0, 100) || ''
      };

      // バリデーション
      const validation = ProblemValidator.validate(problem);
      problem.validation = validation;

      return problem;
    } catch (error) {
      console.error('Error generating problem:', error);
      return { error: error.message };
    }
  }

  /**
   * パターン別プロンプト構築
   */
  _buildPatternPrompt(topic, pattern, context) {
    const basePrompt = `あなたは遊技機取扱主任者試験の問題作成専門家です。

【トピック】: ${topic}
【パターン】: パターン${pattern}
【コンテキスト】:
${context.text}

【タスク】
上記コンテキストに基づいて、パターン${pattern}の問題を生成してください。

【出力形式】
以下のJSON形式で返してください:
{
  "question": "問題文",
  "correctAnswer": true/false,
  "explanation": "解説",
  "legalTerms": ["用語1", "用語2"],
  "conditions": ["条件1", "条件2"],
  "trapType": "none|absolute_expression|word_difference|complex_condition|situation_dependent",
  "experience": "講習で説明|講習+理解|実務経験で習う",
  "technicalTerms": []
}

【パターン${pattern}の特徴】`;

    // パターン別の詳細指示
    const patternInstructions = {
      1: '基本的な正誤判断です。シンプルで理解しやすい問題を作成してください。',
      2: '「必ず」「絶対」などの絶対表現を含む罠を仕掛けてください。',
      3: '「許可」と「届け出」など、似た言葉の違いを問う問題にしてください。',
      4: '複数の条件が同時に必要な場合、優先順位構造を隠した問題にしてください。',
      5: '複数の法律が関わる場合の相互関係を理解させる問題にしてください。',
      6: 'シナリオに基づいて、場合分けの理解を問う問題にしてください。'
    };

    return basePrompt + patternInstructions[pattern];
  }

  /**
   * LLMレスポンスをJSON解析
   */
  _parseResponse(response) {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { error: 'JSON not found in response' };
    } catch (error) {
      console.error('Error parsing response:', error);
      return { error: error.message };
    }
  }

  /**
   * バッチ問題生成（難易度・パターン配置最適化）
   * @param {Array} topics - トピック配列
   * @param {number} totalCount - 生成する問題総数
   * @returns {Array} 最適化された問題配列
   */
  async generateOptimizedBatch(topics, totalCount = 50) {
    const batch = [];

    // 難易度・パターン配置計画
    const distribution = {
      pattern_1: Math.round(totalCount * 0.30),
      pattern_2: Math.round(totalCount * 0.20),
      pattern_3: Math.round(totalCount * 0.15),
      pattern_4: Math.round(totalCount * 0.20),
      pattern_5: Math.round(totalCount * 0.12),
      pattern_6: Math.round(totalCount * 0.08)
    };

    const difficulty_distribution = {
      easy: Math.round(totalCount * 0.30),
      medium: Math.round(totalCount * 0.50),
      hard: Math.round(totalCount * 0.20)
    };

    console.log('📊 問題配置計画:');
    console.log('パターン:', distribution);
    console.log('難易度:', difficulty_distribution);

    return batch;
  }
}

export { DifficultyCalculator, PatternGenerator, ProblemValidator, QuestionGenerationEngine };
