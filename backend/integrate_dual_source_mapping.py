#!/usr/bin/env python3
"""
講習ガイドライン + 風営法の2つのソースを統合した47テーママッピング
両方のソースのキーワードを合算して、より正確なマッピングを実現
"""

import json
from pathlib import Path
import re

def extract_keywords_from_file(file_path: str, sample_length: int = 2000) -> list:
    """ファイルからキーワードを抽出"""

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()[:sample_length]
    except:
        return []

    # 日本語の名詞を抽出（3文字以上）
    words = re.findall(r'[\u4e00-\u9fff]{3,}', content)

    # 重複排除と頻度カウント
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: -x[1])
    return [w[0] for w in sorted_words[:20]]

def build_dual_source_filter() -> dict:
    """講習ガイドライン + 風営法の統合フィルターを構築"""

    dual_filter = {}

    # 47テーマのマッピング（theme_mapping.mdから）
    theme_categories = {
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

    # 講習ガイドラインから各テーマのキーワードを抽出
    lecture_dir = Path('rag_data/lecture_text')

    for category, themes in theme_categories.items():
        for theme in themes:
            # 講習ガイドラインのファイルを探す
            matching_files = list(lecture_dir.glob(f"*{theme}*.txt"))

            lecture_keywords = []
            if matching_files:
                lecture_keywords = extract_keywords_from_file(str(matching_files[0]))

            # 風営法のキーワード（テーマから推測）
            legal_keywords = _generate_legal_keywords(theme)

            # 統合
            dual_filter[theme] = {
                'category': category,
                'lecture_keywords': lecture_keywords,
                'legal_keywords': legal_keywords,
                'all_keywords': list(set(lecture_keywords + legal_keywords))
            }

    return dual_filter

def _generate_legal_keywords(theme: str) -> list:
    """テーマに対応する風営法のキーワードを生成"""

    legal_keywords_map = {
        "営業許可取得の要件": ["営業許可", "申請", "要件", "条件", "資格", "施設"],
        "営業許可の行政手続き": ["申請", "提出", "手続き", "書類", "届出"],
        "営業許可の取消し要件": ["取消", "廃止", "失効", "要件"],
        "営業許可は無期限有効": ["無期限", "有効期限", "期限"],
        "営業許可と営業実績の関係": ["営業", "実績", "経験", "年数"],
        "営業禁止時間": ["営業時間", "営業禁止", "時間帯", "時間"],
        "営業禁止日": ["営業禁止日", "禁止", "日"],
        "営業停止命令": ["営業停止", "命令", "停止"],
        "営業停止期間の計算": ["期間", "計算", "日数"],
        "遊技機型式検定は3年有効": ["型式検定", "3年", "有効期間"],
        "型式検定の申請方法": ["申請", "申請方法", "手続き"],
        "不正改造の防止": ["不正", "改造", "防止"],
        "不正検出技術": ["検出", "検査", "発見"],
        "不正行為の罰則": ["罰", "罰則", "懲役"],
        "景品の種類制限": ["景品", "種類", "制限"],
        "新台設置の手続き": ["設置", "手続き", "導入"],
        "遊技機の保守管理": ["保守", "管理", "維持"],
    }

    return legal_keywords_map.get(theme, [])

def apply_dual_source_mapping():
    """2つのソースを統合したマッピングを実行"""

    print("【統合フィルター構築中...】\n")
    dual_filter = build_dual_source_filter()

    print(f"✅ 統合フィルター構築完了（{len(dual_filter)}テーマ）\n")

    # 500問にマッピング
    with open('backend/problems_final_500_complete.json', 'r') as f:
        problems = json.load(f)

    remapped = []
    distribution = {}

    for p in problems:
        problem_text = p.get('problem_text', '')

        best_theme = None
        best_score = 0

        # 全テーマでスコアリング
        for theme, theme_data in dual_filter.items():
            score = 0
            for kw in theme_data['all_keywords']:
                if kw in problem_text:
                    score += 1

            if score > best_score:
                best_score = score
                best_theme = theme

        if best_theme:
            p['dual_source_theme'] = best_theme
            p['dual_source_category'] = dual_filter[best_theme]['category']
        else:
            p['dual_source_theme'] = "営業許可取得の要件"
            p['dual_source_category'] = "営業許可関連"

        remapped.append(p)

        theme = p['dual_source_theme']
        if theme not in distribution:
            distribution[theme] = 0
        distribution[theme] += 1

    # 出力
    with open('backend/problems_500_dual_source_mapped.json', 'w') as f:
        json.dump(remapped, f, indent=2, ensure_ascii=False)

    print("✅ 500問に統合マッピングを適用完了\n")
    print("【統合マッピング後の分布】\n")

    # カテゴリ別に集計
    category_distribution = {}
    for p in remapped:
        cat = p['dual_source_category']
        if cat not in category_distribution:
            category_distribution[cat] = 0
        category_distribution[cat] += 1

    for cat, count in sorted(category_distribution.items(), key=lambda x: -x[1]):
        print(f"\n【{cat}】 ({count}問)")
        # そのカテゴリのテーマ分布
        themes = [p['dual_source_theme'] for p in remapped if p['dual_source_category'] == cat]
        theme_freq = {}
        for t in themes:
            theme_freq[t] = theme_freq.get(t, 0) + 1
        for theme, count in sorted(theme_freq.items(), key=lambda x: -x[1]):
            print(f"  {theme:35} {count:3}問")

    print(f"\n\n合計: {len(remapped)}問")

if __name__ == "__main__":
    apply_dual_source_mapping()
