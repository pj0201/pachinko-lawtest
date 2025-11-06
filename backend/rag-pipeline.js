/**
 * RAGPipeline - 検索→コンテキスト生成→問題生成のパイプライン
 *
 * フロー:
 * 1. ユーザークエリ受け取り
 * 2. Chromaで関連テキスト検索
 * 3. LLMで問題生成
 * 4. 質問結果を返却
 */

import { ChromaRAG } from './chroma-rag.js';
import { LLMProviderFactory } from './llm-provider.js';

class RAGPipeline {
  constructor(rag, llmProvider) {
    this.rag = rag;
    this.llm = llmProvider;
  }

  /**
   * テキストから問題を生成
   * @param {string} topic - トピック（例：「遊技機の定義」）
   * @param {number} count - 問題数
   * @returns {Object}
   */
  async generateQuestionsForTopic(topic, count = 3) {
    try {
      console.log(`\n📖 Generating questions for topic: "${topic}"\n`);

      // 1. Chromaで関連テキストを検索
      const context = await this.rag.generateContext(topic, count + 2);

      // 2. LLMで問題生成
      const prompt = this._buildQuestionPrompt(topic, context, count);
      const response = await this.llm.generateResponse(prompt, {
        temperature: 0.7,
        maxTokens: 2000
      });

      // 3. JSONパース
      const questions = this._parseQuestions(response);

      return {
        topic,
        count: questions.length,
        questions,
        context_tokens_used: this._estimateTokens(context),
        success: questions.length > 0
      };
    } catch (error) {
      console.error('❌ Error generating questions:', error);
      return {
        topic,
        error: error.message,
        success: false
      };
    }
  }

  /**
   * 質問プロンプト構築
   */
  _buildQuestionPrompt(topic, context, count) {
    return `あなたは日本の遊技機取扱主任者講習試験の出題専門家です。

【コンテキスト】
${context}

【タスク】
上記のコンテキストを基に、「${topic}」に関する${count}問の四択問題を生成してください。

【出力形式】
以下のJSON形式で返してください。複数の問題がある場合は配列で返してください。

[
  {
    "question": "問題文",
    "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "correct_index": 0,
    "explanation": "解説（コンテキストに基づいた正解理由）",
    "difficulty": "easy|medium|hard",
    "source_section": "元となったコンテキストのセクション名"
  }
]

【要件】
1. コンテキストに記載されている内容に基づくこと
2. 日本語で自然な問題文・選択肢にすること
3. 正答は複数でなく1つのみ
4. 難易度は適切に設定すること（easy：基本、medium：応用、hard：深掘り）`;
  }

  /**
   * 問題JSON解析
   */
  _parseQuestions(response) {
    try {
      // JSONブロック抽出
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (!jsonMatch) {
        console.error('No JSON found in response');
        return [];
      }

      const parsed = JSON.parse(jsonMatch[0]);
      return Array.isArray(parsed) ? parsed : [parsed];
    } catch (error) {
      console.error('Error parsing questions:', error);
      return [];
    }
  }

  /**
   * トークン数推定（雑い推定）
   */
  _estimateTokens(text) {
    // 日本語は2-3文字 = 1トークン程度
    return Math.ceil(text.length / 2);
  }

  /**
   * インタラクティブモード：複数トピックから問題生成
   */
  async generateQuestionsMultipleTopics(topics, questionsPerTopic = 2) {
    const results = [];

    for (const topic of topics) {
      const result = await this.generateQuestionsForTopic(topic, questionsPerTopic);
      results.push(result);

      // API呼び出しの間隔を設ける（レート制限対策）
      if (topics.indexOf(topic) < topics.length - 1) {
        await this._delay(1000);
      }
    }

    return {
      total_topics: topics.length,
      total_questions: results.reduce((sum, r) => sum + (r.questions?.length || 0), 0),
      results
    };
  }

  /**
   * 遅延ユーティリティ
   */
  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 関連テキスト検索（デバッグ用）
   */
  async searchRelatedText(query, limit = 5) {
    return await this.rag.search(query, limit);
  }

  /**
   * コンテキスト生成（デバッグ用）
   */
  async getContext(query) {
    return await this.rag.generateContext(query);
  }
}

/**
 * パイプラインファクトリ
 */
class RAGPipelineFactory {
  static async create(rag, llmProvider) {
    if (!rag || !llmProvider) {
      throw new Error('RAG and LLMProvider instances are required');
    }
    return new RAGPipeline(rag, llmProvider);
  }
}

export { RAGPipeline, RAGPipelineFactory };
