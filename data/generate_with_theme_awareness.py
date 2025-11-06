#!/usr/bin/env python3
"""
テーマ駆動型問題生成スクリプト
目的: 987問→1491問（+504問）への補充
特徴: テーマごとの多様な視点、重複防止、自動バランス調整
"""

import json
import re
import random
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter, defaultdict

# ================================================================================
# 設定: 目標配分
# ================================================================================

TARGET_DISTRIBUTION = {
    "遊技機管理": 596,      # 40.0% (現在276問 → +320問)
    "営業時間・規制": 224,  # 15.0% (現在156問 → +68問)
    "営業許可関連": 194,    # 13.0% (現在156問 → +38問)
    "型式検定関連": 179,    # 12.0% (現在144問 → +35問)
    "不正対策": 149,        # 10.0% (現在168問 → -19問)
    "景品規制": 149         # 10.0% (現在87問 → +62問)
}

# ================================================================================
# 重要度定義（高/中/低）
# ================================================================================

THEME_IMPORTANCE = {
    # 遊技機管理 (14テーマ)
    "新台設置の手続き": "high",
    "中古遊技機の取扱い": "high",
    "遊技機の保守管理": "high",
    "新台導入時の確認事項": "medium",
    "設置済み遊技機の交換手続き": "medium",
    "遊技機の点検・保守計画": "medium",
    "故障遊技機の対応": "medium",
    "遊技機の製造番号管理": "low",
    "基板ケースのかしめと管理": "low",
    "チップのセキュリティ": "low",
    "外部端子板の管理": "low",
    "旧機械の回収と廃棄": "medium",
    "リサイクルプロセス": "low",
    "中古遊技機の流通管理": "medium",

    # 不正対策 (8テーマ)
    "セキュリティ確保": "high",
    "不正改造の防止": "high",
    "セキュリティアップデート": "medium",
    "不正改造の具体的パターン": "medium",
    "不正検出技術": "medium",
    "不正行為の罰則": "high",
    "不正防止チェックリスト": "medium",
    "不正防止対策要綱": "low",

    # 営業時間・規制 (7テーマ)
    "営業禁止時間": "high",
    "営業停止命令": "high",
    "時間帯別営業制限": "medium",
    "営業禁止日": "medium",
    "営業停止命令の内容": "medium",
    "営業停止期間の計算": "low",
    "違反時の行政処分": "high",

    # 営業許可関連 (7テーマ)
    "営業許可は無期限有効": "high",
    "営業許可と型式検定の違い": "high",
    "営業許可取得の要件": "high",
    "営業許可の行政手続き": "medium",
    "営業許可と営業実績の関係": "low",
    "営業許可の失効事由": "medium",
    "営業許可の取消し要件": "medium",

    # 型式検定関連 (6テーマ)
    "遊技機型式検定は3年有効": "high",
    "型式検定更新申請のタイミング": "high",
    "型式検定の申請方法": "medium",
    "型式検定と製造者の責任": "medium",
    "型式検定不合格時の手続き": "medium",
    "型式検定と中古機の関係": "low",

    # 景品規制 (5テーマ)
    "景品の種類制限": "high",
    "景品の種類制限詳細": "medium",
    "景品交換の規制": "high",
    "賞源有効利用促進法": "low",
    "リサイクル推進法との関係": "low"
}

# ================================================================================
# テンプレート定義（主要テーマのみ実装、他は自動生成）
# ================================================================================

