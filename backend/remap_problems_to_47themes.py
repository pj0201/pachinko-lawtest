#!/usr/bin/env python3
"""
試験問題を theme_mapping.md の47テーマに再マッピング
根拠：条文ベースのカテゴリ化で、RAG検索精度を向上
"""

import json
from pathlib import Path
from typing import Dict, List

# 47テーママッピング（theme_mapping.mdベース）
THEME_MAPPING = {
    "不正対策": [
        "セキュリティアップデート",
        "セキュリティ確保",
        "不正改造の具体的パターン",
        "不正改造の防止",
        "不正検出技術",
        "不正行為の罰則",
        "不正防止チェックリスト",
        "不正防止対策要綱"
    ],
    "営業時間・規制": [
        "営業停止命令",
        "営業停止命令の内容",
        "営業停止期間の計算",
        "営業禁止日",
        "営業禁止時間",
        "時間帯別営業制限",
        "違反時の行政処分"
    ],
    "営業許可関連": [
        "営業許可と営業実績の関係",
        "営業許可と型式検定の違い",
        "営業許可の取消し要件",
        "営業許可の失効事由",
        "営業許可の行政手続き",
        "営業許可は無期限有効",
        "営業許可取得の要件"
    ],
    "型式検定関連": [
        "型式検定と中古機の関係",
        "型式検定と製造者の責任",
        "型式検定の申請方法",
        "型式検定不合格時の手続き",
        "型式検定更新申請のタイミング",
        "遊技機型式検定は3年有効"
    ],
    "景品規制": [
        "リサイクル推進法との関係",
        "景品の種類制限",
        "景品の種類制限詳細",
        "景品交換の規制",
        "賞源有効利用促進法"
    ],
    "遊技機管理": [
        "チップのセキュリティ",
        "リサイクルプロセス",
        "中古遊技機の取扱い",
        "中古遊技機の流通管理",
        "基板ケースのかしめと管理",
        "外部端子板の管理",
        "故障遊技機の対応",
        "新台導入時の確認事項",
        "新台設置の手続き",
        "旧機械の回収と廃棄",
        "設置済み遊技機の交換手続き",
        "遊技機の保守管理",
        "遊技機の点検・保守計画",
        "遊技機の製造番号管理"
    ]
}

# 旧カテゴリから新テーマへのマッピングルール
OLD_TO_NEW_MAPPING = {
    "営業許可": ("営業許可関連", "営業許可と営業実績の関係"),
    "営業所基準": ("営業許可関連", "営業許可の行政手続き"),
    "営業時間": ("営業時間・規制", "営業禁止時間"),
    "不正防止": ("不正対策", "不正改造の防止"),
    "遊技機の設置": ("遊技機管理", "新台設置の手続き"),
    "遊技機の認定": ("型式検定関連", "遊技機型式検定は3年有効"),
    "景品規制": ("景品規制", "景品の種類制限"),
    "監督・指導": ("営業時間・規制", "違反時の行政処分"),
    "資格要件": ("営業許可関連", "営業許可取得の要件"),
    "法改正": ("営業時間・規制", "営業停止命令")
}

def remap_problems(input_file: str, output_file: str):
    """試験問題を47テーマにマッピング直す"""

    with open(input_file, 'r') as f:
        problems = json.load(f)

    remapped_problems = []

    for problem in problems:
        old_category = problem.get('category')

        # マッピング実行
        if old_category in OLD_TO_NEW_MAPPING:
            new_category, new_theme = OLD_TO_NEW_MAPPING[old_category]
        else:
            new_category = "未分類"
            new_theme = "その他"

        # 問題に新カテゴリ・テーマを追加
        problem['new_category'] = new_category
        problem['new_theme'] = new_theme
        problem['old_category'] = old_category

        remapped_problems.append(problem)

    # 出力
    with open(output_file, 'w') as f:
        json.dump(remapped_problems, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(remapped_problems)}問をマッピング直しました")
    print(f"出力: {output_file}\n")

    # サマリー表示
    print("【新カテゴリ別の問題数】")
    summary = {}
    for p in remapped_problems:
        cat = p['new_category']
        if cat not in summary:
            summary[cat] = 0
        summary[cat] += 1

    for cat, count in sorted(summary.items()):
        print(f"  {cat}: {count}問")

if __name__ == "__main__":
    input_file = "/home/planj/patshinko-exam-app/backend/problems_50_hybrid_rag.json"
    output_file = "/home/planj/patshinko-exam-app/backend/problems_50_remapped_47themes.json"

    remap_problems(input_file, output_file)
