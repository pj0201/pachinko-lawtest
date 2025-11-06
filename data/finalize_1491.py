#!/usr/bin/env python3
"""
最終調整：1510問 → 1491問へ
不正対策から19問を削除して目標達成
"""

import json
import random
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path("/home/planj/patshinko-exam-app/data/FINAL_1491_DEDUPED.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_FINAL_1491.json")

TARGET_DIST = {
    '遊技機管理': 596,
    '営業時間・規制': 224,
    '営業許可関連': 194,
    '型式検定関連': 179,
    '不正対策': 149,
    '景品規制': 149
}

def main():
    print("=" * 80)
    print("最終調整スクリプト")
    print("=" * 80)

    # ロード
    print(f"\n📂 {INPUT_FILE} をロード中...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problems = data['problems']
    print(f"  現在の問題数: {len(problems)}問")

    # カテゴリ別にグループ化
    category_problems = defaultdict(list)
    for p in problems:
        category_problems[p['category']].append(p)

    print(f"\n📊 現在のカテゴリ別配分:")
    for cat in sorted(TARGET_DIST.keys()):
        actual = len(category_problems[cat])
        target = TARGET_DIST[cat]
        diff = actual - target
        symbol = "✅" if diff == 0 else "❌"
        print(f"  {symbol} {cat}: {actual}問 (目標: {target}問, {diff:+d}問)")

    # 削減すべきカテゴリを特定
    print(f"\n🔄 調整対象を特定中...")
    to_remove = {}
    for cat, target in TARGET_DIST.items():
        actual = len(category_problems[cat])
        if actual > target:
            to_remove[cat] = actual - target
            print(f"  {cat}: {to_remove[cat]}問を削除")

    # 削除を実行
    print(f"\n❌ 削除を実行中...")
    removed_count = 0

    for cat, remove_count in to_remove.items():
        # 削除対象を選択（生成された問題を優先）
        candidates = category_problems[cat]

        # 生成されたIDが大きい問題を優先的に削除
        candidates_sorted = sorted(candidates, key=lambda p: p.get('problem_id', 0), reverse=True)
        to_delete = candidates_sorted[:remove_count]

        for p in to_delete:
            problems.remove(p)
            removed_count += 1

        print(f"  {cat}: {remove_count}問を削除")

    final_count = len(problems)
    print(f"\n✅ 削除完了")
    print(f"  削除前: {len(category_problems['不正対策']) + sum(len(category_problems[c]) for c in category_problems if c != '不正対策')}問")
    print(f"  削除数: {removed_count}問")
    print(f"  最終: {final_count}問")

    # メタデータ更新
    print(f"\n📊 メタデータを更新中...")
    data['problems'] = problems
    data['metadata']['total_problems'] = final_count
    data['metadata']['version'] = "FINAL_1491_BALANCED_1.0"

    category_counts = defaultdict(int)
    for p in problems:
        category_counts[p['category']] += 1

    data['metadata']['statistics']['category_distribution'] = dict(category_counts)

    # 保存
    print(f"\n💾 {OUTPUT_FILE} に保存中...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 最終確認
    print(f"\n✅ 完了！")
    print("=" * 80)
    print(f"最終問題数: {final_count}問")
    print()
    print("📈 最終カテゴリ別配分:")
    all_match = True
    for cat in sorted(TARGET_DIST.keys()):
        actual = category_counts[cat]
        target = TARGET_DIST[cat]
        status = "✅" if actual == target else "❌"
        print(f"  {status} {cat}: {actual}問 (目標: {target}問)")
        if actual != target:
            all_match = False

    if all_match and final_count == 1491:
        print(f"\n✅ 完璧です！目標達成！")
    else:
        print(f"\n⚠️  調整が必要")

    print("=" * 80)

if __name__ == '__main__':
    main()
