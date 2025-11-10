#!/usr/bin/env python3
"""
遊技機取扱主任者試験 総合模擬問題集.txt を JSON に変換
"""

import json
import re
from pathlib import Path

def parse_question_file(file_path):
    """テキストファイルから問題をパース"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    problems = []

    # カテゴリヘッダーを検出
    category_pattern = r'####\s+([IVXLC]+)\.\s+(.+?)（問題\s+\d+\s+〜\s+\d+）'

    # カテゴリを抽出
    categories = {}
    for match in re.finditer(category_pattern, content):
        roman_num, category_name = match.groups()
        categories[match.start()] = category_name.strip()

    # 問題を分割（より柔軟なパターン）
    # 数字 + ピリオドで始まり、次の数字 + ピリオドまたはファイル末尾まで
    problem_blocks = re.split(r'\n(?=\d+\.\s+\*\*問題文:)', content)

    for block in problem_blocks:
        block = block.strip()
        if not block:
            continue

        # 問題ID抽出
        id_match = re.match(r'(\d+)\.\s+\*\*問題文:\*\*', block)
        if not id_match:
            continue

        problem_id = int(id_match.group(1))

        # 問題文抽出
        text_match = re.search(r'\*\*問題文:\*\*\s+\*\*(.+?)\*\*', block, re.DOTALL)
        if not text_match:
            continue
        problem_text = text_match.group(1).strip()

        # 正答抽出
        answer_match = re.search(r'\*\*正答:\*\*\s+([〇✕○×])', block)
        if not answer_match:
            continue
        correct_answer_char = answer_match.group(1)
        correct_bool = correct_answer_char in ['〇', '○']
        answer_display = '〇' if correct_bool else '×'

        # 根拠抽出
        basis_match = re.search(r'\*\*根拠:\*\*\s+(.+)', block, re.DOTALL)
        if not basis_match:
            continue
        explanation = basis_match.group(1).strip()

        # カテゴリ特定（問題の位置から）
        problem_position = content.find(block)
        current_category = ""
        for cat_pos in sorted(categories.keys(), reverse=True):
            if problem_position > cat_pos:
                current_category = categories[cat_pos]
                break

        # 難易度を推定（簡易版）
        if any(keyword in problem_text for keyword in ['とは', 'いう', '定義', '意味']):
            difficulty = '★'
        elif any(keyword in problem_text for keyword in ['場合', 'とき', '際', '条件']):
            difficulty = '★★'
        else:
            difficulty = '★★'

        problem = {
            "problem_id": problem_id,
            "statement": problem_text,
            "correct_answer": correct_bool,
            "answer_display": answer_display,
            "basis": explanation,
            "category": map_category(current_category),
            "difficulty": difficulty
        }

        problems.append(problem)

    return problems

def map_category(category_text):
    """カテゴリ名を英語キーにマッピング"""
    category_map = {
        "制度、試験及び資格認定に関する事項": "qualification_system",
        "遊技産業の健全化等に関する事項": "industry_health",
        "風俗営業等の規制及び業務の適正化等に関する法律": "fuei_law",
        "風俗営業等の規制及び業務の適正化等に関する法律施行規則": "fuei_regulations",
        "遊技機の認定及び型式の検定等に関する規則": "machine_certification",
        "遊技機の構造、機能等": "machine_structure",
        "不正改造の実際及び不正改造の防止に関する事項": "fraud_prevention"
    }

    for key, value in category_map.items():
        if key in category_text:
            return value

    return "other"

def main():
    input_file = Path("sources/遊技機取扱主任者試験 総合模擬問題集.txt")
    output_file = Path("backend/db/problems.json")

    print(f"📖 読み込み中: {input_file}")
    problems = parse_question_file(input_file)

    print(f"✅ {len(problems)}問をパース完了")

    # 問題IDでソート
    problems.sort(key=lambda x: x['problem_id'])

    # JSONに出力
    output_data = {
        "problems": problems,
        "metadata": {
            "total": len(problems),
            "source": "遊技機取扱主任者試験 総合模擬問題集.txt",
            "version": "1.0",
            "last_updated": "2025-11-10"
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"💾 保存完了: {output_file}")
    print(f"📊 総問題数: {len(problems)}")

    # 統計情報
    categories = {}
    difficulties = {}
    for p in problems:
        cat = p.get('category', 'unknown')
        diff = p.get('difficulty', '★★')
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\n📈 カテゴリ別:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}問")

    print("\n📊 難易度別:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}問")

if __name__ == "__main__":
    main()
