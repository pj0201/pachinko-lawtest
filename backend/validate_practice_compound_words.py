#!/usr/bin/env python3
"""
Task 4.3: 実務分野複合語検証スクリプト

生成された問題に対し、複合語が正確に扱われているか検証
"""

import json
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 4.3: 実務分野複合語検証】")
print("=" * 80)

# 1. 複合語辞書を読み込む
print("\n✅ ステップ1: 複合語辞書を読み込む")

with open("data/compound_words/compound_words_dictionary.json", 'r', encoding='utf-8') as f:
    compound_dict = json.load(f)

compound_words = [
    cw['word'] for cw in compound_dict.get('compound_words', [])
]

print(f"  読み込み完了: {len(compound_words)}個の複合語")
print(f"  主要複合語: {', '.join(compound_words[:10])}...")

# 2. デモ問題を読み込む
print("\n✅ ステップ2: デモ問題を読み込む")

try:
    with open("output/practice_domain_50_demo.json", 'r', encoding='utf-8') as f:
        demo_data = json.load(f)

    sample_problems = demo_data.get('sample_problems', [])
    print(f"  読み込み完了: {len(sample_problems)}個の問題")
except Exception as e:
    print(f"  エラー: {e}")
    sample_problems = []

# 3. 複合語検証ロジックを定義
print("\n✅ ステップ3: 複合語検証ロジックを定義")

def check_compound_word_integrity(text, compound_words):
    """
    テキストに複合語が正確に含まれているか検証
    複合語が分割されていないか確認
    """
    issues = []
    found_compounds = []

    for compound in compound_words:
        # 複合語が含まれているかチェック
        if compound in text:
            found_compounds.append(compound)

            # 分割パターンをチェック（スペース、改行など）
            split_pattern = " ".join(list(compound))
            if split_pattern in text:
                issues.append(f"❌ 複合語分割エラー: {compound} → {split_pattern}")

    return {
        "found_compounds": found_compounds,
        "issues": issues,
        "integrity_score": 1.0 if not issues else 0.5
    }

def extract_keywords(text, compound_words):
    """テキストから複合語キーワードを自動抽出"""
    found = []
    for compound in compound_words:
        if compound in text:
            found.append(compound)
    return found

# 4. 各問題を検証
print("\n✅ ステップ4: 各問題を検証")

validation_results = []

for i, problem in enumerate(sample_problems, 1):
    problem_id = problem.get('problem_id', f'unknown_{i}')
    problem_text = problem.get('problem_text', '')
    claimed_keywords = problem.get('compound_words_used', [])

    # 複合語検証
    integrity = check_compound_word_integrity(problem_text, compound_words)

    # キーワード抽出
    extracted = extract_keywords(problem_text, compound_words)

    # 差分分析
    missing = set(claimed_keywords) - set(extracted)
    unexpected = set(extracted) - set(claimed_keywords)

    result = {
        "problem_id": problem_id,
        "problem_text_preview": problem_text[:60] + "..." if len(problem_text) > 60 else problem_text,
        "claimed_keywords": claimed_keywords,
        "extracted_keywords": extracted,
        "integrity_issues": integrity['issues'],
        "missing_keywords": list(missing),
        "unexpected_keywords": list(unexpected),
        "integrity_score": integrity['integrity_score'],
        "validation_status": "✓ PASS" if not integrity['issues'] else "✗ FAIL"
    }

    validation_results.append(result)

    # 詳細表示
    print(f"\n  【問題 {i}: {problem_id}】")
    print(f"    テキスト: {result['problem_text_preview']}")
    print(f"    宣言キーワード: {', '.join(claimed_keywords)}")
    print(f"    抽出キーワード: {', '.join(extracted)}")
    if integrity['issues']:
        for issue in integrity['issues']:
            print(f"    {issue}")
    else:
        print(f"    ✓ 複合語検証: OK")
    print(f"    ステータス: {result['validation_status']}")

