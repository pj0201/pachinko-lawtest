#!/usr/bin/env python3
"""
RAG最終統合 - ハイブリッド検索 + 詳細説明 完成版
問題 + ハイブリッドインデックス + 説明文を統合した最終データベース
"""

import json
from pathlib import Path
from typing import Dict, List

def finalize_rag():
    """RAG完成版を構築"""

    print("=" * 80)
    print("【RAGハイブリッド検索システム - 最終統合】")
    print("=" * 80)
    print()

    # 1. 詳細説明文を持つ問題を読み込む
    with open('backend/problems_500_detailed_explanations.json', 'r') as f:
        problems = json.load(f)

    # 2. ハイブリッドインデックスを読み込む
    with open('rag_data/hybrid_index_verified.json', 'r') as f:
        hybrid_index = json.load(f)

    # 3. 最終RAGデータベースを構築
    rag_database = {
        'metadata': {
            'version': '3.0-final',
            'build_date': '2025-11-06',
            'system': 'RAG Hybrid Search - BM25 + Semantic Search',
            'source_data': [
                'problems_500_detailed_explanations.json',
                'hybrid_index_verified.json'
            ],
            'features': [
                'compound_word_support',
                'semantic_search',
                'bm25_keyword_search',
                'theme_based_retrieval',
                'source_verification'
            ],
            'total_problems': len(problems),
            'theme_count': len(hybrid_index['themes']),
            'category_count': len(set(d.get('category') for d in hybrid_index['themes'].values()))
        },
        'problems': {},
        'index': hybrid_index,
        'search_config': {
            'compound_words': hybrid_index['search_index']['compound_words'],
            'decompound_mode': True,
            'bm25_weight': 0.5,
            'semantic_weight': 0.5,
            'keyword_boost': {
                '営業許可': 2.0,
                '型式検定': 1.8,
                '営業禁止': 1.5,
                '不正改造': 1.8,
                '景品': 1.3
            }
        }
    }

    # 4. 問題データを統合
    print("【問題データ統合中...】\n")

    for problem in problems:
        pid = problem.get('problem_id', '')
        if not pid:
            continue

        # 統合データを構築
        integrated_problem = {
            'problem_id': pid,
            'problem_text': problem.get('problem_text', ''),
            'correct_answer': problem.get('correct_answer', 'A'),
            'options': problem.get('options', {}),
            'explanation': problem.get('improved_explanation', ''),
            'explanation_length': problem.get('explanation_length', 0),
            'verified_theme': problem.get('verified_theme', ''),
            'verified_category': problem.get('verified_category', ''),
            'keyword_match_score': problem.get('keyword_match_score', 0),
            'source_data': {
                'legal_sections': [],
                'lecture_files': []
            }
        }

        # テーマからソース情報を追加
        theme = problem.get('verified_theme', '')
        if theme in rag_database['index']['themes']:
            theme_data = rag_database['index']['themes'][theme]
            integrated_problem['source_data']['legal_sections'] = theme_data.get('legal_sections', [])
            integrated_problem['source_data']['lecture_files'] = theme_data.get('lecture_files', [])

        rag_database['problems'][pid] = integrated_problem

    # 5. 統計情報を追加
    print("【統計情報集計中...】\n")

    stats = {
        'problems_by_theme': {},
        'problems_by_category': {},
        'explanation_quality': {
            'in_target_range': 0,
            'min_length': float('inf'),
            'max_length': 0,
            'avg_length': 0
        },
        'source_coverage': {
            'with_legal_sections': 0,
            'with_lecture_files': 0,
            'both_sources': 0
        }
    }

    total_length = 0

    for pid, problem in rag_database['problems'].items():
        # テーマ別統計
        theme = problem['verified_theme']
        if theme not in stats['problems_by_theme']:
            stats['problems_by_theme'][theme] = 0
        stats['problems_by_theme'][theme] += 1

        # カテゴリ別統計
        category = problem['verified_category']
        if category not in stats['problems_by_category']:
            stats['problems_by_category'][category] = 0
        stats['problems_by_category'][category] += 1

        # 説明文の統計
        exp_len = problem['explanation_length']
        if 150 <= exp_len <= 250:
            stats['explanation_quality']['in_target_range'] += 1
        stats['explanation_quality']['min_length'] = min(
            stats['explanation_quality']['min_length'], exp_len
        )
        stats['explanation_quality']['max_length'] = max(
            stats['explanation_quality']['max_length'], exp_len
        )
        total_length += exp_len

        # ソース統合の統計
        legal_count = len(problem['source_data']['legal_sections'])
        lecture_count = len(problem['source_data']['lecture_files'])
        if legal_count > 0:
            stats['source_coverage']['with_legal_sections'] += 1
        if lecture_count > 0:
            stats['source_coverage']['with_lecture_files'] += 1
        if legal_count > 0 and lecture_count > 0:
            stats['source_coverage']['both_sources'] += 1

    stats['explanation_quality']['avg_length'] = total_length / len(rag_database['problems'])

    rag_database['statistics'] = stats

    # 6. 最終ファイルを保存
    output_path = 'backend/rag_database_hybrid_final.json'
    with open(output_path, 'w') as f:
        json.dump(rag_database, f, indent=2, ensure_ascii=False)

    print("✅ RAG最終統合完了\n")

    # 7. 統計情報を表示
    print("【RAGハイブリッド統計】\n")
    print(f"  総問題数: {len(rag_database['problems'])}")
    print(f"  総テーマ数: {len(stats['problems_by_theme'])}")
    print(f"  総カテゴリ数: {len(stats['problems_by_category'])}")

    print(f"\n【説明文の品質】\n")
    print(f"  最小長: {stats['explanation_quality']['min_length']}文字")
    print(f"  最大長: {stats['explanation_quality']['max_length']}文字")
    print(f"  平均長: {stats['explanation_quality']['avg_length']:.1f}文字")
    print(f"  目標範囲内: {stats['explanation_quality']['in_target_range']}/500問 ({(stats['explanation_quality']['in_target_range']/500)*100:.1f}%)")

    print(f"\n【カテゴリ別分布】\n")
    for cat in sorted(stats['problems_by_category'].keys()):
        count = stats['problems_by_category'][cat]
        pct = (count / 500) * 100
        print(f"  {cat:20} {count:3}問 ({pct:5.1f}%)")

    print(f"\n【ソース統合状況】\n")
    legal = stats['source_coverage']['with_legal_sections']
    lecture = stats['source_coverage']['with_lecture_files']
    both = stats['source_coverage']['both_sources']

    print(f"  風営法セクション統合: {legal}問 ({(legal/500)*100:.1f}%)")
    print(f"  講習ガイドライン統合: {lecture}問 ({(lecture/500)*100:.1f}%)")
    print(f"  両ソース統合: {both}問 ({(both/500)*100:.1f}%)")

    print(f"\n【複合語サポート】\n")
    compound_words = rag_database['search_config']['compound_words']
    print(f"  複合語数: {len(compound_words)}")
    print(f"  decompound_mode: {rag_database['search_config']['decompound_mode']}")

    print(f"\n【出力ファイル】\n")
    print(f"  {output_path}")
    print(f"  ファイルサイズ: {Path(output_path).stat().st_size / 1024:.1f}KB")

    print("\n" + "=" * 80)
    print("【RAGハイブリッド検索システム - 完成】")
    print("=" * 80)

if __name__ == "__main__":
    finalize_rag()
