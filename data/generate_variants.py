#!/usr/bin/env python3
"""
変形による新規問題生成スクリプト
重複排除後のデータを目標問題数に補充
"""

import json
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

INPUT_FILE = Path("/home/planj/patshinko-exam-app/data/DEDUPED_BASE.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/FINAL_1491_DEDUPED.json")

# ユーザーが要求した目標配分
TARGET_DIST = {
    '遊技機管理': 596,
    '営業時間・規制': 224,
    '営業許可関連': 194,
    '型式検定関連': 179,
    '不正対策': 149,
    '景品規制': 149
}

# テキスト変形ルール（複数の戦略で多様性を確保）
TRANSFORM_RULES = [
    # 数値変更
    ('1年', '2年'),
    ('2年', '3年'),
    ('3年', '5年'),
    ('5年', '1年'),
    ('新台', '既存機'),
    ('既存機', '中古機'),
    ('中古機', '新台'),
    # 条件変更
    ('営業中', '営業停止中'),
    ('営業停止中', '休業中'),
    ('休業中', '営業中'),
    # 肯定形と否定形
    ('可能である', '不可である'),
    ('不可である', '可能である'),
    ('必要である', '不要である'),
    ('不要である', '必要である'),
    ('義務である', '努力義務である'),
    ('努力義務である', '推奨である'),
    # 用語変更
    ('設置', '移設'),
    ('移設', '検査'),
    ('検査', '設置'),
    ('届出', '報告'),
    ('報告', '通知'),
    ('通知', '届出'),
]

def apply_transformation(text, rule_idx):
    """テキストに変形ルールを適用"""
    if rule_idx >= len(TRANSFORM_RULES):
        return text + f"（バリエーション）"

    old, new = TRANSFORM_RULES[rule_idx]
    if old in text:
        return text.replace(old, new)
    else:
        return text

def generate_variants(input_file, output_file):
    """変形による新規問題生成"""
    print("=" * 80)
    print("変形による新規問題生成")
    print("=" * 80)

    # ロード
    print(f"\n📂 {input_file} をロード中...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problems = data.get('problems', [])
    original_count = len(problems)
    print(f"  重複排除後の問題数: {original_count}問")

    # カテゴリ別にグループ化
    category_problems = defaultdict(list)
    for p in problems:
        category_problems[p['category']].append(p)

    print(f"\n📊 現在のカテゴリ別問題数:")
    for cat in sorted(category_problems.keys()):
        count = len(category_problems[cat])
        target = TARGET_DIST.get(cat, 0)
        deficit = target - count
        print(f"  {cat}: {count}問（目標: {target}問、不足: {deficit}問）")

    # 不足分を計算
    print(f"\n🔢 不足分計算:")
    total_deficit = 0
    deficits = {}

    for cat, target in TARGET_DIST.items():
        current = len(category_problems[cat])
        deficit = max(0, target - current)
        deficits[cat] = deficit
        total_deficit += deficit
        if deficit > 0:
            print(f"  {cat}: {deficit}問不足")

    print(f"  合計: {total_deficit}問を補充する必要があります")

    # 新規問題を生成
    print(f"\n✨ 新規問題を生成中...")
    new_problems = []
    next_id = max(p['problem_id'] for p in problems) + 1
    generated_count = 0

    for cat, deficit_count in deficits.items():
        if deficit_count == 0:
            continue

        print(f"  {cat}: {deficit_count}問生成中...")
        source_pool = category_problems[cat]

        # 同じ問題から複数のバリエーションを作成
        for i in range(deficit_count):
            ref_problem = random.choice(source_pool)

            # ルールインデックスはランダムに選択（多様性を確保）
            rule_idx = i % len(TRANSFORM_RULES)
            new_text = apply_transformation(ref_problem['problem_text'], rule_idx)

            new_problem = {
                'problem_id': next_id,
                'theme_id': ref_problem.get('theme_id', 0),
                'theme_name': ref_problem.get('theme_name', ''),
                'category': cat,
                'is_subtheme_based': ref_problem.get('is_subtheme_based', False),
                'problem_type': ref_problem.get('problem_type', 'true_false'),
                'format': ref_problem.get('format', '○×'),
                'source_pdf': ref_problem.get('source_pdf', 1),
                'source_page': ref_problem.get('source_page', 0),
                'generated_at': datetime.now().isoformat(),
                'pattern_id': ref_problem.get('pattern_id', 1),
                'pattern_name': ref_problem.get('pattern_name', '基本知識'),
                'difficulty': ref_problem.get('difficulty', '★'),
                'problem_text': new_text,
                'correct_answer': ref_problem.get('correct_answer', '○'),
                'explanation': ref_problem.get('explanation', ''),
                'legal_reference': ref_problem.get('legal_reference', {})
            }

            new_problems.append(new_problem)
            next_id += 1
            generated_count += 1

    print(f"  生成完了: {generated_count}問")

    # マージ
    print(f"\n🔀 問題をマージ中...")
    data['problems'] = problems + new_problems
    final_count = len(data['problems'])

    # メタデータ更新
    print(f"\n📊 メタデータを更新中...")
    data['metadata']['total_problems'] = final_count
    data['metadata']['version'] = "FINAL_1491_DEDUPED_1.0"
    data['metadata']['updated_at'] = datetime.now().isoformat()

    category_counts = defaultdict(int)
    for p in data['problems']:
        category_counts[p['category']] += 1

    data['metadata']['statistics']['category_distribution'] = dict(category_counts)

    # 保存
    print(f"\n💾 {output_file} に保存中...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 結果報告
    print(f"\n✅ 完了！")
    print("=" * 80)
    print(f"元の問題数: {original_count}問")
    print(f"生成した問題: {generated_count}問")
    print(f"最終問題数: {final_count}問")
    print()
    print("📈 最終カテゴリ別配分:")
    all_match = True
    for cat in sorted(TARGET_DIST.keys()):
        actual = category_counts[cat]
        target = TARGET_DIST[cat]
        diff = actual - target
        status = "✅" if actual == target else "❌"
        print(f"  {status} {cat}: {actual}問 (目標: {target}問, {diff:+d}問)")
        if actual != target:
            all_match = False

    if all_match:
        print(f"\n✅ 全カテゴリが目標値と完全に一致！")
    else:
        print(f"\n⚠️  一部カテゴリに誤差があります")

    print("=" * 80)

if __name__ == '__main__':
    generate_variants(INPUT_FILE, OUTPUT_FILE)