# 5. 統計集計
print("\n✅ ステップ5: 統計集計")

total_problems = len(validation_results)
passed = sum(1 for r in validation_results if r['integrity_score'] == 1.0)
failed = total_problems - passed

print(f"""
  総問題数: {total_problems}個
  合格: {passed}個 ({(passed/total_problems)*100:.1f}%)
  不合格: {failed}個 ({(failed/total_problems)*100:.1f}%)
""")

# 複合語別の統計
compound_usage = defaultdict(int)
for result in validation_results:
    for keyword in result['extracted_keywords']:
        compound_usage[keyword] += 1

print(f"  【複合語別使用頻度】")
for compound, count in sorted(compound_usage.items(), key=lambda x: -x[1]):
    print(f"    {compound:20} {count}問")

# 6. 問題パターン分析
print("\n✅ ステップ6: 問題パターン別分析")

for result in validation_results:
    expected = set(result['claimed_keywords'])
    actual = set(result['extracted_keywords'])

    if expected == actual:
        print(f"  ✓ {result['problem_id']:25} - 完全一致")
    elif expected.issubset(actual):
        print(f"  △ {result['problem_id']:25} - 追加キーワード: {list(actual - expected)}")
    elif expected.issuperset(actual):
        print(f"  ✗ {result['problem_id']:25} - 欠落キーワード: {list(expected - actual)}")
    else:
        print(f"  ✗ {result['problem_id']:25} - 不一致: {list(expected ^ actual)}")

# 7. 詳細レポートを保存
print("\n✅ ステップ7: 詳細レポートを保存")

report = {
    "metadata": {
        "task": "Task 4.3 - 実務分野複合語検証",
        "validation_date": "2025-11-06",
        "total_problems": total_problems,
        "total_compound_words": len(compound_words),
        "domain": "practice"
    },
    "summary": {
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{(passed/total_problems)*100:.1f}%",
        "complex_word_coverage": f"{len(compound_usage)}/{len(compound_words)}"
    },
    "compound_word_statistics": dict(sorted(
        compound_usage.items(),
        key=lambda x: -x[1]
    )),
    "validation_details": validation_results,
    "recommendations": [
        "✓ 複合語分割エラー: 0件" if failed == 0 else f"❌ 複合語分割エラー: {failed}件 （修正必要）",
        f"✓ キーワード抽出精度: {(passed/total_problems)*100:.1f}%",
        "✓ 本フェーズは品質確認用（実装では50問で検証）"
    ]
}

report_path = "output/validation_report_practice_compound_words.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"  保存完了: {report_path}")

# 8. 検証結果サマリー
print("\n" + "=" * 80)
print("【Task 4.3 完了 - 実務分野複合語検証結果】")
print("=" * 80)

print(f"""
✅ 検証完了：
  - 問題数: {total_problems}個
  - 合格率: {(passed/total_problems)*100:.1f}%
  - 複合語使用数: {len(compound_usage)}個/{len(compound_words)}個

📊 複合語カバー率：
  {len(compound_usage)}/{len(compound_words)} ({(len(compound_usage)/len(compound_words))*100:.1f}%)

🔍 主要複合語使用状況：
  - 営業許可: {compound_usage.get('営業許可', 0)}問
  - 営業停止命令: {compound_usage.get('営業停止命令', 0)}問
  - 型式検定: {compound_usage.get('型式検定', 0)}問
  - 遊技機: {compound_usage.get('遊技機', 0)}問
  - その他: {sum(v for k, v in compound_usage.items() if k not in ['営業許可', '営業停止命令', '型式検定', '遊技機'])}問

✨ 検証の意義：
  1. 複合語が正確に扱われているか確認
  2. キーワード抽出精度を検証
  3. 本フェーズでは品質確認（実装時は50問で実施）

🚀 次タスク（Task 4.4）：
  - ひっかけ強度検証スクリプト
  - distractor_control_logic.py との連携
  - 難易度別の適合度確認
""")

print("=" * 80)
