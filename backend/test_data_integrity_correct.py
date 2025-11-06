#!/usr/bin/env python3
"""
正しいデータ整合性テスト - 基本検査を優先
品質テストはこの後
"""

import json
from collections import defaultdict

print("=" * 80)
print("【データ整合性テスト - 基本検査】")
print("=" * 80)

# 元データを読み込む
with open('backend/problems_final_500_complete.json', 'r') as f:
    problems = json.load(f)

print(f"\n【テスト1: 基本統計】")
print(f"  総問題数: {len(problems)}")

# テスト2: 重複検査
print(f"\n【テスト2: 重複検査 ← 最優先】")

problem_texts = [p.get('problem_text', '') for p in problems]
text_counts = defaultdict(int)
for text in problem_texts:
    text_counts[text] += 1

duplicates = {text: count for text, count in text_counts.items() if count > 1}
unique_problems = len(set(problem_texts))

print(f"  ❌ 重複問題: {len(duplicates)}種類")
print(f"  ❌ 一意な問題: {unique_problems}個")
print(f"  ❌ 重複率: {((len(problems) - unique_problems) / len(problems) * 100):.1f}%")

if duplicates:
    print(f"  ❌ 【FAIL】重複が存在 → データとして不可用")
    for text, count in sorted(duplicates.items(), key=lambda x: -x[1])[:5]:
        print(f"      [{count}回] {text[:50]}...")
else:
    print(f"  ✅ 【PASS】重複なし")

# テスト3: NULL値検査
print(f"\n【テスト3: NULL値検査】")

null_fields = defaultdict(int)
for i, p in enumerate(problems):
    if not p.get('problem_id'):
        null_fields['problem_id'] += 1
    if not p.get('problem_text'):
        null_fields['problem_text'] += 1
    if not p.get('correct_answer'):
        null_fields['correct_answer'] += 1
    if not p.get('explanation'):
        null_fields['explanation'] += 1

if null_fields:
    print(f"  ❌ NULL値検出:")
    for field, count in null_fields.items():
        print(f"      {field}: {count}件")
    print(f"  ❌ 【FAIL】欠落データあり")
else:
    print(f"  ✅ 【PASS】NULL値なし")

# テスト4: メタデータ完全性
print(f"\n【テスト4: メタデータ完全性検査】")

required_fields = ['problem_id', 'problem_text', 'correct_answer', 'options', 'explanation']
missing_field_count = defaultdict(int)

for p in problems:
    for field in required_fields:
        if field not in p or not p[field]:
            missing_field_count[field] += 1

if missing_field_count:
    print(f"  ❌ 必須フィールド欠落:")
    for field, count in missing_field_count.items():
        print(f"      {field}: {count}件")
    print(f"  ❌ 【FAIL】メタデータ不完全")
else:
    print(f"  ✅ 【PASS】全フィールド完全")

# テスト5: テーマ・カテゴリの整合性
print(f"\n【テスト5: テーマ・カテゴリ整合性】")

theme_set = set()
category_set = set()
missing_mapping = 0

for p in problems:
    theme = p.get('verified_theme')
    category = p.get('verified_category')

    if not theme or not category:
        missing_mapping += 1
    else:
        theme_set.add(theme)
        category_set.add(category)

print(f"  テーマ数: {len(theme_set)}")
print(f"  カテゴリ数: {len(category_set)}")
print(f"  マッピング未設定: {missing_mapping}問")

if missing_mapping > 0:
    print(f"  ❌ 【FAIL】{missing_mapping}問がマッピング未設定")
else:
    print(f"  ✅ 【PASS】全問マッピング完全")

# 結論
print(f"\n" + "=" * 80)
print("【結論】")
print("=" * 80)

if duplicates or missing_field_count or missing_mapping > 0:
    print(f"\n❌ 【データ品質: 不適切】")
    print(f"  このデータセットは本番環境に使用できません。")
    print(f"  以下の対応が必須：")
    print(f"  1. 重複問題の削除")
    print(f"  2. 欠落データの補完")
    print(f"  3. メタデータの完全性確認")
else:
    print(f"\n✅ 【データ品質: 適切】")
    print(f"  品質テストに進行可能")

EOF
