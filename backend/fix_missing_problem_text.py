#!/usr/bin/env python3
"""
緊急修正: 失われた problem_text を復元
元のファイルと修正ファイルをマージ
"""

import json
from pathlib import Path

print("=" * 80)
print("【緊急修正: problem_text 復元】")
print("=" * 80)

# ファイルパス
original_file = Path("problems_final_500.json")
fixed_file = Path("problems_final_500_complete.json")
output_file = Path("problems_final_500_complete_fixed.json")

# データ読み込み
with open(original_file) as f:
    original = json.load(f)

with open(fixed_file) as f:
    fixed = json.load(f)

print(f"\n元のファイル: {len(original)}問")
print(f"修正ファイル: {len(fixed)}問")

# マージ処理
result = []
null_count_before = 0
null_count_after = 0

for i, orig in enumerate(original):
    problem_id = orig.get("problem_id")

    # 修正ファイルから対応する問題を探す
    fixed_problem = next((p for p in fixed if p.get("problem_id") == problem_id), None)

    if fixed_problem:
        # 修正ファイルをベースに、problem_text は元のファイルから取る
        merged = fixed_problem.copy()

        # problem_text が None なら元のファイルから復元
        if merged.get("problem_text") is None:
            null_count_before += 1
            merged["problem_text"] = orig.get("problem_text")
            null_count_after += 1

        # 他の欠落フィールドも元のファイルから補充
        for key in ["category", "difficulty", "correct_answer", "explanation", "pattern_name", "generated_at", "pattern_id", "problem_type", "format"]:
            if key not in merged or merged.get(key) is None:
                merged[key] = orig.get(key)

        result.append(merged)
    else:
        # 修正ファイルに無い場合は元のファイルをそのまま使用
        result.append(orig)

print(f"\n✅ 修正済み問題: {len(result)}問")
print(f"✅ problem_text が None だった問題: {null_count_before}問")
print(f"✅ 復元後の None 問題: {null_count_after}問")

# 検証
null_final = sum(1 for p in result if p.get("problem_text") is None)
print(f"\n【検証】")
print(f"✅ 最終的に None の problem_text: {null_final}問")

if null_final > 0:
    print(f"⚠️  警告: {null_final}問に problem_text がありません")
else:
    print(f"✅ すべての問題に problem_text があります")

# 結果を保存
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n✅ 修正済みファイルを保存しました")
print(f"   {output_file}")

# 最終的に修正ファイルを置き換え
import shutil
shutil.copy(output_file, fixed_file)
print(f"\n✅ 本ファイル（{fixed_file}）を更新しました")

print("\n" + "=" * 80)
