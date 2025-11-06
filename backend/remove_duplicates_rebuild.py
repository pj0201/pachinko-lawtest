#!/usr/bin/env python3
"""
重複問題の除去 + RAG再構築
元データに66.6%の重複があったため、一意な問題のみを使用して再構築
"""

import json
from collections import defaultdict

print("【重複除去 + RAG再構築】\n")

# 1. 元データから一意な問題のみを抽出
with open('backend/problems_final_500_complete.json', 'r') as f:
    all_problems = json.load(f)

# 問題テキストでグループ化
text_to_problems = defaultdict(list)
for problem in all_problems:
    text = problem.get('problem_text', '')
    text_to_problems[text].append(problem)

# 各グループから最初の1つだけを取得
deduplicated = []
seen_texts = set()

for problem in all_problems:
    text = problem.get('problem_text', '')
    if text not in seen_texts:
        deduplicated.append(problem)
        seen_texts.add(text)

print(f"✅ 重複除去結果:")
print(f"  元データ: {len(all_problems)}問")
print(f"  重複除去後: {len(deduplicated)}問")
print(f"  削除数: {len(all_problems) - len(deduplicated)}問")

# 2. 重複除去データを保存
with open('backend/problems_deduplicated.json', 'w') as f:
    json.dump(deduplicated, f, indent=2, ensure_ascii=False)

print(f"\n✅ 重複除去済みデータを保存:")
print(f"  problems_deduplicated.json ({len(deduplicated)}問)")

# 3. 新しいRAGデータベースを構築（重複除去版）
with open('rag_data/hybrid_index_verified.json', 'r') as f:
    hybrid_index = json.load(f)

rag_deduplicated = {
    'metadata': {
        'version': '3.1-deduplicated',
        'build_date': '2025-11-06',
        'deduplication': True,
        'original_problem_count': len(all_problems),
        'deduplicated_problem_count': len(deduplicated),
        'duplicate_count': len(all_problems) - len(deduplicated),
        'system': 'RAG Hybrid Search - BM25 + Semantic Search (Deduplicated)',
        'features': [
            'compound_word_support',
            'semantic_search',
            'bm25_keyword_search',
            'theme_based_retrieval',
            'source_verification',
            'duplicate_removal'
        ]
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

# 統計情報を初期化
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

total_exp_length = 0

# 重複除去済み問題を統合
for problem in deduplicated:
    pid = problem.get('problem_id', '')
    if not pid:
        continue

    theme = problem.get('verified_theme', '不明')
    category = problem.get('verified_category', '不明')

    integrated = {
        'problem_id': pid,
        'problem_text': problem.get('problem_text', ''),
        'correct_answer': problem.get('correct_answer', 'A'),
        'options': problem.get('options', {}),
        'explanation': problem.get('improved_explanation', ''),
        'explanation_length': problem.get('explanation_length', 0),
        'verified_theme': theme,
        'verified_category': category,
        'keyword_match_score': problem.get('keyword_match_score', 0),
        'source_data': {
            'legal_sections': [],
            'lecture_files': []
        }
    }

    # テーマからソース情報を追加
    if theme in rag_deduplicated['index']['themes']:
        theme_data = rag_deduplicated['index']['themes'][theme]
        integrated['source_data']['legal_sections'] = theme_data.get('legal_sections', [])
        integrated['source_data']['lecture_files'] = theme_data.get('lecture_files', [])

    rag_deduplicated['problems'][pid] = integrated

    # 統計更新
    if theme not in stats['problems_by_theme']:
        stats['problems_by_theme'][theme] = 0
    stats['problems_by_theme'][theme] += 1

    if category not in stats['problems_by_category']:
        stats['problems_by_category'][category] = 0
    stats['problems_by_category'][category] += 1

    exp_len = integrated['explanation_length']
    if 150 <= exp_len <= 250:
        stats['explanation_quality']['in_target_range'] += 1
    stats['explanation_quality']['min_length'] = min(
        stats['explanation_quality']['min_length'], exp_len
    )
    stats['explanation_quality']['max_length'] = max(
        stats['explanation_quality']['max_length'], exp_len
    )
    total_exp_length += exp_len

    legal_count = len(integrated['source_data']['legal_sections'])
    lecture_count = len(integrated['source_data']['lecture_files'])
    if legal_count > 0:
        stats['source_coverage']['with_legal_sections'] += 1
    if lecture_count > 0:
        stats['source_coverage']['with_lecture_files'] += 1
    if legal_count > 0 and lecture_count > 0:
        stats['source_coverage']['both_sources'] += 1

stats['explanation_quality']['avg_length'] = total_exp_length / len(deduplicated) if deduplicated else 0

rag_deduplicated['statistics'] = stats

# 4. 重複除去版RAGを保存
output_path = 'backend/rag_database_hybrid_deduplicated.json'
with open(output_path, 'w') as f:
    json.dump(rag_deduplicated, f, indent=2, ensure_ascii=False)

print(f"\n✅ 重複除去版RAGデータベースを生成:")
print(f"  {output_path}")

# 5. 統計を表示
print(f"\n【重複除去版RAG - 統計】\n")
print(f"  総問題数: {len(rag_deduplicated['problems'])}")
print(f"  説明文品質: 平均{stats['explanation_quality']['avg_length']:.1f}文字")
print(f"  目標範囲内: {stats['explanation_quality']['in_target_range']}/{len(deduplicated)}問")

print(f"\n【カテゴリ別分布】\n")
for cat in sorted(stats['problems_by_category'].keys()):
    count = stats['problems_by_category'][cat]
    pct = (count / len(deduplicated)) * 100
    print(f"  {cat:20} {count:3}問 ({pct:5.1f}%)")

if __name__ == "__main__":
    pass
