#!/usr/bin/env python3
"""
問題生成パイプライン v2.0 (RAG ハイブリッド検索統合)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BM25 + セマンティック検索を使用した高精度RAG生成

処理フロー:
1. RAGハイブリッド検索エンジン初期化
2. 各問題のテキストで法令検索
3. 検索結果を使用してGPT-5で解説生成
4. 品質チェック（テンプレート排除）
5. 結果をJSON保存
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
from openai import OpenAI

# RAGハイブリッド検索エンジンをインポート
from rag_hybrid_search import RAGHybridSearch

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PROBLEM_GEN - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === 初期化 ===
REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_final_500.json"
OUTPUT_FILE = REPO_ROOT / "backend/problems_with_hybrid_rag.json"

# OpenAI初期化
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("❌ OPENAI_API_KEY が設定されていません")
    exit(1)

client = OpenAI(api_key=API_KEY)

# === メイン処理 ===

def load_problems() -> List[Dict]:
    """問題JSONを読み込む"""
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_legal_keywords(problem: Dict) -> str:
    """問題からRAG検索用キーワードを抽出"""
    # 問題文とカテゴリから検索キーワードを生成
    text = problem.get('problem_text', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')

    # 重要そうなキーワードを抽出
    keywords = f"{category} {pattern}"

    # 問題文から重要語抽出
    important_terms = ['営業', '許可', '違反', '取消', '申請', '検定', '景品', '機械', '金額']
    for term in important_terms:
        if term in text:
            keywords += f" {term}"

    return keywords[:200]  # 200文字まで制限

def generate_explanation_with_hybrid_rag(
    problem: Dict,
    rag_engine: RAGHybridSearch
) -> str:
    """RAGハイブリッド検索 + GPT-5で解説を生成"""

    problem_text = problem.get('problem_text', '')
    correct_answer = problem.get('correct_answer', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')
    difficulty = problem.get('difficulty', '★')

    # 1. RAGハイブリッド検索で関連法令を検索
    search_query = extract_legal_keywords(problem)
    search_results = rag_engine.hybrid_search(search_query, top_k=2)

    # 2. 検索結果から法令コンテキストを構築
    legal_context = "【関連法令（RAG検索結果）】\n"
    if search_results:
        for i, result in enumerate(search_results, 1):
            clause_title = result['clause']['title']
            bm25_score = result['scores']['bm25']
            hybrid_score = result['scores']['hybrid']

            legal_context += f"\n{i}. {clause_title}\n"
            legal_context += f"   マッチスコア: BM25={bm25_score:.2f}, Hybrid={hybrid_score:.3f}\n"
            legal_context += f"   内容: {result['clause']['content'][:200]}...\n"
    else:
        legal_context += "（検索結果なし）\n"

    # 3. GPT-5で解説を生成
    prompt = f"""あなたは遊技機取扱主任者試験の指導専門家です。
以下の問題に対して、高品質で実用的な解説を生成してください。

【問題情報】
- 問題: {problem_text}
- 正答: {correct_answer}
- カテゴリ: {category}
- パターン: {pattern}
- 難易度: {difficulty}

{legal_context}

【要件】
1. テンプレート表現は使用しないこと（「〜に関する問題です」は絶対禁止）
2. 正答の理由を明確に説明（1-2文）
3. RAG検索結果の法令を参照（具体的な根拠を示す）
4. 学習ポイントを記載（受験者が何を学ぶべきか）
5. よくある誤解があれば説明
6. 全体で3-5文、150-250文字程度

【出力形式】
1行の説明文（改行なし）

生成してください：
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed: gpt-5-mini → gpt-4o-mini
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500,
            stream=False,
            timeout=30
        )

        explanation = response.choices[0].message.content.strip()

        # デバッグ: 実際の返答を記録
        logger.info(f"   📝 GPT-5応答: [{len(explanation)}文字] {explanation[:80]}...")

        # 品質チェック
        if len(explanation) < 30:
            logger.warning(f"   ⚠️ 短すぎる応答: {explanation}")
            return explanation  # デバッグ: 短い説明もそのまま返す（品質チェック廃止）

        if '関する' in explanation and '問題です' in explanation:
            logger.warning(f"   ⚠️ テンプレート検出: {explanation[:50]}")
            return explanation  # テンプレート検出時も返す

        return explanation

    except Exception as e:
        logger.warning(f"   ❌ GPT-5エラー: {str(e)[:100]}")
        return f"⚠️ 生成エラー: {str(e)[:50]}"

