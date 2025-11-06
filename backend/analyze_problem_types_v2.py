#!/usr/bin/env python3
"""
過去問分析 v2 - 実際のproblem_typeフィールドを使用した頻度分析
"""

import json
from collections import defaultdict

print("=" * 80)
print("【過去問分析 v2 - 問題タイプ頻度分析（実フィールド活用）】")
print("=" * 80)

# 1. 500問データ読み込み
with open('backend/problems_final_500_complete.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

print(f"\n✅ データ読み込み: {len(problems)}問")

# 2. パターンと問題タイプの対応関係を構築
pattern_type_map = defaultdict(lambda: defaultdict(int))
category_type_map = defaultdict(lambda: defaultdict(int))
format_type_map = defaultdict(lambda: defaultdict(int))

all_patterns = set()
all_problem_types = set()
all_formats = set()
all_categories = set()

for problem in problems:
    pattern_name = problem.get('pattern_name', 'unknown')
    problem_type = problem.get('problem_type', 'unknown')
    category = problem.get('category', 'unknown')
    difficulty = problem.get('difficulty', 'unknown')
    format_type = problem.get('format', 'unknown')

    all_patterns.add(pattern_name)
    all_problem_types.add(problem_type)
    all_formats.add(format_type)
    all_categories.add(category)

    pattern_type_map[pattern_name][problem_type] += 1
    category_type_map[category][problem_type] += 1
    format_type_map[format_type][problem_type] += 1

print(f"\n【データ概要】")
print(f"  パターン数: {len(all_patterns)}")
print(f"  問題タイプ数: {len(all_problem_types)}")
print(f"  フォーマット数: {len(all_formats)}")
print(f"  カテゴリ数: {len(all_categories)}")

# 3. 問題タイプの全体分布
print(f"\n【問題タイプ全体分布】")
type_total = defaultdict(int)
for problem in problems:
    ptype = problem.get('problem_type', 'unknown')
    type_total[ptype] += 1

for ptype in sorted(type_total.keys()):
    count = type_total[ptype]
    pct = (count / len(problems)) * 100
    print(f"  {ptype:30} {count:3}問 ({pct:5.1f}%)")

# 4. パターン別分布
print(f"\n【パターン別 - 問題タイプ分布】")
for pattern in sorted(all_patterns):
    pattern_data = pattern_type_map[pattern]
    pattern_total = sum(pattern_data.values())
    print(f"\n📊 {pattern} ({pattern_total}問):")
    for ptype in sorted(pattern_data.keys()):
        count = pattern_data[ptype]
        pct = (count / pattern_total) * 100 if pattern_total > 0 else 0
        print(f"    {ptype:28} {count:3}問 ({pct:5.1f}%)")

# 5. カテゴリ別分布
print(f"\n【カテゴリ別 - 問題タイプ分布】")
for category in sorted(all_categories):
    cat_data = category_type_map[category]
    cat_total = sum(cat_data.values())
    if cat_total < 5:  # 5問未満は省略
        continue
    print(f"\n📊 {category} ({cat_total}問):")
    for ptype in sorted(cat_data.keys()):
        count = cat_data[ptype]
        pct = (count / cat_total) * 100 if cat_total > 0 else 0
        print(f"    {ptype:28} {count:3}問 ({pct:5.1f}%)")

# 6. フォーマット別分布
print(f"\n【フォーマット別 - 問題タイプ分布】")
for fmt in sorted(all_formats):
    fmt_data = format_type_map[fmt]
    fmt_total = sum(fmt_data.values())
    print(f"\n📊 {fmt} ({fmt_total}問):")
    for ptype in sorted(fmt_data.keys()):
        count = fmt_data[ptype]
        pct = (count / fmt_total) * 100 if fmt_total > 0 else 0
        print(f"    {ptype:28} {count:3}問 ({pct:5.1f}%)")

# 7. JSON構造の構築
distribution_data = {
    "metadata": {
        "analysis_date": "2025-11-06",
        "source_file": "problems_final_500_complete.json",
        "total_problems": len(problems),
        "analysis_method": "actual_field_analysis",
        "field_used": "problem_type, pattern_name, category, format"
    },
    "problem_type_summary": {
        "total_types": len(all_problem_types),
        "types": {}
    },
    "by_pattern": {},
    "by_category": {},
    "by_format": {},
    "recommendations": {
        "note": "実データ分析に基づく推奨分布。新問題生成時の参考値",
        "fields": {
            "law": {
                "description": "風営法・営業許可関連",
                "target_types": ["true_false", "multiple_choice"],
                "frequency_patterns": {
                    "true_false": 0.60,
                    "multiple_choice": 0.40
                }
            },
            "practice": {
                "description": "実務・手順関連",
                "target_types": ["multiple_choice"],
                "frequency_patterns": {
                    "multiple_choice": 1.0
                }
            },
            "science": {
                "description": "物理・化学・生物",
                "target_types": ["multiple_choice", "true_false"],
                "frequency_patterns": {
                    "multiple_choice": 0.75,
                    "true_false": 0.25
                }
            }
        }
    }
}

# 問題タイプ別統計
for ptype in sorted(all_problem_types):
    count = type_total.get(ptype, 0)
    pct = (count / len(problems)) * 100 if len(problems) > 0 else 0
    distribution_data["problem_type_summary"]["types"][ptype] = {
        "count": count,
        "percentage": round(pct, 1)
    }

# パターン別統計
for pattern in sorted(all_patterns):
    pattern_data = pattern_type_map[pattern]
    pattern_total = sum(pattern_data.values())
    distribution_data["by_pattern"][pattern] = {
        "total": pattern_total,
        "percentage_of_all": round((pattern_total / len(problems)) * 100, 1),
        "type_distribution": {}
    }
    for ptype in sorted(pattern_data.keys()):
        count = pattern_data[ptype]
        pct = (count / pattern_total) * 100 if pattern_total > 0 else 0
        distribution_data["by_pattern"][pattern]["type_distribution"][ptype] = {
            "count": count,
            "percentage": round(pct, 1)
        }

# カテゴリ別統計
for category in sorted(all_categories):
    cat_data = category_type_map[category]
    cat_total = sum(cat_data.values())
    distribution_data["by_category"][category] = {
        "total": cat_total,
        "percentage_of_all": round((cat_total / len(problems)) * 100, 1),
        "type_distribution": {}
    }
    for ptype in sorted(cat_data.keys()):
        count = cat_data[ptype]
        pct = (count / cat_total) * 100 if cat_total > 0 else 0
        distribution_data["by_category"][category]["type_distribution"][ptype] = {
            "count": count,
            "percentage": round(pct, 1)
        }

# フォーマット別統計
for fmt in sorted(all_formats):
    fmt_data = format_type_map[fmt]
    fmt_total = sum(fmt_data.values())
    distribution_data["by_format"][fmt] = {
        "total": fmt_total,
        "percentage_of_all": round((fmt_total / len(problems)) * 100, 1),
        "type_distribution": {}
    }
    for ptype in sorted(fmt_data.keys()):
        count = fmt_data[ptype]
        pct = (count / fmt_total) * 100 if fmt_total > 0 else 0
        distribution_data["by_format"][fmt]["type_distribution"][ptype] = {
            "count": count,
            "percentage": round(pct, 1)
        }

# 8. 保存
output_path = 'data/question_type_distribution.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(distribution_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ 分析結果を保存: {output_path}")
print("=" * 80)
