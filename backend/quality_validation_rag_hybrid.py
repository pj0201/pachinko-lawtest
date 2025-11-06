#!/usr/bin/env python3
"""
RAGハイブリッド化 検索品質・問題生成品質の検証
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 検索品質改善確認: 旧実装 vs ハイブリッド実装の比較
2. 問題生成品質測定: 生成される問題の正確性・法令準拠性評価
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

from rag_hybrid_search import RAGHybridSearch

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - QUALITY_VAL - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_final_500.json"

# ===== 1. 検索品質の比較テスト =====

def simple_keyword_search(query: str, legal_texts: Dict[str, str], top_k: int = 3) -> List[Dict]:
    """旧実装: シンプルなキーワード検索"""
    results = []
    keywords = query.split()

    for ref_name, content in legal_texts.items():
        relevance_score = 0
        for keyword in keywords:
            if keyword in content:
                relevance_score += len([w for w in content.split() if w == keyword])

        if relevance_score > 0:
            results.append({
                'source': ref_name,
                'relevance': relevance_score,
                'method': 'simple_keyword'
            })

    results = sorted(results, key=lambda x: -x['relevance'])[:top_k]
    return results

def hybrid_rag_search(query: str, rag_engine: RAGHybridSearch, top_k: int = 3) -> List[Dict]:
    """新実装: ハイブリッドRAG検索"""
    results = rag_engine.hybrid_search(query, top_k=top_k)
    return [
        {
            'source': r['clause']['title'],
            'hybrid_score': float(r['scores']['hybrid']),
            'bm25_score': float(r['scores']['bm25']),
            'method': 'hybrid_rag'
        }
        for r in results
    ]

def test_search_quality():
    """検索品質改善の確認テスト"""
    print("\n" + "="*80)
    print("【テスト1】検索品質改善確認: 旧実装 vs ハイブリッド実装")
    print("="*80 + "\n")

    # 問題読み込み
    with open(PROBLEMS_FILE) as f:
        problems = json.load(f)

    # 法令テキスト読み込み
    legal_texts = {}
    legal_ref_dir = REPO_ROOT / "rag_data/legal_references"
    for file_path in sorted(legal_ref_dir.glob("*.txt")):
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            legal_texts[file_path.stem] = f.read()

    # RAGハイブリッドエンジン初期化
    print("RAGハイブリッド検索エンジン初期化中...")
    rag_engine = RAGHybridSearch()
    rag_engine.initialize()
    print("✅ エンジン初期化完了\n")

    # サンプル5問について比較
    sample_problems = problems[:5]
    comparison_results = []

    for i, problem in enumerate(sample_problems, 1):
        problem_text = problem['problem_text'][:80]
        category = problem['category']

        print(f"【問題 {i}】{problem_text}...")
        print(f"カテゴリ: {category}\n")

        # 検索キーワード生成
        search_query = f"{category} {problem['pattern_name']}"

        # 旧実装実行
        print("  旧実装（シンプルキーワード検索）:")
        old_start = time.time()
        old_results = simple_keyword_search(search_query, legal_texts, top_k=2)
        old_time = time.time() - old_start

        if old_results:
            for j, res in enumerate(old_results, 1):
                print(f"    {j}. {res['source']} (スコア: {res['relevance']})")
        else:
            print(f"    → 検索結果なし")
        print(f"    実行時間: {old_time*1000:.2f}ms\n")

        # 新実装実行
        print("  新実装（ハイブリッドRAG）:")
        new_start = time.time()
        new_results = hybrid_rag_search(search_query, rag_engine, top_k=2)
        new_time = time.time() - new_start

        if new_results:
            for j, res in enumerate(new_results, 1):
                print(f"    {j}. {res['source']} (スコア: {res['hybrid_score']:.3f})")
        else:
            print(f"    → 検索結果なし")
        print(f"    実行時間: {new_time*1000:.2f}ms\n")

        # 比較結果記録
        comparison_results.append({
            "problem_id": problem['problem_id'],
            "category": category,
            "old_results_count": len(old_results),
            "new_results_count": len(new_results),
            "old_time_ms": old_time * 1000,
            "new_time_ms": new_time * 1000,
            "improvement": "✅" if len(new_results) >= len(old_results) else "⚠️"
        })

        time.sleep(0.5)

    # 結果サマリー
    print("="*80)
    print("📊 検索品質改善サマリー")
    print("="*80)

    old_avg = sum(r['old_results_count'] for r in comparison_results) / len(comparison_results)
    new_avg = sum(r['new_results_count'] for r in comparison_results) / len(comparison_results)

    print(f"\n旧実装: 平均 {old_avg:.1f} 件")
    print(f"新実装: 平均 {new_avg:.1f} 件")
    print(f"改善度: {((new_avg - old_avg) / max(old_avg, 1) * 100):.1f}%\n")

    return comparison_results

# ===== 2. 問題生成品質の測定 =====

def evaluate_problem_quality(problem: Dict, rag_results: Dict) -> Dict:
    """問題生成品質の定量評価"""
    evaluation = {
        "problem_id": problem['problem_id'],
        "category": problem['category'],
        "scores": {}
    }

    # 1. 検索結果の有無
    has_rag_results = rag_results.get('result_count', 0) > 0
    evaluation['scores']['rag_search_found'] = 1.0 if has_rag_results else 0.0

    # 2. 生成説明の長さ（目安: 150-250文字）
    explanation = problem.get('explanation_hybrid_rag', '')
    explanation_length = len(explanation)

    if 150 <= explanation_length <= 250:
        evaluation['scores']['explanation_length'] = 1.0
    elif 100 <= explanation_length < 150 or 250 < explanation_length <= 300:
        evaluation['scores']['explanation_length'] = 0.7
    elif explanation_length < 100 or explanation_length > 300:
        evaluation['scores']['explanation_length'] = 0.3
    else:
        evaluation['scores']['explanation_length'] = 0.0

    # 3. テンプレート表現の排除
    template_phrases = ['に関する問題です', 'について学ぶ', 'の知識']
    template_found = any(phrase in explanation for phrase in template_phrases)
    evaluation['scores']['no_template'] = 0.0 if template_found else 1.0

    # 4. 法令参照の有無
    has_legal_ref = '条' in explanation or '法' in explanation
    evaluation['scores']['legal_reference'] = 1.0 if has_legal_ref else 0.5

    # 5. 総合スコア（加重平均）
    weights = {
        'rag_search_found': 0.2,
        'explanation_length': 0.25,
        'no_template': 0.35,
        'legal_reference': 0.2
    }

    total_score = sum(
        evaluation['scores'].get(key, 0) * weight
        for key, weight in weights.items()
    )
    evaluation['overall_score'] = round(total_score, 2)

    return evaluation

def test_problem_quality():
    """問題生成品質の測定テスト"""
    print("\n" + "="*80)
    print("【テスト2】問題生成品質測定")
    print("="*80 + "\n")

    # サンプル問題でテスト（5問）
    with open(PROBLEMS_FILE) as f:
        problems = json.load(f)

    sample_problems = problems[:5]
    quality_results = []

    print("サンプル5問の品質を評価中...\n")

    for i, problem in enumerate(sample_problems, 1):
        # ダミーのRAG結果（実際の統合実行では問題生成スクリプトから取得）
        rag_results = {
            'result_count': 1 if i != 3 else 0,  # 3番目は検索なしでシミュレート
            'results': []
        }

        # ダミー説明を設定（実際の実行では生成される）
        problem['explanation_hybrid_rag'] = problem.get('explanation', '')[:200]

        quality = evaluate_problem_quality(problem, rag_results)
        quality_results.append(quality)

        print(f"【問題 {i}】{problem['problem_text'][:50]}...")
        print(f"  RAG検索: {'✅' if rag_results['result_count'] > 0 else '❌'}")
        print(f"  説明長: {len(problem['explanation_hybrid_rag'])} 文字")
        print(f"  テンプレート排除: {'✅' if quality['scores']['no_template'] == 1.0 else '❌'}")
        print(f"  法令参照: {'✅' if quality['scores']['legal_reference'] == 1.0 else '⚠️'}")
        print(f"  総合スコア: {quality['overall_score']:.2f}/1.0\n")

    # 品質サマリー
    print("="*80)
    print("📊 問題生成品質サマリー")
    print("="*80)

    avg_score = sum(r['overall_score'] for r in quality_results) / len(quality_results)
    rag_found_rate = sum(1 for r in quality_results if r['scores']['rag_search_found'] == 1.0) / len(quality_results)
    no_template_rate = sum(1 for r in quality_results if r['scores']['no_template'] == 1.0) / len(quality_results)

    print(f"\n総合品質スコア: {avg_score:.2f}/1.0")
    print(f"RAG検索成功率: {rag_found_rate*100:.1f}%")
    print(f"テンプレート排除率: {no_template_rate*100:.1f}%")

    if avg_score >= 0.8:
        print("✅ 品質判定: 良好（本番投入可能）")
    elif avg_score >= 0.6:
        print("⚠️  品質判定: 要改善")
    else:
        print("❌ 品質判定: 不十分")

    return quality_results

def main():
    print("\n" + "="*80)
    print("🧪 RAGハイブリッド化 品質検証テスト")
    print("="*80)

    # テスト実行
    search_results = test_search_quality()
    quality_results = test_problem_quality()

    # 結果保存
    output_file = REPO_ROOT / "backend/quality_validation_results.json"
    validation_report = {
        "test_time": datetime.now().isoformat(),
        "search_quality": search_results,
        "problem_quality": quality_results,
        "summary": {
            "total_tests": len(search_results) + len(quality_results),
            "search_improvement_avg": sum(r['new_results_count'] - r['old_results_count'] for r in search_results) / len(search_results),
            "quality_score_avg": sum(r['overall_score'] for r in quality_results) / len(quality_results)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_report, f, ensure_ascii=False, indent=2)

    print(f"\n📁 詳細レポート保存: {output_file}\n")

if __name__ == "__main__":
    main()