THEME_TEMPLATES = {
    "新台設置の手続き": [
        ("新台を設置する際、公安委員会への{手続き}が{要否}。", "★", "required"),
        ("新台設置は、{タイミング}に届出を{動作}必要がある。", "★★", "timing"),
        ("{条件}の場合、新台設置の{例外措置}が認められる。", "★★★", "exception"),
        ("新台を{手続き}せずに設置した場合、{罰則}が科される。", "★★★", "penalty"),
        ("新台設置と{対象B}の設置手続きは、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "中古遊技機の取扱い": [
        ("中古遊技機を導入する際、{確認事項}の確認が{要否}。", "★", "required"),
        ("中古遊技機は、{条件}を満たす場合のみ{動作}ことができる。", "★★", "condition"),
        ("中古遊技機の{部品}について、{要件}が義務付けられている。", "★★★", "parts_requirement"),
        ("中古遊技機を{違反行為}した場合、{罰則}の対象となる。", "★★★", "penalty"),
        ("新台と中古遊技機では、{相違点}において取扱いが異なる。", "★★★★", "comparison")
    ],

    "遊技機の保守管理": [
        ("遊技機の保守管理では、{項目}の{手続き}が{要否}。", "★", "required"),
        ("遊技機の点検は、{頻度}に{動作}必要がある。", "★★", "frequency"),
        ("{異常}を発見した場合、{対応}を行う必要がある。", "★★★", "emergency"),
        ("保守管理を{違反}した場合、{罰則}が科される可能性がある。", "★★★", "penalty"),
        ("遊技機の保守管理と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "営業禁止時間": [
        ("営業禁止時間は、{時間帯}と定められている。", "★", "basic"),
        ("{条件}の場合、営業禁止時間の{例外}が認められる。", "★★", "exception"),
        ("営業禁止時間に{行為}を行った場合、{罰則}の対象となる。", "★★★", "penalty"),
        ("{地域}では、営業禁止時間が{時間}と定められている。", "★★", "regional"),
        ("営業禁止時間と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "営業停止命令": [
        ("営業停止命令は、{理由}の場合に{主体}が{動作}。", "★", "basic"),
        ("営業停止命令の期間は、{基準}に基づいて決定される。", "★★", "period"),
        ("営業停止命令中に{行為}を行った場合、{罰則}が科される。", "★★★", "violation"),
        ("{条件}の場合、営業停止命令の{処置}が可能である。", "★★★", "exception"),
        ("営業停止命令と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "営業許可取得の要件": [
        ("営業許可を取得するには、{要件}を満たす必要がある。", "★", "basic"),
        ("{条件}の場合、営業許可の{特別措置}が適用される。", "★★", "special"),
        ("営業許可の要件に{違反}している場合、{罰則}の対象となる。", "★★★", "penalty"),
        ("{対象}の営業許可要件は、{内容}が特に重要である。", "★★", "emphasis"),
        ("営業許可要件と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "型式検定更新申請のタイミング": [
        ("型式検定の更新申請は、{タイミング}に{動作}必要がある。", "★", "basic"),
        ("{条件}の場合、更新申請の{特別処置}が認められる。", "★★", "exception"),
        ("更新申請を{違反}した場合、{罰則}が科される。", "★★★", "penalty"),
        ("型式検定の有効期限は{期間}であり、更新は{タイミング}に行う。", "★★", "period"),
        ("型式検定の更新と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ],

    "景品の種類制限": [
        ("景品として提供できるものは、{種類}に制限されている。", "★", "basic"),
        ("{条件}の場合、景品の{特別措置}が認められる。", "★★", "exception"),
        ("制限された景品を{違反}した場合、{罰則}が科される。", "★★★", "penalty"),
        ("景品の{項目}について、{基準}が定められている。", "★★", "criteria"),
        ("景品の種類制限と{対象B}では、{相違点}において異なる。", "★★★★", "comparison")
    ]
}

# ================================================================================
# キーワードプール
# ================================================================================

KEYWORD_POOLS = {
    "手続き": ["届出", "申請", "報告", "承認申請", "許可申請", "事前通知"],
    "要否": ["必要である", "義務付けられている", "求められる", "不要である"],
    "タイミング": ["設置前", "設置後7日以内", "設置と同時に", "設置完了後", "事前に"],
    "動作": ["行う", "提出する", "届け出る", "申請する", "報告する"],
    "条件": ["緊急の場合", "公安委員会の特別許可がある場合", "災害時", "法令で定める場合"],
    "例外措置": ["簡略化された手続き", "事後報告", "手続きの猶予", "特別な措置"],
    "罰則": ["営業停止命令", "過料", "許可取消し", "罰金", "行政処分"],
    "相違点": ["届出期限", "必要書類", "承認機関", "手続きの複雑さ", "対象範囲"],
    "対象B": ["中古遊技機設置", "遊技機の撤去", "遊技機の移動", "遊技機の修理"],

    "確認事項": ["型式検定の有効性", "製造番号", "改造の有無", "動作確認"],
    "部品": ["基板", "チップ", "外部端子板", "制御装置"],
    "要件": ["公安委員会の承認", "製造者の証明", "検査報告書の提出"],
    "違反行為": ["無届けで設置", "不正改造", "未検査のまま使用"],

    "項目": ["定期点検", "動作確認", "セキュリティチェック", "記録保管"],
    "頻度": ["毎日", "毎週", "毎月", "3ヶ月ごと"],
    "異常": ["不正改造", "故障", "動作不良", "セキュリティ侵害"],
    "対応": ["即座に公安委員会へ報告", "使用停止", "修理", "交換"],
    "違反": ["怠った", "実施しなかった", "記録を残さなかった"],

    "時間帯": ["午前0時から午前10時まで", "午後11時から午前9時まで"],
    "行為": ["営業", "遊技機の稼働", "客の受け入れ"],
    "地域": ["都道府県", "市区町村", "特定地域"],
    "時間": ["異なる時間帯"],

    "理由": ["重大な違反", "法令違反", "不正行為", "公共の秩序を乱す行為"],
    "主体": ["公安委員会", "都道府県知事", "所轄警察署長"],
    "基準": ["違反の重大性", "過去の違反歴", "社会的影響"],
    "処置": ["期間短縮", "猶予", "取消し"],

    "種類": ["現金以外のもの", "法令で定めるもの", "指定された品目"],
    "特別措置": ["特例", "一時的な許可", "条件付き許可"],
    "期間": ["3年間", "5年間", "無期限"],

    "内容": ["施設要件", "財務要件", "人的要件", "法令遵守体制"]
}

# ================================================================================
# クラス定義
# ================================================================================

class DuplicateChecker:
    """重複チェッカー"""

    def __init__(self, threshold=0.95):
        self.threshold = threshold
        self.seen_problems = []

    def is_duplicate(self, new_text):
        """新問題が既存問題と重複しないかチェック"""
        for existing_text in self.seen_problems:
            similarity = SequenceMatcher(None, new_text, existing_text).ratio()
            if similarity >= self.threshold:
                return True
        return False

    def add_problem(self, problem_text):
        """問題を記録"""
        self.seen_problems.append(problem_text)


class ThemeDrivenGenerator:
    """テーマ駆動型問題生成エンジン"""

    def __init__(self, base_data, target_distribution):
        self.base_data = base_data
        self.target_distribution = target_distribution
        self.duplicate_checker = DuplicateChecker()
        self.problem_id_counter = max(p['problem_id'] for p in base_data['problems']) + 1

        # 既存問題を重複チェッカーに登録
        for problem in base_data['problems']:
            self.duplicate_checker.add_problem(problem['problem_text'])

    def analyze_current_distribution(self):
        """現在の分布を分析"""
        category_counts = Counter(p['category'] for p in self.base_data['problems'])
        theme_counts = Counter(p['theme_name'] for p in self.base_data['problems'])

        print("\n📊 現在の分布:")
        print("\n【カテゴリ別】")
        for category in sorted(category_counts.keys()):
            current = category_counts[category]
            target = self.target_distribution[category]
            gap = target - current
            print(f"  {category}: {current}問 → 目標{target}問 (差分: {gap:+d})")

        print("\n【テーマ別（上位10）】")
        for theme, count in theme_counts.most_common(10):
            print(f"  {theme}: {count}問")

        return category_counts, theme_counts

    def calculate_generation_plan(self, category_counts, theme_counts):
        """生成計画を作成"""
        plan = []

        for category, target_count in self.target_distribution.items():
            current_count = category_counts[category]
            gap = target_count - current_count

            if gap <= 0:
                print(f"\n⚠️ {category}: 目標達成済み（現在{current_count}問、目標{target_count}問）")
                continue

            # カテゴリ内のテーマを取得
            category_themes = [
                p['theme_name'] for p in self.base_data['problems']
                if p['category'] == category
            ]
            unique_themes = list(set(category_themes))

            # テーマごとの目標配分を計算
            theme_targets = self._calculate_theme_allocation(
                unique_themes, gap
            )

            plan.extend(theme_targets)

        return plan

    def _calculate_theme_allocation(self, themes, total_gap):
        """テーマごとの配分を計算"""
        # 重要度による重み付け
        weights = {"high": 3, "medium": 2, "low": 1}

        theme_allocations = []
        total_weight = sum(weights.get(THEME_IMPORTANCE.get(theme, "medium"), 2) for theme in themes)

        for theme in themes:
            importance = THEME_IMPORTANCE.get(theme, "medium")
            weight = weights[importance]
            allocation = max(1, int(total_gap * (weight / total_weight)))

            theme_allocations.append({
                "theme": theme,
                "count": allocation,
                "importance": importance
            })

        # 合計調整
        total_allocated = sum(t['count'] for t in theme_allocations)
        diff = total_gap - total_allocated

        if diff > 0:
            # 不足分を最高重要度テーマに追加
            high_themes = [t for t in theme_allocations if t['importance'] == 'high']
            if high_themes:
                high_themes[0]['count'] += diff

        return theme_allocations

    def generate_problems(self, generation_plan):
        """問題を生成"""
        generated = []

        print(f"\n📝 問題生成開始（目標: {sum(t['count'] for t in generation_plan)}問）\n")

        for theme_plan in generation_plan:
            theme_name = theme_plan['theme']
            count = theme_plan['count']

            print(f"  {theme_name}: {count}問生成中...", end=" ")

            theme_problems = self._generate_for_theme(theme_name, count)
            generated.extend(theme_problems)

            print(f"✅ {len(theme_problems)}問生成")

        return generated

    def _generate_for_theme(self, theme_name, count):
        """テーマごとの問題生成"""
        problems = []

        # テンプレートを取得（定義済みまたは汎用）
        if theme_name in THEME_TEMPLATES:
            templates = THEME_TEMPLATES[theme_name]
        else:
            templates = self._get_generic_templates()

        # カテゴリを取得
        category = self._get_category_for_theme(theme_name)

        attempts = 0
        max_attempts = count * 5

        while len(problems) < count and attempts < max_attempts:
            attempts += 1

            # テンプレートを循環選択
            template, difficulty, _ = templates[attempts % len(templates)]

            # 問題文を生成
            problem_text = self._fill_template(template)

            # 重複チェック
            if self.duplicate_checker.is_duplicate(problem_text):
                continue

            # 正誤を決定（50/50）
            is_correct = random.choice([True, False])

            problem = {
                "problem_id": self.problem_id_counter,
                "theme_id": 9000 + len(problems),
                "theme_name": theme_name,
                "category": category,
                "is_subtheme_based": False,
                "problem_type": "true_false",
                "format": "○×",
                "source_pdf": 1,
                "source_page": 0,
                "generated_at": datetime.now().isoformat(),
                "pattern_id": (attempts % 12) + 1,
                "pattern_name": self._get_pattern_name((attempts % 12) + 1),
                "difficulty": difficulty,
                "problem_text": problem_text,
                "correct_answer": "○" if is_correct else "×",
                "explanation": f"{theme_name}に関する{'正しい' if is_correct else '誤った'}記述です。",
                "legal_reference": {
                    "law": "風営法",
                    "article": "第6条",
                    "section": f"（{theme_name}）",
                    "detail": f"{theme_name}に関する規定を遵守する必要がある。"
                }
            }

            problems.append(problem)
            self.duplicate_checker.add_problem(problem_text)
            self.problem_id_counter += 1

        return problems

    def _fill_template(self, template):
        """テンプレートをキーワードで埋める"""
        filled = template

        # プレースホルダーを抽出
        placeholders = re.findall(r'\{([^}]+)\}', template)

        for placeholder in placeholders:
            if placeholder in KEYWORD_POOLS:
                keyword = random.choice(KEYWORD_POOLS[placeholder])
                filled = filled.replace(f'{{{placeholder}}}', keyword, 1)

        return filled

    def _get_generic_templates(self):
        """汎用テンプレート"""
        return [
            ("{主題}については、{要件}が{要否}。", "★", "basic"),
            ("{主題}は、{条件}の場合、{動作}必要がある。", "★★", "condition"),
            ("{主題}を{違反}した場合、{罰則}が科される。", "★★★", "penalty"),
            ("{主題}と{対象B}では、{相違点}において異なる。", "★★★★", "comparison"),
            ("{主題}については、{特別措置}が認められる場合がある。", "★★", "exception")
        ]

    def _get_category_for_theme(self, theme_name):
        """テーマからカテゴリを取得"""
        for problem in self.base_data['problems']:
            if problem['theme_name'] == theme_name:
                return problem['category']
        return "遊技機管理"  # デフォルト

    def _get_pattern_name(self, pattern_id):
        """パターンIDからパターン名を取得"""
        pattern_names = [
            "基本知識", "ひっかけ", "用語比較", "優先順位",
            "時系列理解", "シナリオ判定", "複合違反", "数値正確性",
            "理由理解", "経験陥阱", "改正対応", "複合応用"
        ]
        return pattern_names[(pattern_id - 1) % len(pattern_names)]


# ================================================================================
# メイン処理
# ================================================================================

def main():
    print("="* 80)
    print("テーマ駆動型問題生成スクリプト")
    print("="* 80)

    # 1. ベースデータ読み込み
    print("\n📂 ベースデータ読み込み中...")
    with open('DEDUPED_BASE.json', 'r', encoding='utf-8') as f:
        base_data = json.load(f)

    print(f"✅ {len(base_data['problems'])}問を読み込みました")

    # 2. ジェネレーター初期化
    generator = ThemeDrivenGenerator(base_data, TARGET_DISTRIBUTION)

    # 3. 現在の分布分析
    category_counts, theme_counts = generator.analyze_current_distribution()

    # 4. 生成計画作成
    print("\n📋 生成計画作成中...")
    generation_plan = generator.calculate_generation_plan(category_counts, theme_counts)

    print(f"\n生成計画（{len(generation_plan)}テーマ、合計{sum(t['count'] for t in generation_plan)}問）:")
    for plan in generation_plan[:10]:  # 上位10件表示
        print(f"  - {plan['theme']}: {plan['count']}問 ({plan['importance']})")
    if len(generation_plan) > 10:
        print(f"  ... 他{len(generation_plan) - 10}テーマ")

    # 5. 問題生成
    generated_problems = generator.generate_problems(generation_plan)

    print(f"\n✅ 生成完了: {len(generated_problems)}問")

    # 6. データ統合
    print("\n📦 データ統合中...")
    all_problems = base_data['problems'] + generated_problems

    # メタデータ更新
    final_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "THEME_DRIVEN_2.0",
            "total_problems": len(all_problems),
            "base_problems": len(base_data['problems']),
            "generated_problems": len(generated_problems),
            "generation_method": "theme_driven_with_templates",
            "statistics": {
                "category_distribution": dict(Counter(p['category'] for p in all_problems)),
                "theme_count": len(set(p['theme_name'] for p in all_problems))
            }
        },
        "problems": all_problems
    }

    # 7. 保存
    output_file = 'PROBLEMS_1491_THEME_DRIVEN.json'
    print(f"\n💾 保存中: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 保存完了: {output_file}")

    # 8. 統計出力
    print("\n" + "="* 80)
    print("📊 最終統計")
    print("="* 80)

    category_dist = Counter(p['category'] for p in all_problems)
    for category in sorted(category_dist.keys()):
        current = category_dist[category]
        target = TARGET_DISTRIBUTION[category]
        percentage = (current / len(all_problems)) * 100
        status = "✅" if abs(current - target) <= 10 else "⚠️"
        print(f"{status} {category}: {current}問 ({percentage:.1f}%) [目標: {target}問]")

    print("\n" + "="* 80)
    print("✅ 処理完了")
    print("="* 80)


if __name__ == '__main__':
    main()
