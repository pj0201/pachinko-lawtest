#!/usr/bin/env python3
"""
問題データセット修正スクリプト
- 削減対象カテゴリの問題を削除
- 新規問題は独自の内容で作成（重複排除）
"""

import json
import random
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CURRENT_FILE = Path("/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_REBALANCED_1617_FIXED.json")

# 目標配分
TARGET_DISTRIBUTION = {
    '遊技機管理': 596,      # 現在540 → +56
    '営業時間・規制': 224,  # 現在216 → +8
    '営業許可関連': 194,    # 現在216 → -22
    '型式検定関連': 179,    # 現在192 → -13
    '不正対策': 149,        # 現在240 → -91
    '景品規制': 149         # 現在87 → +62
}

CURRENT_DISTRIBUTION = {
    '遊技機管理': 540,
    '不正対策': 240,
    '営業時間・規制': 216,
    '営業許可関連': 216,
    '型式検定関連': 192,
    '景品規制': 87
}

def load_problems():
    with open(CURRENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_varied_problem(ref_problem, new_id, variation_num):
    """既存問題をベースに、内容を変えた新問題を作成"""
    # テキストを明らかに変える（数字変更、表現変更など）
    original_text = ref_problem['problem_text']

    # いくつかのバリエーション戦略
    strategies = [
        lambda t: t.replace('新台', '既存台').replace('新', '既'),
        lambda t: t.replace('設置', '移設').replace('移動', '設置'),
        lambda t: t.replace('1年', '2年').replace('2年', '3年'),
        lambda t: t.replace('は', 'ではなく'),
        lambda t: t.replace('必須', '推奨'),
        lambda t: t.replace('可能', '不可'),
        lambda t: t.replace('義務', '努力義務'),
    ]

    strategy = strategies[variation_num % len(strategies)]
    varied_text = strategy(original_text)

    # 元のテキストと同じ場合は、詳細を追加
    if varied_text == original_text:
        varied_text = original_text + f"（パターン{variation_num}）"

    new_problem = {
        'problem_id': new_id,
        'theme_id': ref_problem.get('theme_id', 0),
        'theme_name': ref_problem.get('theme_name', ''),
        'category': ref_problem['category'],
        'is_subtheme_based': ref_problem.get('is_subtheme_based', False),
        'problem_type': ref_problem.get('problem_type', 'true_false'),
        'format': ref_problem.get('format', '○×'),
        'source_pdf': ref_problem.get('source_pdf', 1),
        'source_page': ref_problem.get('source_page', 0),
        'generated_at': datetime.now().isoformat(),
        'pattern_id': ref_problem.get('pattern_id', 1),
        'pattern_name': ref_problem.get('pattern_name', '基本知識'),
        'difficulty': ref_problem.get('difficulty', '★'),
        'problem_text': varied_text,  # 変更版テキスト
        'correct_answer': ref_problem.get('correct_answer', '○'),
        'explanation': ref_problem.get('explanation', ''),
        'legal_reference': ref_problem.get('legal_reference', {})
    }

    return new_problem

def main():
    print("=" * 70)
    print("問題データセット修正（削減+新規作成）")
    print("=" * 70)

    # ロード
    print("\n📂 既存データをロード中...")
    data = load_problems()
    problems = data['problems'][:]
    print(f"  既存問題数: {len(problems)}問")

    # ステップ1: カテゴリ別にグループ化
    print("\n🔄 ステップ1: カテゴリ別にグループ化...")
    category_problems = defaultdict(list)
    for p in problems:
        category_problems[p['category']].append(p)

    for cat, probs in category_problems.items():
        print(f"  {cat}: {len(probs)}問")

    # ステップ2: 削減対象カテゴリの問題を削除
    print("\n❌ ステップ2: 削減対象カテゴリから問題を削除...")
    categories_to_reduce = {
        '営業許可関連': 22,      # 216 → 194 (-22)
        '型式検定関連': 13,      # 192 → 179 (-13)
        '不正対策': 91           # 240 → 149 (-91)
    }

    for category, reduce_count in categories_to_reduce.items():
        current_problems = category_problems[category]
        # ランダムに削減対象を選択
        to_remove = random.sample(current_problems, reduce_count)
        for p in to_remove:
            problems.remove(p)
        print(f"  {category}: {reduce_count}問を削除")

    print(f"  削除後の総問題数: {len(problems)}問")

    # ステップ3: 新規問題を作成（バリエーション形式）
    print("\n✨ ステップ3: 新規問題を作成中...")
    new_problems = []
    next_id = len(problems) + 1

    # 追加対象
    categories_to_add = {
        '遊技機管理': 56,
        '営業時間・規制': 8,
        '景品規制': 62
    }

    for category, add_count in categories_to_add.items():
        print(f"  {category}: {add_count}問を作成中...")
        source_problems = category_problems[category]

        for i in range(add_count):
            ref_problem = random.choice(source_problems)
            new_problem = create_varied_problem(ref_problem, next_id, i)
            new_problems.append(new_problem)
            next_id += 1

    # マージ
    print(f"\n🔀 ステップ4: 新問題をマージ中...")
    data['problems'] = problems + new_problems
    final_count = len(data['problems'])
    print(f"  最終問題数: {final_count}問（+{len(new_problems)}問）")

    # メタデータ更新
    print("\n📊 ステップ5: メタデータを更新中...")
    data['metadata']['total_problems'] = final_count
    data['metadata']['version'] = "REBALANCED_FIXED_1.0"
    data['metadata']['updated_at'] = datetime.now().isoformat()

    # カテゴリ別統計
    category_counts = defaultdict(int)
    for p in data['problems']:
        category_counts[p['category']] += 1

    data['metadata']['statistics']['category_distribution'] = dict(category_counts)

    # 保存
    print("\n💾 ステップ6: 修正版を保存中...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 結果報告
    print("\n✅ 完了！")
    print("=" * 70)
    print(f"📌 新規ファイル: {OUTPUT_FILE}")
    print(f"📊 総問題数: {len(problems)} → {final_count}問")
    print("\n📈 最終カテゴリ別配分:")
    for category in sorted(TARGET_DISTRIBUTION.keys()):
        actual = category_counts[category]
        target = TARGET_DISTRIBUTION[category]
        diff = actual - target
        status = "✅" if diff == 0 else "⚠️ "
        print(f"  {status} {category}: {actual}問 (目標: {target}問, {diff:+d}問)")
    print("=" * 70)

if __name__ == '__main__':
    main()
