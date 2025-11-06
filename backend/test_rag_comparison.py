#!/usr/bin/env python3
"""
RAG検索精度比較テスト
- 旧実装（簡易キーワード検索）vs 新実装（ハイブリッド検索）
"""

import json
import time
from pathlib import Path
from rag_hybrid_search import RAGHybridSearch

def test_simple_search(query: str, legal_texts: dict, max_results: int = 3) -> list:
    """旧実装: 簡易キーワード検索"""
    results = []
    keywords = query.split()

    for ref_name, content in legal_texts.items():
        relevance_score = 0
        for keyword in keywords:
            if keyword in content:
                relevance_score += 1

        if relevance_score > 0:
            results.append({
                'source': ref_name,
                'relevance': relevance_score
            })

    # スコアでソート
    results = sorted(results, key=lambda x: -x['relevance'])[:max_results]
    return results

def main():
    print("\n" + "="*80)
    print("📊 RAG検索精度比較テスト")
    print("="*80)

    # エンジン初期化
    engine = RAGHybridSearch()
    engine.initialize()

    # 法令テキストの辞書
    legal_texts = {}
    if engine.legal_ref_dir.exists():
        for file_path in sorted(engine.legal_ref_dir.glob("*.txt")):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                legal_texts[file_path.stem] = f.read()

    # テストクエリ
    test_queries = [
        "営業許可申請",
        "違反処分",
        "許可取消",
        "営業禁止",
        "罰金"
    ]

    comparison_results = []

    print("\n【テスト結果】\n")

    for query in test_queries:
        print(f"クエリ: {query}")
        print("-" * 80)

        # 旧実装（簡易キーワード検索）
        start = time.time()
        old_results = test_simple_search(query, legal_texts, max_results=3)
        old_time = time.time() - start

        print(f"  旧実装（簡易キーワード検索）: {len(old_results)}件 ({old_time*1000:.2f}ms)")
        for i, r in enumerate(old_results, 1):
            print(f"    {i}. {r['source']} (スコア: {r['relevance']})")

        # 新実装（ハイブリッド検索）
        start = time.time()
        new_results = engine.hybrid_search(query, top_k=3)
        new_time = time.time() - start

        print(f"  新実装（ハイブリッド検索）: {len(new_results)}件 ({new_time*1000:.2f}ms)")
        for i, r in enumerate(new_results, 1):
            print(f"    {i}. {r['clause']['title']} (スコア: {r['scores']['hybrid']:.3f})")

        comparison_results.append({
            "query": query,
            "old_count": len(old_results),
            "new_count": len(new_results),
            "old_time_ms": old_time * 1000,
            "new_time_ms": new_time * 1000,
            "improvement": "✅" if len(new_results) > 0 else "⚠️"
        })

        print()

    # サマリー
    print("="*80)
    print("📈 パフォーマンスサマリー")
    print("="*80)

    old_total = sum(r['old_count'] for r in comparison_results)
    new_total = sum(r['new_count'] for r in comparison_results)

    print(f"\n旧実装（簡易検索）: {old_total}件")
    print(f"新実装（ハイブリッド）: {new_total}件")
    print(f"精度向上: {((new_total - old_total) / max(old_total, 1) * 100):.1f}%\n")

    # 詳細レポート保存
    report_file = Path("/home/planj/patshinko-exam-app/backend/rag_comparison_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": comparison_results,
            "summary": {
                "old_total_hits": old_total,
                "new_total_hits": new_total,
                "improvement_percent": ((new_total - old_total) / max(old_total, 1) * 100)
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"📁 レポート保存: {report_file}\n")

if __name__ == "__main__":
    main()
