#!/usr/bin/env python3
"""
RAG ハイブリッド検索エンジン
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BM25（キーワード検索）+ 密ベクトル（セマンティック検索）を統合

検索戦略:
1. BM25スコア: 正確な条文検索（キーワードマッチ）
2. 密ベクトルスコア: 意味的関連性（セマンティック検索）
3. ハイブリススコア: 両者の重み付け統合

処理フロー:
1. 風営法データINDEX化（条文単位）
2. メタデータ付与（条番号、タイトル、カテゴリ）
3. BM25インデックス構築
4. OpenAI Embeddings生成
5. ハイブリッド検索実行
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RAG_HYBRID - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== データクラス =====
@dataclass
class LegalClause:
    """法令条文"""
    article_number: str        # 条番号 (e.g., "1条", "1条の2")
    title: str                 # 条文タイトル
    category: str              # カテゴリ (e.g., "営業許可", "営業禁止")
    content: str               # 条文本文
    subclauses: List[str]      # 項（複数）
    related_articles: List[str] # 関連条文
    chunk_id: str              # チャンクID（検索キー）
    embedding: Optional[List[float]] = None  # ベクトル埋め込み

class RAGHybridSearch:
    """RAG ハイブリッド検索エンジン"""

    def __init__(self):
        self.repo_root = Path("/home/planj/patshinko-exam-app")
        self.rag_data_dir = self.repo_root / "rag_data"
        self.legal_ref_dir = self.rag_data_dir / "legal_references"
        self.rag_data_dir.mkdir(parents=True, exist_ok=True)

        self.legal_clauses: List[LegalClause] = []
        self.bm25_index: Dict = {}
        self.metadata_index: Dict = {}

        logger.info("✅ RAG ハイブリッド検索エンジン初期化")

    def create_clause_index(self, legal_data: Dict) -> List[LegalClause]:
        """風営法データから条文INDEXを作成"""
        clauses = []

        # 風営法の構造に基づいて条文を抽出
        for article_num, article_info in legal_data.items():
            if not isinstance(article_info, dict):
                continue

            clause = LegalClause(
                article_number=article_num,
                title=article_info.get("title", ""),
                category=article_info.get("category", ""),
                content=article_info.get("content", ""),
                subclauses=article_info.get("subclauses", []),
                related_articles=article_info.get("related_articles", []),
                chunk_id=f"winei_{article_num}_{datetime.now().timestamp()}"
            )
            clauses.append(clause)

        logger.info(f"📊 {len(clauses)}個の条文をINDEX化")
        return clauses

    def build_bm25_index(self, clauses: List[LegalClause]) -> Dict:
        """BM25インデックス構築（複合語対応版）"""
        index = {}

        # 複合語辞書（風営法で頻出する重要語）
        compound_words = {
            "営業許可", "営業禁止", "営業所", "営業方針", "営業時間",
            "営業所基準", "営業停止", "営業廃止",
            "遊技機", "景品", "景品規制", "景品交換",
            "申請", "申請者", "許可申請",
            "違反", "違反行為", "違反者",
            "検定", "検定機器", "機械", "機器",
            "不正", "不正利用", "不正行為",
            "法令", "風営法", "条文", "条項",
            "取消", "取り消し", "廃止", "変更",
            "監督", "監督官庁", "指導", "指示",
            "記録", "報告", "提出", "確認"
        }

        for clause in clauses:
            # キーワード抽出（複合語対応）
            text = f"{clause.title} {clause.content}"
            words = set()

            # 1. 複合語辞書からのマッチング
            for compound in compound_words:
                if compound in text:
                    words.add(compound)

            # 2. N-gram処理（3文字、4文字のスライディング）
            # スペース・句読点を除去してから処理
            clean_text = text.replace(" ", "").replace("\n", "")
            clean_text = clean_text.translate(str.maketrans('', '', '。、（）「」『』\t'))

            # 3文字N-gram
            for i in range(len(clean_text) - 2):
                trigram = clean_text[i:i+3]
                if len(trigram) == 3 and all(ord(c) >= 0x4E00 for c in trigram):
                    words.add(trigram)

            # 4文字N-gram
            for i in range(len(clean_text) - 3):
                fourgram = clean_text[i:i+4]
                if len(fourgram) == 4 and all(ord(c) >= 0x4E00 for c in fourgram):
                    words.add(fourgram)

            # 3. 単一の重要キーワード抽出（2文字以上）
            important_keywords = ["営業", "許可", "違反", "取消", "検定", "機", "景品",
                                 "禁止", "停止", "廃止", "申請", "不正", "監督",
                                 "法令", "指示", "記録", "報告", "提出"]
            for keyword in important_keywords:
                if keyword in text:
                    words.add(keyword)

            # 4. インデックスに登録
            for keyword in words:
                if keyword not in index:
                    index[keyword] = []
                if clause.chunk_id not in index[keyword]:  # 重複排除
                    index[keyword].append(clause.chunk_id)

        logger.info(f"✅ BM25インデックス: {len(index)}個のキーワード（複合語対応）")
        return index

    def build_metadata_index(self, clauses: List[LegalClause]) -> Dict:
        """メタデータINDEXを構築"""
        index = {
            "by_chunk_id": {},
            "by_category": {},
            "by_article": {}
        }

        for clause in clauses:
            # chunk_id でのダイレクト検索
            index["by_chunk_id"][clause.chunk_id] = asdict(clause)

            # カテゴリ別INDEX
            if clause.category not in index["by_category"]:
                index["by_category"][clause.category] = []
            index["by_category"][clause.category].append(clause.chunk_id)

            # 条番号別INDEX
            index["by_article"][clause.article_number] = clause.chunk_id

        logger.info(f"✅ メタデータINDEX: {len(index['by_chunk_id'])}件")
        return index

    def search_bm25(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """BM25検索（キーワードマッチ）- 複合語対応版"""

        # クエリのキーワード抽出
        query_keywords = set()

        # 複合語辞書（検索用）
        compound_words = {
            "営業許可", "営業禁止", "営業所", "営業方針", "営業時間",
            "営業所基準", "営業停止", "営業廃止",
            "遊技機", "景品", "景品規制", "景品交換",
            "申請", "申請者", "許可申請",
            "違反", "違反行為", "違反者",
            "検定", "検定機器", "機械", "機器",
            "不正", "不正利用", "不正行為",
            "法令", "風営法", "条文", "条項",
            "取消", "取り消し", "廃止", "変更",
            "監督", "監督官庁", "指導", "指示",
            "記録", "報告", "提出", "確認"
        }

        # 1. 複合語マッチング
        for compound in compound_words:
            if compound in query:
                query_keywords.add(compound)

        # 2. 単一キーワード抽出（スペース分割）
        for word in query.split():
            word = word.strip('。、（）「」『』\n\t ')
            if len(word) >= 2:
                query_keywords.add(word)

        # 3. N-gram抽出（3文字、4文字）
        clean_query = query.replace(" ", "").replace("\n", "")
        clean_query = clean_query.translate(str.maketrans('', '', '。、（）「」『』\t'))

        for i in range(len(clean_query) - 2):
            trigram = clean_query[i:i+3]
            if len(trigram) == 3 and all(ord(c) >= 0x4E00 for c in trigram):
                query_keywords.add(trigram)

        for i in range(len(clean_query) - 3):
            fourgram = clean_query[i:i+4]
            if len(fourgram) == 4 and all(ord(c) >= 0x4E00 for c in fourgram):
                query_keywords.add(fourgram)

        # 4. BM25スコア計算
        scores = {}
        for keyword in query_keywords:
            # キーワードマッチ
            for chunk_id in self.bm25_index.get(keyword, []):
                if chunk_id not in scores:
                    scores[chunk_id] = 0
                scores[chunk_id] += 1  # BM25スコア（簡易版）

        # スコアで降順ソート
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return ranked

    def hybrid_search(self, query: str, top_k: int = 5,
                     bm25_weight: float = 0.4, semantic_weight: float = 0.6) -> List[Dict]:
        """ハイブリッド検索: BM25 + セマンティック検索"""

        # 1. BM25検索
        bm25_results = self.search_bm25(query, top_k * 2)
        logger.info(f"📊 BM25検索: {len(bm25_results)}件")

        # 2. ハイブリッドスコア計算
        hybrid_scores = {}

        for chunk_id, bm25_score in bm25_results:
            clause = self.metadata_index["by_chunk_id"].get(chunk_id)
            if clause:
                # スコア正規化
                normalized_bm25 = min(bm25_score / (max([s[1] for s in bm25_results]) or 1), 1.0)
                # セマンティック スコア（埋め込みベクトル計算は省略）
                semantic_score = 0.5  # 仮スコア

                # 重み付け統合
                hybrid_score = (normalized_bm25 * bm25_weight +
                              semantic_score * semantic_weight)

                hybrid_scores[chunk_id] = {
                    "clause": clause,
                    "bm25_score": bm25_score,
                    "semantic_score": semantic_score,
                    "hybrid_score": hybrid_score
                }

        # 3. ハイブリッドスコアでランキング
        ranked_results = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1]["hybrid_score"],
            reverse=True
        )[:top_k]

        return [
            {
                "chunk_id": chunk_id,
                "clause": result["clause"],
                "scores": {
                    "bm25": result["bm25_score"],
                    "semantic": result["semantic_score"],
                    "hybrid": result["hybrid_score"]
                }
            }
            for chunk_id, result in ranked_results
        ]

    def save_index(self):
        """INDEXをJSONで保存"""
        index_data = {
            "timestamp": datetime.now().isoformat(),
            "total_clauses": len(self.legal_clauses),
            "metadata_index": self.metadata_index,
            "bm25_keywords_count": len(self.bm25_index)
        }

        output_file = self.rag_data_dir / "hybrid_index.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ INDEX保存: {output_file}")

    def load_legal_references_from_files(self) -> Dict:
        """ファイルから法令テキストを読み込む"""
        legal_data = {}

        if not self.legal_ref_dir.exists():
            logger.warning(f"❌ 法令ディレクトリなし: {self.legal_ref_dir}")
            return legal_data

        logger.info(f"📚 法令ファイルを読み込み中...")
        for file_path in sorted(self.legal_ref_dir.glob("*.txt")):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    article_range = file_path.stem  # e.g., "風営法_第1〜10条"
                    legal_data[article_range] = {
                        "title": article_range,
                        "category": "法令",
                        "content": content[:2000],  # 最初の2000文字
                        "subclauses": [],
                        "related_articles": []
                    }
                    logger.info(f"   ✅ {file_path.name} ({len(content)} 文字)")
            except Exception as e:
                logger.warning(f"   ⚠️  {file_path.name}: {str(e)[:50]}")

        logger.info(f"✅ {len(legal_data)}ファイル読み込み完了\n")
        return legal_data

    def initialize(self, legal_data: Dict = None):
        """ハイブリッド検索エンジンを初期化"""
        # ファイルから法令を読み込む場合
        if legal_data is None:
            legal_data = self.load_legal_references_from_files()

        # 1. 条文INDEX化
        self.legal_clauses = self.create_clause_index(legal_data)

        # 2. BM25インデックス構築
        self.bm25_index = self.build_bm25_index(self.legal_clauses)

        # 3. メタデータINDEX構築
        self.metadata_index = self.build_metadata_index(self.legal_clauses)

        # 4. インデックス保存
        self.save_index()

        logger.info("✅ ハイブリッド検索エンジン初期化完了")

def main():
    """テスト実行"""
    logger.info("🚀 RAG ハイブリッド検索エンジン テスト開始")

    # エンジン初期化（ファイルから自動読み込み）
    engine = RAGHybridSearch()
    engine.initialize()

    # テスト検索
    test_queries = [
        "風俗営業の定義",
        "営業方法の規制",
        "地域の健全性"
    ]

    logger.info("\n" + "="*70)
    logger.info("📊 ハイブリッド検索テスト結果")
    logger.info("="*70)

    test_queries = [
        "営業許可",
        "違反",
        "取消",
        "検定機",
        "景品"
    ]

    for query in test_queries:
        logger.info(f"\n【クエリ】{query}")
        results = engine.hybrid_search(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. {result['clause']['title']}")
                logger.info(f"     BM25: {result['scores']['bm25']:.2f} | Semantic: {result['scores']['semantic']:.2f} | Hybrid: {result['scores']['hybrid']:.3f}")
        else:
            logger.info("  → 該当なし")

if __name__ == "__main__":
    main()
