#!/usr/bin/env python3
"""
RAGハイブリッド検索システムの品質テスト
1. マッピング正確性テスト
2. 説明文品質テスト
3. 複合語処理テスト
4. ソース統合テスト
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def test_mapping_accuracy():
    """マッピングの正確性テスト"""

    print("\n【テスト1: マッピング正確性】")
    print("-" * 60)

    with open('backend/rag_database_hybrid_final.json', 'r') as f:
        rag = json.load(f)

    # テーマごとに問題を検証
    theme_issues = []
    theme_coverage = defaultdict(int)

    for pid, problem in rag['problems'].items():
        theme = problem['verified_theme']
        category = problem['verified_category']
        score = problem['keyword_match_score']

        theme_coverage[theme] += 1

        # スコアが0のテーマをチェック
        if score == 0 and theme == "営業許可と型式検定の違い":
            theme_issues.append({
                'problem_id': pid,
                'theme': theme,
                'score': score,
                'issue': 'ゼロスコアマッピング'
            })

    print(f"✅ テーマ覆蓋: {len(theme_coverage)}テーマ")
    print(f"  期待: 17テーマ")
    print(f"  結果: {'OK' if len(theme_coverage) == 17 else 'NG'}")

    if theme_issues:
        print(f"\n⚠️  問題検出: {len(theme_issues)}件")
        for issue in theme_issues[:3]:
            print(f"  - Problem {issue['problem_id']}: {issue['issue']}")
    else:
        print(f"✅ マッピング異常: なし")

    # カテゴリ分布チェック
    print(f"\n✅ カテゴリ分布:")
    for cat, count in sorted(rag['statistics']['problems_by_category'].items(),
                            key=lambda x: -x[1]):
        pct = (count / 500) * 100
        print(f"  {cat:20} {count:3}問 ({pct:5.1f}%)")

    return len(theme_issues) == 0

def test_explanation_quality():
    """説明文品質テスト"""

    print("\n【テスト2: 説明文品質】")
    print("-" * 60)

    with open('backend/rag_database_hybrid_final.json', 'r') as f:
        rag = json.load(f)

    lengths = []
    in_range = 0
    too_short = 0
    too_long = 0

    for pid, problem in rag['problems'].items():
        length = problem['explanation_length']
        lengths.append(length)

        if 150 <= length <= 250:
            in_range += 1
        elif length < 150:
            too_short += 1
        else:
            too_long += 1

    avg_len = sum(lengths) / len(lengths)

    print(f"✅ 説明文長の統計:")
    print(f"  平均: {avg_len:.1f}文字 (目標: 150-250)")
    print(f"  目標範囲内: {in_range}/500問 ({(in_range/500)*100:.1f}%)")
    print(f"  短すぎ (<150): {too_short}問")
    print(f"  長すぎ (>250): {too_long}問")

    # サンプル表示
    print(f"\n✅ 説明文サンプル:")
    sample_pids = list(rag['problems'].keys())[:2]
    for pid in sample_pids:
        problem = rag['problems'][pid]
        exp = problem['explanation']
        print(f"  [{problem['verified_theme']}] {exp[:80]}...")

    return in_range >= 300  # 60%以上が目標

def test_compound_words():
    """複合語処理テスト"""

    print("\n【テスト3: 複合語処理】")
    print("-" * 60)

    with open('backend/rag_database_hybrid_final.json', 'r') as f:
        rag = json.load(f)

    compound_words = rag['search_config']['compound_words']

    print(f"✅ 複合語設定:")
    print(f"  登録数: {len(compound_words)}個")
    print(f"  decompound_mode: {rag['search_config']['decompound_mode']}")

    # 主要複合語が含まれているか確認
    critical_words = ["営業許可", "型式検定", "営業禁止", "不正改造"]
    all_present = all(word in compound_words for word in critical_words)

    print(f"\n✅ 主要複合語の確認:")
    for word in critical_words:
        present = "✓" if word in compound_words else "✗"
        print(f"  {present} {word}")

    print(f"\n✅ キーワード重み付け:")
    for kw, weight in rag['search_config']['keyword_boost'].items():
        print(f"  {kw:20} x{weight}")

    return all_present

def test_source_integration():
    """ソース統合テスト"""

    print("\n【テスト4: ソース統合】")
    print("-" * 60)

    with open('backend/rag_database_hybrid_final.json', 'r') as f:
        rag = json.load(f)

    stats = rag['statistics']['source_coverage']

    print(f"✅ ソース統合率:")
    print(f"  風営法統合: {stats['with_legal_sections']:3}問 ({(stats['with_legal_sections']/500)*100:5.1f}%)")
    print(f"  講習ガイドライン統合: {stats['with_lecture_files']:3}問 ({(stats['with_lecture_files']/500)*100:5.1f}%)")
    print(f"  両ソース統合: {stats['both_sources']:3}問 ({(stats['both_sources']/500)*100:5.1f}%)")

    # テーマ別ソース確認
    print(f"\n✅ テーマ別ソース統合:")
    themes_with_both = 0
    themes_with_legal = 0
    themes_with_lecture = 0

    for theme_name, theme_data in rag['index']['themes'].items():
        legal = len(theme_data.get('legal_sections', []))
        lecture = len(theme_data.get('lecture_files', []))

        if legal > 0:
            themes_with_legal += 1
        if lecture > 0:
            themes_with_lecture += 1
        if legal > 0 and lecture > 0:
            themes_with_both += 1

    print(f"  法律セクション統合テーマ: {themes_with_legal}/17")
    print(f"  講習ガイドライン統合テーマ: {themes_with_lecture}/17")
    print(f"  両ソース統合テーマ: {themes_with_both}/17")

    return stats['with_lecture_files'] == 500  # 講習ガイドライン100%統合

def test_edge_cases():
    """エッジケースの検証"""

    print("\n【テスト5: エッジケース検証】")
    print("-" * 60)

    with open('backend/rag_database_hybrid_final.json', 'r') as f:
        rag = json.load(f)

    issues = []

    for pid, problem in rag['problems'].items():
        # 空の説明文チェック
        if not problem['explanation'] or len(problem['explanation']) < 10:
            issues.append(f"Problem {pid}: 説明文が空/極度に短い")

        # テーマの一貫性チェック
        if not problem['verified_theme'] or not problem['verified_category']:
            issues.append(f"Problem {pid}: テーマ/カテゴリが未設定")

    if issues:
        print(f"⚠️  検出された問題: {len(issues)}件")
        for issue in issues[:5]:
            print(f"  - {issue}")
    else:
        print(f"✅ エッジケース: 検出なし")

    # 複合語マッチングの確認
    print(f"\n✅ 複合語マッチング確認:")
    compound_words = set(rag['search_config']['compound_words'])
    matched_in_problems = 0

    for pid, problem in rag['problems'].items():
        text = problem['problem_text']
        if any(word in text for word in compound_words):
            matched_in_problems += 1

    print(f"  複合語を含む問題: {matched_in_problems}/500問 ({(matched_in_problems/500)*100:.1f}%)")

    return len(issues) == 0

def run_all_tests():
    """全テストを実行"""

    print("=" * 60)
    print("【RAGハイブリッド検索システム - 品質テスト】")
    print("=" * 60)

    results = {
        'mapping': test_mapping_accuracy(),
        'explanation': test_explanation_quality(),
        'compound_words': test_compound_words(),
        'source_integration': test_source_integration(),
        'edge_cases': test_edge_cases()
    }

    print("\n" + "=" * 60)
    print("【テスト結果サマリー】")
    print("=" * 60)

    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "⚠️  CHECK"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1

    print(f"\n総合: {passed}/{len(results)}テスト合格")

    if passed == len(results):
        print("\n🎉 RAGハイブリッド検索システム - 品質OK")
    else:
        print(f"\n⚠️  {len(results) - passed}つの項目を確認してください")

if __name__ == "__main__":
    run_all_tests()
