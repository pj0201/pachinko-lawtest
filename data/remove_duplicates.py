#!/usr/bin/env python3
"""
重複問題排除スクリプト - Union-Find アプローチ
完全重複（99%以上）を検出・排除
"""

import json
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict

INPUT_FILE = Path("/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/DEDUPED_BASE.json")

def text_similarity(text1, text2):
    """テキストの類似度を計算"""
    return SequenceMatcher(None, text1, text2).ratio()

def find_duplicate_groups(problems, threshold=0.99):
    """重複グループを検出"""
    duplicate_map = defaultdict(set)
    total = len(problems)

    print("🔍 重複検出中...")

    for i, p1 in enumerate(problems):
        if i % 200 == 0:
            print(f"  進捗: {i}/{total}")

        text1 = p1.get('problem_text', '')
        id1 = p1.get('problem_id')

        for p2 in problems[i+1:]:
            text2 = p2.get('problem_text', '')
            id2 = p2.get('problem_id')

            similarity = text_similarity(text1, text2)

            if similarity >= threshold:
                duplicate_map[id1].add(id2)
                duplicate_map[id2].add(id1)

    # BFSでグループ化
    visited = set()
    groups = []

    for pid in duplicate_map:
        if pid in visited:
            continue

        group = set()
        queue = [pid]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)
            group.add(current)

            for neighbor in duplicate_map[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

        if group:
            groups.append(group)

    return groups

def remove_duplicates(input_file, output_file):
    """重複問題を排除"""
    print("=" * 80)
    print("重複問題排除スクリプト")
    print("=" * 80)

    # ロード
    print(f"\n📂 {input_file} をロード中...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problems = data.get('problems', [])
    original_count = len(problems)
    print(f"  元の問題数: {original_count}問")

    # 重複グループを検出
    print("\n🔍 重複グループを検出中...")
    groups = find_duplicate_groups(problems, threshold=0.99)
    print(f"  重複グループ数: {len(groups)}")

    # 統計情報
    total_duplicates = sum(len(g) - 1 for g in groups)
    duplicate_pairs = sum(len(g) // 2 for g in groups)
    print(f"  重複ペア数: 約{duplicate_pairs}ペア")
    print(f"  重複に関与する問題: 約{total_duplicates * 2}問")

    # カテゴリ情報を保持するマップを作成
    problem_by_id = {p['problem_id']: p for p in problems}

    # 各グループから1つずつ選択
    print("\n🔀 各グループから最適な問題を選択中...")
    unique_problems = []
    removed_count = 0

    # グループに属さない問題を追加
    all_duplicate_ids = set()
    for group in groups:
        all_duplicate_ids.update(group)

    for p in problems:
        if p.get('problem_id') not in all_duplicate_ids:
            unique_problems.append(p)

    # 各グループから1つ選択
    for group_idx, group in enumerate(groups):
        # グループ内で最小のIDを持つ問題を選択（古い問題を優先）
        best_id = min(group)
        best_problem = problem_by_id[best_id]
        unique_problems.append(best_problem)
        removed_count += len(group) - 1

        if (group_idx + 1) % 100 == 0:
            print(f"  処理済みグループ: {group_idx + 1}/{len(groups)}")

    # 結果
    final_count = len(unique_problems)
    print(f"\n✅ 重複排除完了")
    print(f"  元の問題数: {original_count}問")
    print(f"  削除された問題数: {removed_count}問")
    print(f"  重複排除後: {final_count}問")
    print(f"  削減率: {(removed_count / original_count * 100):.1f}%")

    # メタデータ更新
    data['problems'] = unique_problems
    data['metadata']['total_problems'] = final_count
    data['metadata']['version'] = "DEDUPED_1.0"
    data['metadata']['deduplication'] = {
        'original_count': original_count,
        'removed_count': removed_count,
        'final_count': final_count,
        'duplicate_groups': len(groups)
    }

    # カテゴリ分布を計算
    from collections import Counter
    category_counts = Counter(p['category'] for p in unique_problems)
    data['metadata']['statistics']['category_distribution'] = dict(category_counts)

    # 保存
    print(f"\n💾 {output_file} に保存中...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完了！\n")

    # カテゴリ分布の表示
    print("📊 カテゴリ別の問題数:")
    for cat in sorted(category_counts.keys()):
        count = category_counts[cat]
        pct = (count / final_count) * 100
        print(f"  {cat}: {count}問 ({pct:.1f}%)")

    print("=" * 80)

if __name__ == '__main__':
    remove_duplicates(INPUT_FILE, OUTPUT_FILE)
