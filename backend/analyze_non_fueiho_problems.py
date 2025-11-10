#!/usr/bin/env python3
"""
風営法・風営法施行規則に含まれていない問題を特定（basis フィールド分析版）
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    base_dir = Path(__file__).parent.parent
    problems_file = base_dir / "backend" / "db" / "problems.json"

    with open(problems_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        problems = data.get('problems', [])

    print(f"✅ 問題数: {len(problems)}問\n")

    # 風営法・施行規則に基づく問題 vs それ以外
    fueiho_problems = []
    non_fueiho_problems = []

    for p in problems:
        basis = p.get('basis', '')
        statement = p.get('statement', '')

        # 風営法・施行規則のキーワード
        is_fueiho = any(keyword in basis for keyword in [
            '風営法', '風俗営業', '法第', '施行規則', '規則第', '施行令'
        ])

        # 業界団体規制のキーワード
        is_industry = any(keyword in basis for keyword in [
            '規程', '要領', '要綱', '日遊協', '実施要領', '登録規程',
            '中古遊技機流通', '不正防止対策', '業務委託'
        ])

        if is_industry and not is_fueiho:
            non_fueiho_problems.append(p)
        elif is_fueiho:
            fueiho_problems.append(p)
        else:
            # その他（特定困難）
            non_fueiho_problems.append(p)

    print(f"🔵 風営法・施行規則に基づく問題: {len(fueiho_problems)}問")
    print(f"🟠 業界団体の自主規制のみに基づく問題: {len(non_fueiho_problems)}問")
    print()

    # カテゴリ別集計
    by_category = defaultdict(list)
    for p in non_fueiho_problems:
        by_category[p.get('category', 'unknown')].append(p)

    print("=" * 70)
    print("📋 風営法・施行規則に含まれていない問題（246問中）")
    print("=" * 70)
    print()

    category_names = {
        'qualification_system': '資格制度',
        'supervisor_duties_and_guidance': '主任者職務・指導',
        'administrative_procedures_and_penalties': '行政手続・罰則',
        'business_regulation_and_obligations': '営業規制・義務',
        'game_machine_technical_standards': '遊技機技術基準'
    }

    total = 0
    for category, category_problems in sorted(by_category.items()):
        cat_name = category_names.get(category, category)
        print(f"\n## {cat_name}（{len(category_problems)}問）\n")

        for p in category_problems:
            problem_id = p.get('problem_id', '?')
            statement = p.get('statement', '')[:100]
            basis = p.get('basis', '')[:120]

            print(f"**問{problem_id}**: {statement}...")
            print(f"  根拠: {basis}...")
            print()

        total += len(category_problems)

    print("\n" + "=" * 70)
    print(f"合計: {total}問 / {len(problems)}問")
    print("=" * 70)

    # レポート保存
    lines = [
        "# 風営法・風営法施行規則に含まれていない問題一覧",
        "",
        f"**分析対象**: {len(problems)}問",
        f"**風営法・施行規則に基づく問題**: {len(fueiho_problems)}問",
        f"**業界団体の自主規制のみに基づく問題**: {len(non_fueiho_problems)}問",
        "",
        "---",
        ""
    ]

    for category, category_problems in sorted(by_category.items()):
        cat_name = category_names.get(category, category)
        lines.append(f"## {cat_name}（{len(category_problems)}問）")
        lines.append("")

        for p in category_problems:
            problem_id = p.get('problem_id', '?')
            statement = p.get('statement', '')
            correct = '〇' if p.get('correct_answer') else '✕'
            basis = p.get('basis', '')

            lines.append(f"### 問{problem_id} [{correct}]")
            lines.append(f"**問題**: {statement}")
            lines.append(f"**根拠**: {basis}")
            lines.append("")

    # 保存
    output_file = base_dir / "backend" / "data" / "non_fueiho_problems_detailed.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n✅ 詳細レポート保存: {output_file}")


if __name__ == "__main__":
    main()
