#!/usr/bin/env python3
"""
500問を theme_mapping.md の47テーマに再マッピング
根拠：条文ベースのカテゴリ化で、RAG検索精度を向上させる

【マッピング戦略】
10カテゴリ → 47テーマへの細分化
- 問題テキストのキーワード分析で自動判定
- 手動ルールでカバレッジ確保
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# 47テーママッピング（theme_mapping.mdベース）
THEME_STRUCTURE = {
    "不正対策": {
        "themes": [
            "セキュリティアップデート",
            "セキュリティ確保",
            "不正改造の具体的パターン",
            "不正改造の防止",
            "不正検出技術",
            "不正行為の罰則",
            "不正防止チェックリスト",
            "不正防止対策要綱"
        ],
        "keywords": ["不正", "改造", "セキュリティ", "検出", "罰則", "防止"]
    },
    "営業時間・規制": {
        "themes": [
            "営業停止命令",
            "営業停止命令の内容",
            "営業停止期間の計算",
            "営業禁止日",
            "営業禁止時間",
            "時間帯別営業制限",
            "違反時の行政処分"
        ],
        "keywords": ["営業時間", "営業停止", "禁止", "営業所基準", "時間帯", "制限", "処分"]
    },
    "営業許可関連": {
        "themes": [
            "営業許可と営業実績の関係",
            "営業許可と型式検定の違い",
            "営業許可の取消し要件",
            "営業許可の失効事由",
            "営業許可の行政手続き",
            "営業許可は無期限有効",
            "営業許可取得の要件"
        ],
        "keywords": ["営業許可", "申請", "要件", "取消", "失効", "手続き", "資格"]
    },
    "型式検定関連": {
        "themes": [
            "型式検定と中古機の関係",
            "型式検定と製造者の責任",
            "型式検定の申請方法",
            "型式検定不合格時の手続き",
            "型式検定更新申請のタイミング",
            "遊技機型式検定は3年有効"
        ],
        "keywords": ["型式検定", "認定", "認証", "検査", "適合", "3年", "有効期間"]
    },
    "景品規制": {
        "themes": [
            "リサイクル推進法との関係",
            "景品の種類制限",
            "景品の種類制限詳細",
            "景品交換の規制",
            "賞源有効利用促進法"
        ],
        "keywords": ["景品", "規制", "交換", "リサイクル", "制限", "種類"]
    },
    "遊技機管理": {
        "themes": [
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
        ],
        "keywords": ["遊技機", "設置", "管理", "保守", "点検", "交換", "新台", "中古", "廃棄"]
    }
}

# 旧カテゴリごとのキーワード
OLD_CATEGORY_KEYWORDS = {
    "営業許可": ["営業許可", "申請", "取消", "失効", "資格", "要件"],
    "営業所基準": ["営業所", "基準", "手続き", "条件", "設置"],
    "営業時間": ["営業時間", "営業禁止", "営業停止", "時間帯"],
    "不正防止": ["不正", "改造", "セキュリティ", "防止", "検出"],
    "遊技機の設置": ["設置", "新台", "導入", "手続き"],
    "遊技機の認定": ["型式", "認定", "検定", "有効期間", "3年"],
    "景品規制": ["景品", "規制", "交換", "制限"],
    "監督・指導": ["監督", "指導", "指示", "処分", "違反"],
    "資格要件": ["資格", "要件", "営業", "許可"],
    "法改正": ["改正", "法律", "規定", "要件"]
}

def analyze_problem_text(problem_text: str, category: str) -> Tuple[str, str]:
    """問題テキストを分析して、最適なテーマを決定"""

    # 旧カテゴリをベースに主カテゴリを決定
    main_category = None
    theme_name = None

    if category == "不正防止":
        main_category = "不正対策"
        if any(kw in problem_text for kw in ["改造", "パターン", "具体"]):
            theme_name = "不正改造の具体的パターン"
        elif any(kw in problem_text for kw in ["防止", "防ぐ", "対策"]):
            theme_name = "不正改造の防止"
        elif any(kw in problem_text for kw in ["検出", "検査", "発見"]):
            theme_name = "不正検出技術"
        elif any(kw in problem_text for kw in ["罰則", "罰", "処罰"]):
            theme_name = "不正行為の罰則"
        elif any(kw in problem_text for kw in ["チェック", "リスト", "確認"]):
            theme_name = "不正防止チェックリスト"
        elif any(kw in problem_text for kw in ["セキュリティ", "保安"]):
            theme_name = "セキュリティ確保"
        else:
            theme_name = "不正改造の防止"

    elif category == "営業時間":
        main_category = "営業時間・規制"
        if any(kw in problem_text for kw in ["停止", "停止命令", "業務停止"]):
            theme_name = "営業停止命令"
        elif any(kw in problem_text for kw in ["期間", "計算", "日数"]):
            theme_name = "営業停止期間の計算"
        elif any(kw in problem_text for kw in ["禁止日", "禁止", "休業"]):
            theme_name = "営業禁止日"
        elif any(kw in problem_text for kw in ["時間", "時間帯", "制限"]):
            theme_name = "営業禁止時間"
        else:
            theme_name = "営業禁止時間"

    elif category == "営業所基準":
        main_category = "営業時間・規制"
        if any(kw in problem_text for kw in ["停止", "命令"]):
            theme_name = "営業停止命令"
        elif any(kw in problem_text for kw in ["時間", "時間帯"]):
            theme_name = "営業禁止時間"
        elif any(kw in problem_text for kw in ["基準", "設置", "条件"]):
            theme_name = "時間帯別営業制限"
        else:
            theme_name = "営業禁止時間"

    elif category == "営業許可":
        main_category = "営業許可関連"
        if any(kw in problem_text for kw in ["取消", "失効", "廃止"]):
            theme_name = "営業許可の取消し要件"
        elif any(kw in problem_text for kw in ["要件", "条件", "資格"]):
            theme_name = "営業許可取得の要件"
        elif any(kw in problem_text for kw in ["手続き", "申請", "申請書"]):
            theme_name = "営業許可の行政手続き"
        elif any(kw in problem_text for kw in ["無期限", "有効", "期限"]):
            theme_name = "営業許可は無期限有効"
        else:
            theme_name = "営業許可と営業実績の関係"

    elif category == "資格要件":
        main_category = "営業許可関連"
        if any(kw in problem_text for kw in ["要件", "条件", "必要"]):
            theme_name = "営業許可取得の要件"
        elif any(kw in problem_text for kw in ["資格", "適性", "能力"]):
            theme_name = "営業許可取得の要件"
        else:
            theme_name = "営業許可取得の要件"

    elif category == "遊技機の認定":
        main_category = "型式検定関連"
        if any(kw in problem_text for kw in ["3年", "有効期間", "期間"]):
            theme_name = "遊技機型式検定は3年有効"
        elif any(kw in problem_text for kw in ["検定", "申請", "申請方法"]):
            theme_name = "型式検定の申請方法"
        elif any(kw in problem_text for kw in ["中古", "リユース", "流通"]):
            theme_name = "型式検定と中古機の関係"
        else:
            theme_name = "遊技機型式検定は3年有効"

    elif category == "遊技機の設置":
        main_category = "遊技機管理"
        if any(kw in problem_text for kw in ["新台", "導入", "新規設置"]):
            theme_name = "新台設置の手続き"
        elif any(kw in problem_text for kw in ["確認", "チェック", "検査"]):
            theme_name = "新台導入時の確認事項"
        elif any(kw in problem_text for kw in ["交換", "設置済み"]):
            theme_name = "設置済み遊技機の交換手続き"
        elif any(kw in problem_text for kw in ["保守", "管理", "メンテナンス"]):
            theme_name = "遊技機の保守管理"
        elif any(kw in problem_text for kw in ["点検", "定期", "計画"]):
            theme_name = "遊技機の点検・保守計画"
        else:
            theme_name = "新台設置の手続き"

    elif category == "景品規制":
        main_category = "景品規制"
        if any(kw in problem_text for kw in ["種類", "制限", "限定"]):
            theme_name = "景品の種類制限"
        elif any(kw in problem_text for kw in ["交換", "交換方法", "景品交換"]):
            theme_name = "景品交換の規制"
        elif any(kw in problem_text for kw in ["リサイクル", "リユース"]):
            theme_name = "リサイクル推進法との関係"
        else:
            theme_name = "景品の種類制限"

    elif category == "監督・指導":
        main_category = "営業時間・規制"
        if any(kw in problem_text for kw in ["処分", "違反", "行政処分"]):
            theme_name = "違反時の行政処分"
        elif any(kw in problem_text for kw in ["指導", "指示", "監督", "命令"]):
            theme_name = "違反時の行政処分"
        else:
            theme_name = "違反時の行政処分"

    elif category == "法改正":
        main_category = "営業時間・規制"
        theme_name = "時間帯別営業制限"

    # デフォルト
    if not main_category:
        main_category = "遊技機管理"
        theme_name = "遊技機の保守管理"

    return main_category, theme_name

def remap_500_problems():
    """500問を47テーマに再マッピング"""

    with open('backend/problems_final_500_complete.json', 'r') as f:
        problems = json.load(f)

    remapped = []
    theme_distribution = {}

    for p in problems:
        old_cat = p.get('category', '未分類')
        problem_text = p.get('problem_text', '')

        # テーマを分析して決定
        main_cat, theme = analyze_problem_text(problem_text, old_cat)

        p['new_main_category'] = main_cat
        p['new_theme'] = theme
        p['old_category'] = old_cat

        remapped.append(p)

        if main_cat not in theme_distribution:
            theme_distribution[main_cat] = {}
        if theme not in theme_distribution[main_cat]:
            theme_distribution[main_cat][theme] = 0
        theme_distribution[main_cat][theme] += 1

    # 出力
    with open('backend/problems_500_remapped_47themes.json', 'w') as f:
        json.dump(remapped, f, indent=2, ensure_ascii=False)

    print("✅ 500問を47テーマに再マッピング完了\n")
    print("【新カテゴリ別テーマ分布】\n")

    total = 0
    for main_cat in sorted(theme_distribution.keys()):
        themes = theme_distribution[main_cat]
        cat_total = sum(themes.values())
        total += cat_total
        print(f"\n【{main_cat}】 ({cat_total}問)")
        for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
            print(f"  {theme:25} {count:3}問")

    print(f"\n\n合計: {total}問")

if __name__ == "__main__":
    remap_500_problems()
