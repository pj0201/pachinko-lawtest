#!/usr/bin/env python3
"""
ソース検証: 風営法 + 講習ガイドラインの統合分析
両ソースで実際に存在するテーマを特定し、47テーマの問題を洗い出す
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_source_coverage():
    """両ソースの完全比較分析"""

    print("=" * 80)
    print("【ソース統合検証 - 両ソースの徹底比較】")
    print("=" * 80)
    print()

    # 47テーマの期待リスト
    expected_47_themes = {
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
            "営業禁止時間",
            "営業禁止日",
            "時間帯別営業制限",
            "違反時の行政処分"
        ],
        "営業許可関連": [
            "営業許可取得の要件",
            "営業許可の行政手続き",
            "営業許可の取消し要件",
            "営業許可は無期限有効",
            "営業許可と営業実績の関係",
            "営業許可と型式検定の違い",
            "（不明なテーマ7）"
        ],
        "型式検定関連": [
            "遊技機型式検定は3年有効",
            "型式検定の申請方法",
            "型式検定と中古機の関係",
            "型式検定と製造者の責任",
            "型式検定不合格時の手続き",
            "型式検定更新申請のタイミング"
        ],
        "景品規制": [
            "景品の種類制限",
            "景品交換の規制",
            "景品の種類制限詳細",
            "リサイクル推進法との関係",
            "賞源有効利用促進法"
        ],
        "遊技機管理": [
            "新台設置の手続き",
            "新台導入時の確認事項",
            "遊技機の保守管理",
            "遊技機の点検・保守計画",
            "設置済み遊技機の交換手続き",
            "中古遊技機の取扱い",
            "中古遊技機の流通管理",
            "遊技機の製造番号管理",
            "基板ケースのかしめと管理",
            "外部端子板の管理",
            "チップのセキュリティ",
            "リサイクルプロセス",
            "故障遊技機の対応",
            "旧機械の回収と廃棄"
        ]
    }

    # 講習ガイドラインから実際に存在するテーマ
    actual_lecture_themes = {
        "不正対策": [
            "セキュリティアップデート",
            "セキュリティ確保",
            "チップのセキュリティ",
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
            "営業禁止時間"
        ],
        "営業許可関連": [
            "営業許可と営業実績の関係",
            "営業許可と型式検定の違い",
            "営業許可の取消し要件",
            "営業許可の失効事由",
            "営業許可の行政手続き",
            "営業許可は無期限有効"
        ],
        "型式検定関連": [
            "型式検定と中古機の関係",
            "型式検定と製造者の責任",
            "型式検定の申請方法",
            "型式検定更新申請のタイミング",
            "遊技機型式検定は3年有効"
        ],
        "景品規制": [
            "リサイクルプロセス",
            "リサイクル推進法との関係",
            "景品の種類制限",
            "景品交換の規制",
            "賞源有効利用促進法"
        ],
        "遊技機管理": [
            "中古遊技機の取扱い",
            "中古遊技機の流通管理",
            "基板ケースのかしめと管理",
            "外部端子板の管理",
            "故障遊技機の対応",
            "新台設置の手続き",
            "旧機械の回収と廃棄",
            "時間帯別営業制限",
            "設置済み遊技機の交換手続き",
            "遊技機の保守管理",
            "遊技機の点検・保守計画",
            "遊技機の製造番号管理",
            "違反時の行政処分"
        ]
    }

    # 比較結果
    print("【期待 vs 実際の比較】\n")

    missing_themes = []
    placeholder_themes = []
    extra_themes = []

    for category in sorted(expected_47_themes.keys()):
        expected = set(expected_47_themes[category])
        actual = set(actual_lecture_themes.get(category, []))

        print(f"\n【{category}】")
        print(f"  期待: {len(expected)}テーマ")
        print(f"  実際: {len(actual)}テーマ")

        missing = expected - actual
        if missing:
            print(f"  ⚠️  欠落テーマ ({len(missing)}):")
            for t in sorted(missing):
                print(f"    - {t}")
                if "（不明" not in t and t != "":
                    missing_themes.append((category, t))

        extra = actual - expected
        if extra:
            print(f"  ℹ️  追加テーマ ({len(extra)}):")
            for t in sorted(extra):
                print(f"    + {t}")
                extra_themes.append((category, t))

    # 特に問題のあるテーマをチェック
    print("\n" + "=" * 80)
    print("【疑わしいテーマ検証】")
    print("=" * 80)

    lecture_dir = Path('rag_data/lecture_text')

    suspicious_theme = "営業許可と営業実績の関係"
    theme_file = list(lecture_dir.glob(f"*{suspicious_theme}*"))

    if theme_file:
        with open(theme_file[0], 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n【{suspicious_theme}】")
        print(f"  サイズ: {len(content):,}文字")
        print(f"  判定: {'❌ プレースホルダ可能性高' if len(content) < 3000 else '✅ 実質的内容あり'}")
        print(f"  内容サンプル:")
        print(f"  {content[:200]}...")

    # サマリー
    print("\n" + "=" * 80)
    print("【結論と対応】")
    print("=" * 80)

    print(f"\n✅ 期待47テーマに対して実際は41テーマ")
    print(f"⚠️  欠落: {len(missing_themes)}テーマ")
    print(f"ℹ️  追加: {len(extra_themes)}テーマ")

    if missing_themes:
        print(f"\n【対応が必要なテーマ】")
        for cat, theme in missing_themes:
            print(f"  [{cat}] {theme}")

if __name__ == "__main__":
    analyze_source_coverage()
