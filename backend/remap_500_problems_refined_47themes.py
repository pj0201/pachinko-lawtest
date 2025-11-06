#!/usr/bin/env python3
"""
500問を47テーマに再マッピング【改良版】
GROK4採用済み500問の品質を保ちながら、テーマ分布を最適化
"""

import json
from typing import Tuple

# より細かいテーママッピングルール
DETAILED_THEME_KEYWORDS = {
    # 不正対策（8テーマ）
    "セキュリティ確保": ["セキュリティ", "保安", "防犯", "監視", "管理", "装置"],
    "不正改造の防止": ["改造", "防止", "対策", "防ぐ", "防がれ", "改造禁止"],
    "不正改造の具体的パターン": ["パターン", "事例", "具体的", "例"],
    "不正検出技術": ["検出", "検査", "発見", "検知", "感知"],
    "不正行為の罰則": ["罰", "罰則", "懲役", "罰金", "処罰"],

    # 営業時間・規制（7テーマ）
    "営業禁止時間": ["営業時間", "営業禁止", "営業開始", "営業終了", "時間制限", "時間帯"],
    "営業禁止日": ["営業禁止日", "禁止日", "休業日", "営業できない日"],
    "営業停止命令": ["営業停止", "営業停止命令", "停止命令", "業務停止"],
    "営業停止期間の計算": ["停止期間", "期間計算", "日数計算", "期間"],
    "時間帯別営業制限": ["時間帯", "営業所", "営業規制", "営業基準", "基準"],
    "違反時の行政処分": ["違反", "処分", "指導", "指示", "警告", "行政"],

    # 営業許可関連（7テーマ）
    "営業許可取得の要件": ["営業許可", "取得", "要件", "条件", "資格", "申請資格"],
    "営業許可の行政手続き": ["申請", "手続き", "申請書", "申請方法", "提出"],
    "営業許可の取消し要件": ["取消", "取り消し", "廃止", "失効", "失効要件"],
    "営業許可は無期限有効": ["無期限", "有効期限", "期限なし", "永遠", "有効"],
    "営業許可と営業実績の関係": ["実績", "営業", "許可", "関係"],
    "営業許可と型式検定の違い": ["違い", "区別", "相違", "型式検定"],

    # 型式検定関連（6テーマ）
    "遊技機型式検定は3年有効": ["型式検定", "3年", "有効期間", "更新", "期限"],
    "型式検定の申請方法": ["型式検定", "申請", "申請方法", "方法"],
    "型式検定と中古機の関係": ["中古", "型式検定", "リユース", "流通"],
    "型式検定と製造者の責任": ["製造者", "型式検定", "責任"],
    "型式検定不合格時の手続き": ["不合格", "不適合", "手続き"],
    "型式検定更新申請のタイミング": ["更新", "タイミング", "時期"],

    # 景品規制（5テーマ）
    "景品の種類制限": ["景品", "種類", "制限", "限定", "範囲"],
    "景品交換の規制": ["景品交換", "交換", "景品"],
    "景品の種類制限詳細": ["景品", "詳細", "具体的"],
    "リサイクル推進法との関係": ["リサイクル", "リユース", "推進法"],
    "賞源有効利用促進法": ["賞源", "有効利用", "促進法"],

    # 遊技機管理（14テーマ）
    "新台設置の手続き": ["新台", "設置", "導入", "手続き", "新規"],
    "新台導入時の確認事項": ["新台", "導入", "確認", "チェック", "検査"],
    "遊技機の保守管理": ["保守", "管理", "メンテナンス", "維持"],
    "遊技機の点検・保守計画": ["点検", "保守計画", "定期点検", "計画"],
    "設置済み遊技機の交換手続き": ["交換", "設置済み", "設置機", "取替"],
    "中古遊技機の取扱い": ["中古", "取扱い", "取扱", "リユース"],
    "中古遊技機の流通管理": ["中古", "流通", "市場"],
    "遊技機の製造番号管理": ["製造番号", "管理", "番号"],
    "基板ケースのかしめと管理": ["基板", "ケース", "かしめ", "管理"],
    "外部端子板の管理": ["外部端子", "端子板", "管理"],
    "チップのセキュリティ": ["チップ", "セキュリティ", "保安"],
    "リサイクルプロセス": ["リサイクル", "廃棄", "処分"],
    "故障遊技機の対応": ["故障", "不具合", "対応", "修理"],
    "旧機械の回収と廃棄": ["回収", "廃棄", "廃棄処分"],
}

def find_best_theme(problem_text: str, old_category: str) -> Tuple[str, str]:
    """問題テキストから最適なテーマを検索（キーワードマッチ）"""

    # 大カテゴリの決定
    category_map = {
        "不正防止": "不正対策",
        "営業時間": "営業時間・規制",
        "営業所基準": "営業時間・規制",
        "営業許可": "営業許可関連",
        "資格要件": "営業許可関連",
        "遊技機の認定": "型式検定関連",
        "遊技機の設置": "遊技機管理",
        "景品規制": "景品規制",
        "監督・指導": "営業時間・規制",
        "法改正": "営業時間・規制"
    }

    main_category = category_map.get(old_category, "遊技機管理")

    # テーマの決定（キーワード照合）
    best_theme = None
    best_score = 0

    for theme_name, keywords in DETAILED_THEME_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in problem_text:
                score += 1

        if score > best_score:
            best_score = score
            best_theme = theme_name

    # マッチなしの場合のデフォルト
    if not best_theme:
        defaults = {
            "不正対策": "不正改造の防止",
            "営業時間・規制": "営業禁止時間",
            "営業許可関連": "営業許可取得の要件",
            "型式検定関連": "遊技機型式検定は3年有効",
            "景品規制": "景品の種類制限",
            "遊技機管理": "新台設置の手続き"
        }
        best_theme = defaults.get(main_category, "新台設置の手続き")

    return main_category, best_theme

def refine_500_problems():
    """500問を改良版マッピングで再処理"""

    with open('backend/problems_500_remapped_47themes.json', 'r') as f:
        problems = json.load(f)

    refined = []
    distribution = {}

    for p in problems:
        problem_text = p.get('problem_text', '')
        old_cat = p.get('old_category', '未分類')

        # 改良版マッピングを実行
        main_cat, theme = find_best_theme(problem_text, old_cat)

        p['main_category'] = main_cat
        p['theme'] = theme

        refined.append(p)

        # 統計
        if main_cat not in distribution:
            distribution[main_cat] = {}
        if theme not in distribution[main_cat]:
            distribution[main_cat][theme] = 0
        distribution[main_cat][theme] += 1

    # 出力
    with open('backend/problems_500_refined_47themes.json', 'w') as f:
        json.dump(refined, f, indent=2, ensure_ascii=False)

    # 表示
    print("✅ 500問を改良版47テーママッピング完了\n")
    print("【改良後の分布】\n")

    total = 0
    for main_cat in sorted(distribution.keys()):
        themes = distribution[main_cat]
        cat_total = sum(themes.values())
        total += cat_total
        print(f"\n【{main_cat}】 ({cat_total}問)")
        for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
            print(f"  {theme:30} {count:3}問")

    print(f"\n\n合計: {total}問")

if __name__ == "__main__":
    refine_500_problems()
