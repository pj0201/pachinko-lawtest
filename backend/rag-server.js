/**
 * RAG API Server - Express.js ベースのRAGバックエンド
 *
 * エンドポイント:
 * POST /api/rag/init - RAG初期化
 * POST /api/questions/generate - 問題生成
 * GET /api/questions/search - テキスト検索
 * POST /api/questions/categorize - 問題カテゴライズ
 * POST /api/progress/analyze - 学習進捗分析
 * GET /api/health - ヘルスチェック
 * GET /api/config/providers - LLMプロバイダ一覧
 */

import express from 'express';
import cors from 'cors';
import { RAGInitializer, ChromaRAG } from './chroma-rag.js';
import { RAGPipeline, RAGPipelineFactory } from './rag-pipeline.js';
import { LLMProviderFactory } from './llm-provider.js';
import { QuestionCategorizer } from './question-categorizer.js';
import { RAGQuestionGenerator } from './rag-question-generator.js';
import { CompleteQuestionGenerationPipeline } from './advanced-problem-generator.js';
import dotenv from 'dotenv';

dotenv.config();

class RAGServer {
  constructor(config = {}) {
    this.app = express();
    this.config = config;
    this.rag = null;
    this.pipeline = null;
    this.categorizer = new QuestionCategorizer();
    this.llmProvider = null;
    this.questionGenerator = null;
    this.completePipeline = null;  // ワーカー2仕様版

    this._setupMiddleware();
    this._setupRoutes();
  }

