#!/usr/bin/env python3
"""
50問の品質評価スクリプト
Phase 3.3: 品質閾値達成確認
"""

import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_50_hybrid_rag.json"

def evaluate_problem_quality(problem: dict) -> dict:
    """問題生成品質の定量評価"""
    evaluation = {
        "problem_id": problem.get('problem_id', 'N/A'),
        "category": problem.get('category', 'N/A'),
        "scores": {}
    }

    # 1. RAG検索結果の有無
    has_rag_results = problem.get('rag_search_results', {}).get('result_count', 0) > 0
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

def main():
    print("\n" + "="*80)
    print("📊 Phase 3.3: 50問の品質評価")
    print("="*80 + "\n")

    # ファイル読み込み
    with open(PROBLEMS_FILE) as f:
        problems = json.load(f)

    print(f"📖 {len(problems)}問題を評価中...\n")

    quality_results = []
    for problem in problems:
        quality = evaluate_problem_quality(problem)
        quality_results.append(quality)

    # サマリー計算
    overall_scores = [r['overall_score'] for r in quality_results]
    avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0

    rag_found_rate = sum(1 for r in quality_results if r['scores']['rag_search_found'] == 1.0) / len(quality_results) if quality_results else 0
    no_template_rate = sum(1 for r in quality_results if r['scores']['no_template'] == 1.0) / len(quality_results) if quality_results else 0
    legal_ref_rate = sum(1 for r in quality_results if r['scores']['legal_reference'] >= 1.0) / len(quality_results) if quality_results else 0

    # 説明長の統計
    explanation_lengths = [len(p.get('explanation_hybrid_rag', '')) for p in problems]
    avg_length = sum(explanation_lengths) / len(explanation_lengths) if explanation_lengths else 0
    min_length = min(explanation_lengths) if explanation_lengths else 0
    max_length = max(explanation_lengths) if explanation_lengths else 0

    # 結果表示
    print("="*80)
    print("📊 品質評価サマリー")
    print("="*80)

    print(f"\n【総合品質スコア】")
    print(f"  平均スコア: {avg_score:.2f}/1.0")
    print(f"  目標値: 0.80以上")
    if avg_score >= 0.80:
        print(f"  判定: ✅ 目標達成")
    else:
        print(f"  判定: ⚠️ 要改善 (不足: {0.80 - avg_score:.2f})")

    print(f"\n【メトリクス】")
    print(f"  RAG検索成功率: {rag_found_rate*100:.1f}% ({int(rag_found_rate*len(quality_results))}/{len(quality_results)})")
    print(f"  テンプレート排除率: {no_template_rate*100:.1f}% ({int(no_template_rate*len(quality_results))}/{len(quality_results)})")
    print(f"  法令参照率: {legal_ref_rate*100:.1f}% ({int(legal_ref_rate*len(quality_results))}/{len(quality_results)})")

    print(f"\n【説明長（文字数）】")
    print(f"  平均: {avg_length:.0f}文字")
    print(f"  最小: {min_length}文字")
    print(f"  最大: {max_length}文字")
    print(f"  目標: 150-250文字")

    # 詳細結果保存
    report = {
        "timestamp": datetime.now().isoformat(),
        "problem_count": len(problems),
        "summary": {
            "average_score": avg_score,
            "target_score": 0.80,
            "achievement": "✅ 達成" if avg_score >= 0.80 else "⚠️ 要改善",
            "rag_search_rate": round(rag_found_rate, 3),
            "template_exclusion_rate": round(no_template_rate, 3),
            "legal_reference_rate": round(legal_ref_rate, 3),
            "explanation_length": {
                "average": round(avg_length, 1),
                "min": min_length,
                "max": max_length
            }
        },
        "detailed_results": quality_results
    }

    output_file = REPO_ROOT / "backend/quality_eval_50_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📁 詳細結果: {output_file}")

    print("\n" + "="*80)
    if avg_score >= 0.80:
        print("✅ 品質基準達成！本番投入準備完了")
    else:
        print("⚠️ 品質改善が必要な状態")
    print("="*80 + "\n")

    return avg_score

if __name__ == "__main__":
    main()
