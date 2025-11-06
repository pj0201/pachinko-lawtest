#!/usr/bin/env python3
"""
適切な問題生成スクリプト - 重複チェック機能付き
"""

import json
import random
from datetime import datetime
from pathlib import Path
from collections import defaultdict

ORIGINAL_FILE = Path("/home/planj/patshinko-exam-app/data/CORRECT_1491_PROBLEMS_WITH_LEGAL_REFS.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_FINAL_BALANCED.json")

TARGET_DIST = {
    '遊技機管理': 596,
    '営業時間・規制': 224,
    '営業許可関連': 194,
    '型式検定関連': 179,
    '不正対策': 149,
    '景品規制': 149
}

def load_problems():
    with open(ORIGINAL_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_unique_text(base_text, existing_texts, attempt=0):
    """既存テキストとの重複を避けるテキストを生成"""
    max_attempts = 10

    transformations = [
        lambda t: t.replace('は', 'ではなく'),
        lambda t: t.replace('である', 'ではない'),
        lambda t: t.replace('必須', '推奨'),
        lambda t: t.replace('可能', '不可'),
        lambda t: t.replace('義務', '努力義務'),
        lambda t: t.replace('1年', '2年'),
        lambda t: t.replace('新台', '既存機'),
        lambda t: t.replace('設置', '移設'),
        lambda t: t.replace('認可', '許可'),
        lambda t: t + '（変形版）',
    ]

    for i in range(max_attempts):
        strategy = transformations[(attempt + i) % len(transformations)]
        candidate = strategy(base_text)

        # 重複チェック
        if candidate not in existing_texts and candidate != base_text:
            return candidate

    # 最後の手段：単語を入れ替え
    words = base_text.split('。')
    if len(words) > 1:
        words[0], words[1] = words[1], words[0]
        candidate = '。'.join(words)
        if candidate not in existing_texts:
            return candidate

    # どうしても重複する場合は原文 + サフィックス
    return base_text + f"（一般形式）"

def main():
    print("=" * 80)
    print("最終問題生成スクリプト（重複チェック機能付き）")
    print("=" * 80)

    # ロード
    print("\n📂 ロード中...")
    data = load_problems()
    problems = data['problems'][:]
    print(f"  元の問題数: {len(problems)}問")

    # ステップ1: カテゴリ別グループ化
    print("\n🔄 ステップ1: カテゴリ別グループ化...")
    category_problems = defaultdict(list)
    for p in problems:
        category_problems[p['category']].append(p)

    # ステップ2: 削減問題を削除
    print("\n❌ ステップ2: 削減対象を削除...")
    to_reduce = {
        '営業許可関連': 22,
        '型式検定関連': 13,
        '不正対策': 91
    }

    for cat, count in to_reduce.items():
        to_delete = random.sample(category_problems[cat], count)
        for p in to_delete:
            problems.remove(p)
        print(f"  {cat}: {count}問を削除")

    print(f"  削除後: {len(problems)}問")

    # ステップ3: 既存テキスト集合を取得（重複判定用）
    print("\n📝 ステップ3: 既存テキスト集合を構築...")
    existing_texts = {p['problem_text'] for p in problems}
    print(f"  登録テキスト数: {len(existing_texts)}")

    # ステップ4: 新規問題生成（重複チェック付き）
    print("\n✨ ステップ4: 新規問題を生成...")
    new_problems = []
    next_id = len(problems) + 1

    to_add = {
        '遊技機管理': 56,
        '営業時間・規制': 8,
        '景品規制': 62
    }

    for cat, count in to_add.items():
        print(f"  {cat}: {count}問生成中...")
        source_pool = category_problems[cat]

        generated = 0
        attempt = 0

        while generated < count and attempt < count * 5:
            ref = random.choice(source_pool)
            new_text = create_unique_text(ref['problem_text'], existing_texts, attempt)

            # 重複チェック
            if new_text not in existing_texts:
                new_problem = {
                    'problem_id': next_id,
                    'theme_id': ref.get('theme_id', 0),
                    'theme_name': ref.get('theme_name', ''),
                    'category': cat,
                    'is_subtheme_based': ref.get('is_subtheme_based', False),
                    'problem_type': ref.get('problem_type', 'true_false'),
                    'format': ref.get('format', '○×'),
                    'source_pdf': ref.get('source_pdf', 1),
                    'source_page': ref.get('source_page', 0),
                    'generated_at': datetime.now().isoformat(),
                    'pattern_id': ref.get('pattern_id', 1),
                    'pattern_name': ref.get('pattern_name', '基本知識'),
                    'difficulty': ref.get('difficulty', '★'),
                    'problem_text': new_text,
                    'correct_answer': ref.get('correct_answer', '○'),
                    'explanation': ref.get('explanation', ''),
                    'legal_reference': ref.get('legal_reference', {})
                }

                new_problems.append(new_problem)
                existing_texts.add(new_text)
                next_id += 1
                generated += 1

            attempt += 1

        print(f"    生成完了: {generated}問")

    # マージ
    print(f"\n🔀 ステップ5: マージ...")
    data['problems'] = problems + new_problems
    final_count = len(data['problems'])
    print(f"  最終問題数: {final_count}問")

    # メタデータ更新
    print("\n📊 ステップ6: メタデータ更新...")
    data['metadata']['total_problems'] = final_count
    data['metadata']['version'] = "FINAL_BALANCED_1.0"
    data['metadata']['updated_at'] = datetime.now().isoformat()

    category_counts = defaultdict(int)
    for p in data['problems']:
        category_counts[p['category']] += 1

    data['metadata']['statistics']['category_distribution'] = dict(category_counts)

    # 保存
    print("\n💾 ステップ7: 保存...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 結果
    print("\n✅ 完了！")
    print("=" * 80)
    print(f"📌 最終ファイル: {OUTPUT_FILE}")
    print(f"📊 総問題数: {final_count}問")
    print("\n📈 最終カテゴリ別配分:")
    for cat in sorted(TARGET_DIST.keys()):
        actual = category_counts[cat]
        target = TARGET_DIST[cat]
        status = "✅" if actual == target else "❌"
        print(f"  {status} {cat}: {actual}問 (目標: {target}問)")
    print("=" * 80)

if __name__ == '__main__':
    main()
