#!/usr/bin/env python3
"""
過去問分析 - 問題タイプ頻度表の作成
500問データから問題タイプの出現パターンを分析

問題タイプ分類基準：
- 法令: 判断型, 定義型, 条文該当型, その他
- 実務: 応用型, 手順型, 判断型, その他
- 物理・化学・生物: 理由型, 計算型, 定義型, その他
"""

import json
import re
from collections import defaultdict

print("=" * 80)
print("【過去問分析 - 問題タイプ頻度分析】")
print("=" * 80)

# 1. 500問データ読み込み
with open('backend/problems_final_500_complete.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

print(f"\n✅ データ読み込み: {len(problems)}問")

# 2. 問題テキストから問題タイプを推定する関数
def detect_problem_type(problem_text, category=None):
    """
    問題文から問題タイプを推定
    """
    text = problem_text.lower()

    # キーワードベースの検出

    # 判断型: 「正しい」「誤り」「適切」
    if any(kw in text for kw in ['正しい', '誤り', '適切', '違反', '該当', '認められ']):
        # 法令系かの判定
        if any(kw in text for kw in ['営業', '許可', '検定', '禁止']):
            return 'law_judgment'
        else:
            return 'judgment'

    # 定義型: 「とは」「意味」「定義」
    if any(kw in text for kw in ['とは', '意味', '定義', 'いう']):
        if any(kw in text for kw in ['営業', '許可', '検定', '禁止']):
            return 'law_definition'
        else:
            return 'definition'

    # 手順型: 「順序」「手順」「流れ」「手続き」
    if any(kw in text for kw in ['順序', '手順', '流れ', '手続き', '進め', 'どの順']):
        return 'procedure'

    # 応用型: 「~した場合」「対応」「措置」
    if any(kw in text for kw in ['した場合', '対応', '措置', 'するべき', '求め']):
        return 'application'

    # 理由型: 「なぜ」「理由」「原因」「わけ」
    if any(kw in text for kw in ['なぜ', '理由', '原因', 'わけ', 'ため']):
        return 'reason'

    # 計算型: 「計算」「何個」「何台」「費用」「金額」
    if any(kw in text for kw in ['計算', '何個', '何台', '費用', '金額', '合計', '除く']):
        return 'calculation'

    # 組合せ型: 「組合せ」「選び」「選べ」
    if any(kw in text for kw in ['組合', '選び', '選べ', '組み合わせ']):
        return 'combination'

    # デフォルト
    return 'other'


# 3. 各問題をカテゴリ分類（verified_categoryを使用）
def get_field_category(verified_category):
    """
    verified_categoryから分野を判定
    """
    category = verified_category.lower() if verified_category else 'unknown'

    if any(kw in category for kw in ['営業', '許可', '型式', '禁止', '停止', '検定']):
        return 'law'
    elif any(kw in category for kw in ['実務', '点検', '管理', '設置', '保守']):
        return 'practice'
    elif any(kw in category for kw in ['物理', '化学', '生物', '機械', '電気']):
        return 'science'
    else:
        return 'other'


# 4. 分析実行
analysis = defaultdict(lambda: defaultdict(int))
field_distribution = defaultdict(int)
total_by_type = defaultdict(int)

for i, problem in enumerate(problems):
    problem_text = problem.get('problem_text', '')
    verified_category = problem.get('verified_category', 'unknown')

    if not problem_text:
        continue

    # 問題タイプ推定
    ptype = detect_problem_type(problem_text, verified_category)

    # 分野判定
    field = get_field_category(verified_category)

    analysis[field][ptype] += 1
    field_distribution[field] += 1
    total_by_type[ptype] += 1

print(f"\n【分野別集計】")
for field in sorted(field_distribution.keys()):
    count = field_distribution[field]
    pct = (count / len(problems)) * 100
    print(f"  {field:15} {count:3}問 ({pct:5.1f}%)")

print(f"\n【分野別 - 問題タイプ分布】\n")

# 5. 出力用JSON構造を構築
question_type_distribution = {
    "metadata": {
        "analysis_date": "2025-11-06",
        "source_data": "problems_final_500_complete.json",
        "total_problems": len(problems),
        "analysis_method": "keyword-based_type_detection",
        "fields": list(sorted(field_distribution.keys()))
    },
    "distributions": {}
}

for field in sorted(analysis.keys()):
    field_data = analysis[field]
    total = field_distribution[field]

    print(f"📊 {field}分野 ({total}問):")

    # パーセンテージ計算
    field_dist = {}
    for ptype in sorted(field_data.keys()):
        count = field_data[ptype]
        pct = (count / total * 100) if total > 0 else 0
        field_dist[ptype] = {
            "count": count,
            "percentage": round(pct, 1)
        }
        print(f"  {ptype:20} {count:3}問 ({pct:5.1f}%)")

    question_type_distribution["distributions"][field] = field_dist
    print()

# 6. サマリー統計
print(f"【全体 - 問題タイプ統計】")
for ptype in sorted(total_by_type.keys()):
    count = total_by_type[ptype]
    pct = (count / len(problems) * 100)
    print(f"  {ptype:20} {count:3}問 ({pct:5.1f}%)")

# 7. 推奨頻度パターン（実装計画参考値との比較）
print(f"\n【推奨パターン vs 実績】\n")

print("法令分野（推奨: 判断型50%, 定義型30%, その他20%）")
if 'law' in analysis:
    law_total = field_distribution['law']
    for ptype in ['law_judgment', 'law_definition', 'other']:
        if ptype in analysis['law']:
            actual = (analysis['law'][ptype] / law_total * 100)
        else:
            actual = 0
        print(f"  {ptype:20} {actual:5.1f}%")
print()

print("実務分野（推奨: 応用型60%, 手順型40%）")
if 'practice' in analysis:
    practice_total = field_distribution['practice']
    for ptype in ['application', 'procedure']:
        if ptype in analysis['practice']:
            actual = (analysis['practice'][ptype] / practice_total * 100)
        else:
            actual = 0
        print(f"  {ptype:20} {actual:5.1f}%")
print()

print("科学分野（推奨: 理由型50%, 計算型30%, その他20%）")
if 'science' in analysis:
    science_total = field_distribution['science']
    for ptype in ['reason', 'calculation', 'other']:
        if ptype in analysis['science']:
            actual = (analysis['science'][ptype] / science_total * 100)
        else:
            actual = 0
        print(f"  {ptype:20} {actual:5.1f}%")

# 8. JSON保存
output_path = 'data/question_type_distribution.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(question_type_distribution, f, indent=2, ensure_ascii=False)

print(f"\n✅ 分析結果を保存: {output_path}")
print("=" * 80)