  _setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  _setupRoutes() {
    // ヘルスチェック
    this.app.get('/api/health', (req, res) => {
      res.json({
        status: 'ok',
        ragReady: !!this.rag,
        pipelineReady: !!this.pipeline,
        llmProvider: this.llmProvider?.constructor?.name || 'none'
      });
    });

    // LLMプロバイダ一覧
    this.app.get('/api/config/providers', (req, res) => {
      res.json({
        availableProviders: ['groq', 'openai', 'claude', 'mistral', 'ollama'],
        currentProvider: this.llmProvider?.constructor?.name || 'none',
        configRequired: {
          groq: 'GROQ_API_KEY',
          openai: 'OPENAI_API_KEY',
          claude: 'CLAUDE_API_KEY',
          mistral: 'MISTRAL_API_KEY',
          ollama: '(ローカル - APIキー不要)'
        }
      });
    });

    // RAG初期化
    this.app.post('/api/rag/init', async (req, res) => {
      try {
        console.log('🚀 RAG initialization requested...');

        const result = await RAGInitializer.initialize({
          ocrPath: req.body.ocrPath || '/home/planj/patshinko-exam-app/data/ocr_results_corrected.json',
          windPath: req.body.windPath || '/home/planj/Claude-Code-Communication/resources/legal/wind_eikyo_law/wind_eikyo_law_v1.0.md'
        });

        this.rag = result.rag;

        // LLMプロバイダ初期化
        const provider = req.body.llmProvider || process.env.LLM_PROVIDER || 'groq';
        const apiKey = req.body.apiKey || process.env[`${provider.toUpperCase()}_API_KEY`];

        this.llmProvider = LLMProviderFactory.create(provider, {
          apiKey: apiKey,
          model: req.body.model || process.env[`${provider.toUpperCase()}_MODEL`]
        });

        // パイプライン初期化
        this.pipeline = await RAGPipelineFactory.create(this.rag, this.llmProvider);

        // 問題生成エンジン初期化
        this.questionGenerator = new RAGQuestionGenerator(this.rag, this.llmProvider);

        // ワーカー2仕様版パイプライン初期化
        this.completePipeline = new CompleteQuestionGenerationPipeline(this.rag, this.llmProvider);

        res.json({
          success: true,
          message: 'RAG system initialized',
          stats: result.stats,
          provider: provider,
          examSpecs: {
            new: { questions: 50, timeLimit: 60, passingScore: 40 },
            renewal: { questions: 30, timeLimit: 40, passingScore: 24 }
          }
        });
      } catch (error) {
        console.error('❌ RAG initialization error:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // 問題生成
    this.app.post('/api/questions/generate', async (req, res) => {
      try {
        if (!this.pipeline) {
          return res.status(400).json({
            error: 'RAG not initialized. Call /api/rag/init first'
          });
        }

        const { topic, count = 3, topics } = req.body;

        let result;
        if (topic) {
          // 単一トピック
          result = await this.pipeline.generateQuestionsForTopic(topic, count);
          result = { topics: 1, ...result };
        } else if (topics) {
          // 複数トピック
          result = await this.pipeline.generateQuestionsMultipleTopics(topics, count);
        } else {
          return res.status(400).json({
            error: 'Either "topic" or "topics" parameter required'
          });
        }

        // カテゴライズ
        if (result.questions) {
          result.questions = this.categorizer.categorizeQuestions(result.questions);
        } else if (result.results) {
          result.results = result.results.map(r => ({
            ...r,
            questions: this.categorizer.categorizeQuestions(r.questions || [])
          }));
        }

        res.json(result);
      } catch (error) {
        console.error('❌ Question generation error:', error);
        res.status(500).json({
          error: error.message
        });
      }
    });

    // テキスト検索
    this.app.get('/api/questions/search', async (req, res) => {
      try {
        if (!this.rag) {
          return res.status(400).json({ error: 'RAG not initialized' });
        }

        const { query, limit = 5 } = req.query;
        if (!query) {
          return res.status(400).json({ error: 'query parameter required' });
        }

        const results = await this.rag.search(query, parseInt(limit));
        res.json({
          query,
          resultCount: results.length,
          results
        });
      } catch (error) {
        console.error('❌ Search error:', error);
        res.status(500).json({ error: error.message });
      }
    });

    // 問題カテゴライズ
    this.app.post('/api/questions/categorize', (req, res) => {
      try {
        const { questions } = req.body;
        if (!Array.isArray(questions)) {
          return res.status(400).json({ error: 'questions must be an array' });
        }

        const categorized = this.categorizer.categorizeQuestions(questions);
        res.json({
          total: categorized.length,
          questions: categorized
        });
      } catch (error) {
        console.error('❌ Categorization error:', error);
        res.status(500).json({ error: error.message });
      }
    });

    // 学習進捗分析
    this.app.post('/api/progress/analyze', (req, res) => {
      try {
        const { answeredQuestions, targetAccuracy = 80 } = req.body;
        if (!Array.isArray(answeredQuestions)) {
          return res.status(400).json({ error: 'answeredQuestions must be an array' });
        }

        const stats = this.categorizer.analyzeProgress(answeredQuestions);
        const suggestions = this.categorizer.suggestLearningTopics(answeredQuestions, targetAccuracy);

        res.json({
          statistics: stats,
          weakPoints: suggestions,
          overallAccuracy: this._calculateOverallAccuracy(stats)
        });
      } catch (error) {
        console.error('❌ Analysis error:', error);
        res.status(500).json({ error: error.message });
      }
    });

    // 試験セット生成（新規50問 or 更新30問）
    this.app.post('/api/exam/generate', async (req, res) => {
      try {
        if (!this.questionGenerator) {
          return res.status(400).json({
            error: 'Question generator not initialized. Call /api/rag/init first'
          });
        }

        const { examType = 'new' } = req.body;

        if (!['new', 'renewal'].includes(examType)) {
          return res.status(400).json({
            error: 'examType must be "new" or "renewal"'
          });
        }

        console.log(`📝 Generating ${examType} exam...`);
        const examSet = await this.questionGenerator.generateExamSet(examType);

        res.json({
          success: true,
          exam: examSet
        });
      } catch (error) {
        console.error('❌ Exam generation error:', error);
        res.status(500).json({
          error: error.message
        });
      }
    });

    // 正誤択一式問題生成（単一問題）
    this.app.post('/api/questions/generate-true-false', async (req, res) => {
      try {
        if (!this.questionGenerator) {
          return res.status(400).json({
            error: 'Question generator not initialized. Call /api/rag/init first'
          });
        }

        const { topic, pattern = 1 } = req.body;

        if (!topic) {
          return res.status(400).json({
            error: 'topic parameter required'
          });
        }

        if (pattern < 1 || pattern > 6) {
          return res.status(400).json({
            error: 'pattern must be 1-6'
          });
        }

        // RAGからコンテキスト取得
        const ragResults = await this.rag.search(topic, 1);
        if (ragResults.length === 0) {
          return res.status(400).json({
            error: 'No relevant context found'
          });
        }

        // 問題生成
        const question = await this.questionGenerator.generateTrueOrFalseQuestion(
          topic,
          ragResults[0],
          pattern
        );

        if (question.error) {
          return res.status(500).json({
            error: question.error
          });
        }

        res.json({
          success: true,
          question: question
        });
      } catch (error) {
        console.error('❌ Question generation error:', error);
        res.status(500).json({
          error: error.message
        });
      }
    });

    // ワーカー2仕様版: 詳細問題生成（6ステップフロー）
    this.app.post('/api/questions/generate-advanced', async (req, res) => {
      try {
        if (!this.completePipeline) {
          return res.status(400).json({
            error: 'Pipeline not initialized. Call /api/rag/init first'
          });
        }

        const { topic, pattern = 1, difficulty = 'medium' } = req.body;

        if (!topic) {
          return res.status(400).json({
            error: 'topic parameter required'
          });
        }

        if (pattern < 1 || pattern > 6) {
          return res.status(400).json({
            error: 'pattern must be 1-6'
          });
        }

        // RAGからコンテキスト取得
        const ragResults = await this.rag.search(topic, 1);
        if (ragResults.length === 0) {
          return res.status(400).json({
            error: 'No relevant context found'
          });
        }

        // ワーカー2仕様版の完全フロー実行
        console.log(`📝 Advanced generation: Pattern ${pattern}, Difficulty: ${difficulty}`);
        const result = await this.completePipeline.executeCompleteFlow(
          ragResults[0],
          pattern,
          difficulty
        );

        if (!result.success) {
          return res.status(500).json({
            error: result.error || 'Generation failed'
          });
        }

        res.json({
          success: true,
          question: result.problem,
          analysis: {
            main_rule: result.analysis.main_rule,
            exception_clauses: result.analysis.exception_clauses,
            key_terms: result.analysis.key_terms.map(t => ({ term: t.term, category: t.category })),
            related_articles: result.analysis.related_articles
          },
          validation: result.validation
        });
      } catch (error) {
        console.error('❌ Advanced generation error:', error);
        res.status(500).json({
          error: error.message
        });
      }
    });

    // 試験仕様取得（UI表示用）
    this.app.get('/api/exam/specs', (req, res) => {
      res.json({
        new: {
          type: '遊技機取扱主任者試験（新規）',
          total_questions: 50,
          time_limit_minutes: 60,
          passing_score: 40,
          passing_rate_percent: 80,
          format: '正誤択一式（〇×式）',
          implementation_authority: '日本遊技関連事業協会（日遊協）',
          reference_url: 'https://exam.nichiyukyo.or.jp/'
        },
        renewal: {
          type: '遊技機取扱主任者試験（更新）',
          total_questions: 30,
          time_limit_minutes: 40,
          passing_score: 24,
          passing_rate_percent: 80,
          format: '正誤択一式（〇×式）',
          implementation_authority: '日本遊技関連事業協会（日遊協）',
          reference_url: 'https://exam.nichiyukyo.or.jp/'
        }
      });
    });

    // RAG統計情報
    this.app.get('/api/rag/stats', async (req, res) => {
      try {
        if (!this.rag) {
          return res.status(400).json({ error: 'RAG not initialized' });
        }

        const stats = await this.rag.getStats();
        res.json(stats);
      } catch (error) {
        console.error('❌ Stats error:', error);
        res.status(500).json({ error: error.message });
      }
    });
  }

  /**
   * 全体精度計算
   */
  _calculateOverallAccuracy(stats) {
    let totalCorrect = 0;
    let totalQuestions = 0;

    for (const category of Object.values(stats)) {
      totalCorrect += category.correct || 0;
      totalQuestions += category.total || 0;
    }

    return totalQuestions > 0 ? (totalCorrect / totalQuestions * 100).toFixed(1) : 0;
  }

  /**
   * サーバー起動
   */
  start(port = 3000) {
    this.app.listen(port, () => {
      console.log(`\n✅ RAG API Server running on http://localhost:${port}`);
      console.log(`📝 Documentation:\n`);
      console.log(`  POST   /api/rag/init              - Initialize RAG system`);
      console.log(`  POST   /api/questions/generate    - Generate questions`);
      console.log(`  GET    /api/questions/search      - Search related text`);
      console.log(`  POST   /api/questions/categorize  - Categorize questions`);
      console.log(`  POST   /api/progress/analyze      - Analyze learning progress`);
      console.log(`  GET    /api/rag/stats             - Get RAG statistics`);
      console.log(`  GET    /api/config/providers      - List available LLM providers`);
      console.log(`  GET    /api/health                - Health check\n`);
    });
  }
}

export { RAGServer };

// 直接実行時
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new RAGServer();
  const port = process.env.PORT || 3000;
  server.start(port);
}
