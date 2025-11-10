#!/usr/bin/env python3
"""
PCB問題をbackend/db/problems.jsonに統合
"""

import json
from pathlib import Path

def convert_difficulty(jp_difficulty):
    """日本語難易度を★に変換"""
    mapping = {
        '基礎': '★',
        '標準': '★★',
        '応用': '★★★'
    }
    return mapping.get(jp_difficulty, '★★')

def main():
    # 既存の問題を読み込み
    with open('backend/db/problems.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    existing_problems = existing_data.get('problems', existing_data)

    print(f'📊 既存問題数: {len(existing_problems)}')

    # 最大IDを取得
    max_id = max([p['problem_id'] for p in existing_problems])
    print(f'📌 最大ID: {max_id}')

    # PCB問題を読み込み
    pcb_problems = []
    for i in range(1, 8):
        file_path = Path(f'data/pcb_category{i}_questions.json')
        if not file_path.exists():
            print(f'⚠️  {file_path} が見つかりません')
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('questions', [])
            category_name = data.get('category', f'PCB Category {i}')

            for q in questions:
                pcb_problems.append({
                    'original_id': q.get('id'),
                    'problem_text': q.get('problem_text'),
                    'correct_answer': q.get('correct_answer'),
                    'explanation': q.get('explanation'),
                    'difficulty': q.get('difficulty'),
                    'category_name': category_name
                })

            print(f'  ✅ {category_name}: {len(questions)}問')

    print(f'\n📊 PCB問題総数: {len(pcb_problems)}')

    # PCB問題のIDを振り直し、フォーマットを統一
    next_id = max_id + 1
    unified_pcb = []

    for pcb_prob in pcb_problems:
        # correct_answerを bool に変換
        correct_str = pcb_prob['correct_answer']
        correct_bool = correct_str in ['○', '〇', '◯']
        answer_display = '〇' if correct_bool else '×'

        unified = {
            "problem_id": next_id,
            "statement": pcb_prob['problem_text'],
            "correct_answer": correct_bool,
            "answer_display": answer_display,
            "basis": pcb_prob['explanation'],
            "category": "pcb_management",
            "difficulty": convert_difficulty(pcb_prob['difficulty'])
        }

        unified_pcb.append(unified)
        next_id += 1

    # 全問題をマージ
    all_problems = existing_problems + unified_pcb

    print(f'\n🎯 合計問題数: {len(all_problems)}')

    # 難易度別統計
    difficulty_stats = {}
    category_stats = {}

    for p in all_problems:
        diff = p.get('difficulty', '★★')
        cat = p.get('category', 'other')
        difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1
        category_stats[cat] = category_stats.get(cat, 0) + 1

    print('\n📊 難易度別:')
    for diff in sorted(difficulty_stats.keys()):
        print(f'  {diff}: {difficulty_stats[diff]}問')

    print('\n📂 カテゴリ別:')
    for cat in sorted(category_stats.keys()):
        print(f'  {cat}: {category_stats[cat]}問')

    # 保存
    output_data = {
        'problems': all_problems,
        'metadata': {
            'total': len(all_problems),
            'sources': [
                '遊技機取扱主任者試験 総合模擬問題集.txt (230問)',
                'PCB管理試験問題 7カテゴリ (105問)'
            ],
            'version': '1.1',
            'last_updated': '2025-11-10'
        }
    }

    with open('backend/db/problems.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 保存完了: backend/db/problems.json ({len(all_problems)}問)')

if __name__ == "__main__":
    main()
