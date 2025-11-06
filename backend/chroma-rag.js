/**
 * ChromaRAG - Chroma統合のRAGシステム初期化
 *
 * 役割:
 * - ベクトルDB初期化
 * - チャンク埋め込み
 * - 検索インデックス構築
 */

import { ChromaClient } from 'chromadb';
import { TextChunker } from './text-chunker.js';
import { LLMProviderFactory } from './llm-provider.js';
import fs from 'fs';
import path from 'path';

class ChromaRAG {
  constructor(config = {}) {
    this.chromaPath = config.chromaPath || '/tmp/chroma_db';
    this.collectionName = config.collectionName || 'patshinko-exam';
    this.embeddingModel = config.embeddingModel || 'default'; // Chromaが自動的に処理
    this.client = null;
    this.collection = null;
  }

  /**
   * Chromaクライアント初期化
   */
  async initialize() {
    try {
      console.log('🔄 Initializing Chroma client...');

      // Chromaクライアント作成（新バージョン対応: HTTP + ローカルサーバー起動）
      // または代替: メモリモード（テスト用）
      try {
        // 新バージョン用: HTTPクライアント（推奨）
        this.client = new ChromaClient({
          host: 'localhost',
          port: 8000
        });
        console.log('📡 Using HTTP client mode (localhost:8000)');
      } catch (httpError) {
        console.log('⚠️  HTTP mode failed, attempting direct mode...');
        // フォールバック: 直接初期化試行
        this.client = new ChromaClient();
      }

      // コレクション取得または作成
      this.collection = await this.client.getOrCreateCollection({
        name: this.collectionName,
        metadata: {
          description: 'パチンコ遊技機取扱主任者講習 - OCR補正テキスト + 風営法',
          createdAt: new Date().toISOString()
        }
      });

      console.log(`✅ Chroma initialized. Collection: ${this.collectionName}`);
      return this;
    } catch (error) {
      console.error('❌ Error initializing Chroma:', error);
      throw error;
    }
  }

  /**
   * チャンクをコレクションに追加
   * @param {Array} chunks - [{id, text, section, source, ...}]
   */
  async addChunks(chunks) {
    try {
      console.log(`🔄 Adding ${chunks.length} chunks to Chroma...`);

      // Chromaは自動的に埋め込み処理を行う
      const ids = chunks.map(c => c.id);
      const texts = chunks.map(c => c.text);
      const metadatas = chunks.map(c => ({
        page: c.page,
        section: c.section,
        source: c.source,
        sourceFile: c.sourceFile,
        timestamp: c.timestamp
      }));

      await this.collection.add({
        ids: ids,
        documents: texts,
        metadatas: metadatas
      });

      console.log(`✅ Added ${chunks.length} chunks to Chroma`);
    } catch (error) {
      console.error('❌ Error adding chunks to Chroma:', error);
      throw error;
    }
  }

  /**
   * セマンティック検索
   * @param {string} query
   * @param {number} limit
   * @returns {Array}
   */
  async search(query, limit = 5) {
    try {
      const results = await this.collection.query({
        queryTexts: [query],
        nResults: limit
      });

      // 結果をフォーマット
      const formattedResults = [];
      if (results && results.documents && results.documents[0]) {
        for (let i = 0; i < results.documents[0].length; i++) {
          formattedResults.push({
            id: results.ids[0][i],
            text: results.documents[0][i],
            metadata: results.metadatas[0][i],
            distance: results.distances[0][i] // コサイン距離（0に近いほど類似）
          });
        }
      }

      return formattedResults;
    } catch (error) {
      console.error('❌ Error searching Chroma:', error);
      throw error;
    }
  }

  /**
   * コンテキスト生成（複数検索結果から）
   * @param {string} query
   * @param {number} contextCount
   * @returns {string}
   */
  async generateContext(query, contextCount = 5) {
    const results = await this.search(query, contextCount);

    if (results.length === 0) {
      return 'No relevant information found.';
    }

    const context = results
      .map(r => `[${r.metadata.section}]\n${r.text}`)
      .join('\n\n---\n\n');

    return context;
  }

  /**
   * 統計情報を取得
   */
  async getStats() {
    try {
      const count = await this.collection.count();
      return {
        collectionName: this.collectionName,
        documentCount: count,
        status: 'active'
      };
    } catch (error) {
      console.error('❌ Error getting stats:', error);
      return { error: error.message };
    }
  }

  /**
   * コレクションをクリア
   */
  async clear() {
    try {
      await this.client.deleteCollection({ name: this.collectionName });
      console.log(`✅ Collection ${this.collectionName} cleared`);
    } catch (error) {
      console.error('❌ Error clearing collection:', error);
    }
  }
}

/**
 * RAG初期化実行スクリプト
 */
export class RAGInitializer {
  static async initialize(config = {}) {
    try {
      console.log('\n🚀 RAG System Initialization\n');

      // パス設定
      const ocrPath = config.ocrPath || '/home/planj/patshinko-exam-app/data/ocr_results_corrected.json';
      const windPath = config.windPath || '/home/planj/Claude-Code-Communication/resources/legal/wind_eikyo_law/wind_eikyo_law_v1.0.md';
      const outputPath = config.outputPath || '/tmp/rag_chunks.json';

      // 1. テキストチャンキング
      console.log('📝 Step 1: Text Chunking');
      const chunker = new TextChunker({
        chunkSize: 800,
        overlapSize: 100
      });

      const chunks = await chunker.chunkMultipleSources({
        ocr: ocrPath,
        markdown: [windPath]
      });

      chunker.saveChunks(
        [...chunks.ocrChunks, ...chunks.mdChunks],
        outputPath
      );

      // 2. Chroma初期化
      console.log('\n🗄️  Step 2: Chroma Initialization');
      const rag = new ChromaRAG({
        chromaPath: config.chromaPath || '/tmp/chroma_db',
        collectionName: 'patshinko-exam'
      });

      await rag.initialize();

      // 3. チャンク追加
      console.log('\n📚 Step 3: Adding Chunks to Vector DB');
      await rag.addChunks([...chunks.ocrChunks, ...chunks.mdChunks]);

      // 4. 統計情報
      console.log('\n📊 Step 4: Statistics');
      const stats = await rag.getStats();
      console.log(`Total documents in vector DB: ${stats.documentCount}`);

      // 5. 動作確認（テスト検索）
      console.log('\n🧪 Step 5: Testing Search');
      const testQuery = '遊技機の定義は？';
      const searchResults = await rag.search(testQuery, 3);
      console.log(`\nTest Query: "${testQuery}"`);
      console.log(`Results: ${searchResults.length} matches`);
      searchResults.forEach((r, i) => {
        console.log(`  ${i + 1}. [${r.metadata.section}] ${r.text.substring(0, 50)}...`);
      });

      console.log('\n✅ RAG System Initialized Successfully!\n');
      return { rag, chunks, stats };
    } catch (error) {
      console.error('❌ RAG Initialization failed:', error);
      throw error;
    }
  }
}

export { ChromaRAG };