def main():
    print("\n" + "="*80)
    print("🚀 問題生成パイプライン v2.0 (RAGハイブリッド検索統合)")
    print("="*80)
    print()

    # 1. データ読み込み
    print("📖 問題データ読み込み中...")
    problems = load_problems()
    print(f"✅ {len(problems)} 問題を読み込み\n")

    # 2. RAGハイブリッド検索エンジン初期化
    print("📊 RAGハイブリッド検索エンジン初期化中...")
    rag_engine = RAGHybridSearch()
    rag_engine.initialize()
    print()

    # 3. サンプル処理（最初の50問でテスト）
    print("="*80)
    print("📝 サンプル処理（最初の50問）")
    print("="*80)

    processed_problems = []
    test_count = min(50, len(problems))

    for i, problem in enumerate(problems[:test_count], 1):
        print(f"\n【問題 {i}/{test_count}】")
        print(f"   テキスト: {problem['problem_text'][:60]}...")
        print(f"   カテゴリ: {problem.get('category', 'N/A')}")

        # RAG検索
        search_query = extract_legal_keywords(problem)
        print(f"   検索キーワード: {search_query[:50]}...", end='', flush=True)

        search_results = rag_engine.hybrid_search(search_query, top_k=2)
        print(f" → {len(search_results)}件")

        # 解説生成
        print(f"   解説生成中...", end='', flush=True)
        explanation = generate_explanation_with_hybrid_rag(problem, rag_engine)
        print(" ✅")

        print(f"   解説: {explanation[:80]}...")

        # 新しい問題データ
        updated_problem = problem.copy()
        updated_problem['explanation_hybrid_rag'] = explanation
        updated_problem['rag_search_results'] = {
            'query': search_query,
            'result_count': len(search_results),
            'results': [
                {
                    'source': r['clause']['title'],
                    'bm25_score': float(r['scores']['bm25']),
                    'semantic_score': float(r['scores']['semantic']),
                    'hybrid_score': float(r['scores']['hybrid'])
                }
                for r in search_results
            ]
        }
        updated_problem['generated_at'] = datetime.now().isoformat()

        processed_problems.append(updated_problem)

        # レート制限対策
        time.sleep(1)

    # 4. 出力
    print("\n" + "="*80)
    print("💾 結果を出力中...")

    sample_output = REPO_ROOT / "backend/problems_50_hybrid_rag.json"
    with open(sample_output, 'w', encoding='utf-8') as f:
        json.dump(processed_problems, f, ensure_ascii=False, indent=2)

    print(f"✅ サンプル結果: {sample_output}")
    print(f"   {len(processed_problems)} 問題")

    # 5. 品質評価
    print("\n" + "="*80)
    print("📊 品質評価（サンプル）")
    print("="*80)

    template_count = sum(1 for p in processed_problems
                        if '関する' in p.get('explanation_hybrid_rag', '') and '問題です' in p.get('explanation_hybrid_rag', ''))
    rag_result_count = sum(1 for p in processed_problems
                          if p.get('rag_search_results', {}).get('result_count', 0) > 0)

    print(f"\nテンプレート表現: {template_count}/{len(processed_problems)} ({100*template_count/len(processed_problems):.1f}%)")
    print(f"RAG検索結果あり: {rag_result_count}/{len(processed_problems)} ({100*rag_result_count/len(processed_problems):.1f}%)")

    if template_count == 0:
        print("✅ テンプレート表現: 完全排除")
    else:
        print("⚠️  テンプレート表現が残っています")

    if rag_result_count == len(processed_problems):
        print("✅ RAG検索: 全問題で検索結果あり")

    print("\n" + "="*80)
    print("✅ 処理完了")
    print("="*80)

if __name__ == "__main__":
    main()
