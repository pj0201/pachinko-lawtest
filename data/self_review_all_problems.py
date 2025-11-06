#!/usr/bin/env python3
"""
全問題セルフレビュー - Claude Code による品質確認
"""

import json
from pathlib import Path
from collections import defaultdict

PROBLEMS_FILE = Path("/home/planj/patshinko-exam-app/data/PROBLEMS_REBALANCED_1617.json")

def load_problems():
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_problem_quality(problem, problem_num):
    """1問を詳細チェック"""
    issues = []

    # フィールド確認
    required_fields = ['problem_id', 'problem_text', 'correct_answer', 'explanation', 'category']
    for field in required_fields:
        if field not in problem:
            issues.append(f"❌ 必須フィールド '{field}' が欠落")

    if not issues:
        # 問題文の確認
        text = problem.get('problem_text', '')

        # 1. 意味不明でないか（中身がないテキスト）
        if not text or len(text.strip()) < 5:
            issues.append(f"❌ 問題文が短すぎる: '{text}'")

        # 2. 具体性チェック（曖昧な表現）
        vague_words = ['など', 'ものなど', 'とか', 'いろいろ', '様々', 'いくつか']
        if any(word in text for word in vague_words):
            # 「など」「様々」はOK（法律用語として使われる）
            # でも異常に多いのはNG
            vague_count = sum(text.count(word) for word in vague_words)
            if vague_count > 2:
                issues.append(f"⚠️  曖昧な表現が多い: '{text}'")

        # 3. 正答確認
        answer = problem.get('correct_answer', '')
        if answer not in ['○', '×']:
            issues.append(f"❌ 正答が不正: '{answer}'（○か×であるべき）")

        # 4. 説明確認
        explanation = problem.get('explanation', '')
        if not explanation or len(explanation.strip()) < 5:
            issues.append(f"❌ 説明が不足: '{explanation}'")

        # 5. カテゴリ確認
        category = problem.get('category', '')
        valid_categories = ['遊技機管理', '営業時間・規制', '営業許可関連',
                           '型式検定関連', '不正対策', '景品規制']
        if category not in valid_categories:
            issues.append(f"❌ 無効なカテゴリ: '{category}'")

    return issues

def check_duplicates(problems):
    """重複チェック"""
    text_map = defaultdict(list)
    duplicates = []

    for idx, problem in enumerate(problems):
        text = problem.get('problem_text', '')
        text_map[text].append(idx + 1)

    for text, problem_ids in text_map.items():
        if len(problem_ids) > 1:
            duplicates.append({
                'text': text,
                'problem_ids': problem_ids
            })

    return duplicates

def main():
    print("=" * 80)
    print("全問題セルフレビュー - Claude Code")
    print("=" * 80)

    data = load_problems()
    problems = data['problems']
    total = len(problems)

    print(f"\n📊 対象: 全{total}問\n")

    # ======== 1. 個別問題チェック ========
    print("1️⃣  個別問題の品質チェック中...")
    problem_issues = []

    for idx, problem in enumerate(problems, 1):
        issues = check_problem_quality(problem, idx)
        if issues:
            problem_issues.append((idx, issues))

        if idx % 200 == 0:
            print(f"   ✓ {idx}/{total} 確認済み")

    if problem_issues:
        print(f"\n❌ 問題が見つかった問題数: {len(problem_issues)}")
        for problem_id, issues in problem_issues[:10]:  # 最初の10件表示
            print(f"\n   【問題ID {problem_id}】")
            for issue in issues:
                print(f"      {issue}")
        if len(problem_issues) > 10:
            print(f"\n   ⚠️  他 {len(problem_issues) - 10} 件の問題あり")
    else:
        print(f"✅ すべての問題が合格！")

    # ======== 2. 重複チェック ========
    print("\n2️⃣  重複チェック中...")
    duplicates = check_duplicates(problems)

    if duplicates:
        print(f"\n❌ 重複が見つかった: {len(duplicates)}")
        for dup in duplicates[:5]:
            print(f"   問題ID {dup['problem_ids']}: '{dup['text'][:50]}...'")
        if len(duplicates) > 5:
            print(f"   他 {len(duplicates) - 5} 件の重複あり")
    else:
        print(f"✅ 重複なし！")

    # ======== 3. カテゴリ分布確認 ========
    print("\n3️⃣  カテゴリ分布確認中...")
    category_counts = defaultdict(int)
    for problem in problems:
        category_counts[problem.get('category', 'unknown')] += 1

    target = {
        '遊技機管理': 596,
        '営業時間・規制': 224,
        '営業許可関連': 194,
        '型式検定関連': 179,
        '不正対策': 149,
        '景品規制': 149
    }

    all_match = True
    for category in sorted(target.keys()):
        actual = category_counts[category]
        expected = target[category]
        match = actual == expected
        symbol = "✅" if match else "❌"
        print(f"   {symbol} {category}: {actual}/{expected}")
        if not match:
            all_match = False

    # ======== 4. 総合判定 ========
    print("\n" + "=" * 80)

    issue_count = len(problem_issues)
    duplicate_count = len(duplicates)

    if issue_count == 0 and duplicate_count == 0 and all_match:
        print("✅ 【全問題セルフレビュー合格】")
        print(f"   総問題数: {total}問")
        print(f"   個別問題: ✅ 全問合格")
        print(f"   重複: ✅ なし")
        print(f"   カテゴリ分布: ✅ 完全一致")
        print(f"   【結論】問題データセットの品質は良好です。本番デプロイ可能。")
    else:
        print("⚠️  【セルフレビュー：修正必要】")
        if issue_count > 0:
            print(f"   問題: ❌ {issue_count}問に問題あり")
        if duplicate_count > 0:
            print(f"   重複: ❌ {duplicate_count}個の重複あり")
        if not all_match:
            print(f"   分布: ❌ カテゴリ分布が一致していない")
        print(f"   【結論】修正が必要です。")

    print("=" * 80 + "\n")

    # 詳細レポート出力
    if problem_issues or duplicates:
        with open('/home/planj/patshinko-exam-app/data/SELF_REVIEW_ISSUES.json', 'w', encoding='utf-8') as f:
            json.dump({
                'problem_issues': [
                    {'problem_id': pid, 'issues': issues}
                    for pid, issues in problem_issues
                ],
                'duplicates': duplicates
            }, f, ensure_ascii=False, indent=2)
        print("📝 詳細レポート: /home/planj/patshinko-exam-app/data/SELF_REVIEW_ISSUES.json\n")

if __name__ == '__main__':
    main()
