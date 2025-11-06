#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OPUS拡張生成システム
高品質300問を基盤に600問→900問へ拡張
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any
from opus_300_problem_generator import OpusProblemGenerator

class OpusExpansionGenerator(OpusProblemGenerator):
    """OPUS拡張生成クラス"""

    def __init__(self):
        """初期化"""
        super().__init__()
        self.problem_variations = {}

    def create_variation(self, theme: Dict, pattern: Dict, variation_type: str) -> Dict:
        """問題のバリエーション生成"""

        # 基本問題生成
        base_problem = self.generate_problem(theme, pattern)

        # バリエーションタイプに応じて変更
        if variation_type == "inverse":
            # 正誤を逆にする
            problem_text = base_problem["problem_text"]
            if base_problem["correct_answer"] == "○":
                # 正しい文を誤りに変換
                if "必要" in problem_text:
                    problem_text = problem_text.replace("必要", "不要")
                elif "できる" in problem_text:
                    problem_text = problem_text.replace("できる", "できない")
                elif "である" in problem_text:
                    problem_text = problem_text.replace("である", "でない")
                else:
                    problem_text = problem_text.replace("。", "ことはない。")

                base_problem["problem_text"] = problem_text
                base_problem["correct_answer"] = "×"
                base_problem["explanation"] = f"誤りです。{theme['content']}。{theme['legal_ref']}を確認してください。"
            else:
                # 誤った文を正しく変換
                if "不要" in problem_text:
                    problem_text = problem_text.replace("不要", "必要")
                elif "できない" in problem_text:
                    problem_text = problem_text.replace("できない", "できる")
                elif "でない" in problem_text:
                    problem_text = problem_text.replace("でない", "である")

                base_problem["problem_text"] = problem_text
                base_problem["correct_answer"] = "○"
                base_problem["explanation"] = f"正解です。{theme['content']}。{theme['legal_ref']}に規定されています。"

        elif variation_type == "detail":
            # より詳細な条件を追加
            conditions = [
                "営業所において",
                "風営法に基づき",
                "公安委員会の承認を得て",
                "所定の手続きにより",
                "法令に従って"
            ]
            condition = random.choice(conditions)
            base_problem["problem_text"] = f"{condition}、{base_problem['problem_text']}"

        elif variation_type == "specific":
            # 具体例を追加
            if theme["category"] == "遊技機管理":
                specifics = [
                    "パチンコ機",
                    "パチスロ機",
                    "新台",
                    "中古機",
                    "認定機"
                ]
                specific = random.choice(specifics)
                base_problem["problem_text"] = base_problem["problem_text"].replace("遊技機", specific)

            elif theme["category"] == "営業時間・規制":
                if "営業" in base_problem["problem_text"]:
                    base_problem["problem_text"] = base_problem["problem_text"].replace("営業", "パチンコ店の営業")

        elif variation_type == "negative":
            # 二重否定を避けつつ否定形を作る
            if "禁止" not in base_problem["problem_text"]:
                base_problem["problem_text"] = base_problem["problem_text"].replace("必要である", "必要ではない")
                base_problem["problem_text"] = base_problem["problem_text"].replace("できる", "できない")
                # 答えを反転
                base_problem["correct_answer"] = "×" if base_problem["correct_answer"] == "○" else "○"
                # 解説も調整
                if base_problem["correct_answer"] == "×":
                    base_problem["explanation"] = f"誤りです。{theme['content']}。"
                else:
                    base_problem["explanation"] = f"正解です。実際には{theme['content']}。"

        elif variation_type == "exception":
            # 例外事項を追加
            exceptions = [
                "ただし、特例が認められる場合を除く",
                "原則として",
                "一般的に",
                "通常は"
            ]
            exception = random.choice(exceptions)

            if pattern["id"] in ["P01", "P02", "P05", "P06"]:  # 基本的なパターン
                base_problem["problem_text"] = f"{exception}、{base_problem['problem_text']}"

        # バリエーションタイプを記録
        base_problem["variation_type"] = variation_type

        return base_problem

    def expand_to_600(self, base_300: List[Dict]) -> List[Dict]:
        """300問を600問に拡張"""
        expanded = []

        # 既存の300問を追加
        expanded.extend(base_300)

        # 各テーマ×パターンの組み合わせで追加生成
        variation_types = ["inverse", "detail", "specific", "negative", "exception"]

        # 重要カテゴリから優先的に拡張
        important_themes = [t for t in self.themes if t["category"] in ["遊技機管理", "不正対策"]]
        less_important_themes = [t for t in self.themes if t["category"] not in ["遊技機管理", "不正対策"]]

        # 重要テーマから150問追加
        for _ in range(150):
            theme = random.choice(important_themes)
            pattern = random.choice(self.patterns)
            variation = random.choice(variation_types)

            problem = self.create_variation(theme, pattern, variation)
            problem["problem_id"] = len(expanded) + 1
            expanded.append(problem)

        # その他のテーマから150問追加
        for _ in range(150):
            theme = random.choice(less_important_themes)
            pattern = random.choice(self.patterns)
            variation = random.choice(variation_types[:3])  # シンプルなバリエーション

            problem = self.create_variation(theme, pattern, variation)
            problem["problem_id"] = len(expanded) + 1
            expanded.append(problem)

        return expanded

    def expand_to_900(self, base_600: List[Dict]) -> List[Dict]:
        """600問を900問に拡張"""
        expanded = base_600.copy()

        # 全テーマ×全パターンの組み合わせから生成
        all_combinations = []
        for theme in self.themes:
            for pattern in self.patterns:
                all_combinations.append((theme, pattern))

        # ランダムに300個の組み合わせを選択
        selected_combinations = random.sample(all_combinations, min(300, len(all_combinations)))

        for theme, pattern in selected_combinations:
            # バリエーションを決定
            if theme["category"] in ["遊技機管理", "不正対策"]:
                variation = random.choice(["detail", "specific", "exception"])
            else:
                variation = random.choice(["inverse", "negative"])

            problem = self.create_variation(theme, pattern, variation)
            problem["problem_id"] = len(expanded) + 1
            expanded.append(problem)

        return expanded[:900]  # 900問でカット

    def optimize_distribution(self, problems: List[Dict]) -> List[Dict]:
        """カテゴリ・難易度の分布を最適化"""

        # カテゴリごとに分類
        categorized = {}
        for problem in problems:
            cat = problem["category"]
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(problem)

        # 理想的な配分
        ideal_distribution = {
            "遊技機管理": int(len(problems) * 0.40),  # 40%
            "不正対策": int(len(problems) * 0.20),     # 20%
            "営業許可関連": int(len(problems) * 0.15), # 15%
            "営業時間・規制": int(len(problems) * 0.10), # 10%
            "型式検定関連": int(len(problems) * 0.08),  # 8%
            "景品規制": int(len(problems) * 0.07)       # 7%
        }

        # 最適化された問題リスト
        optimized = []

        for category, target_count in ideal_distribution.items():
            if category in categorized:
                available = categorized[category]
                if len(available) >= target_count:
                    selected = random.sample(available, target_count)
                else:
                    selected = available
                    # 不足分は生成
                    shortage = target_count - len(available)
                    theme_list = [t for t in self.themes if t["category"] == category]
                    if theme_list:
                        for _ in range(shortage):
                            theme = random.choice(theme_list)
                            pattern = random.choice(self.patterns)
                            problem = self.generate_problem(theme, pattern)
                            problem["problem_id"] = len(optimized) + 1
                            selected.append(problem)

                optimized.extend(selected)

        # ID再振り
        for i, problem in enumerate(optimized, 1):
            problem["problem_id"] = i

        return optimized

    def convert_to_app_format(self, problems: List[Dict]) -> List[Dict]:
        """アプリ形式に変換"""
        difficulty_map = {
            '★': 'easy',
            '★★': 'medium',
            '★★★': 'hard',
            '★★★★': 'expert'
        }

        converted = []
        for problem in problems:
            converted.append({
                'id': f"q{problem['problem_id']:04d}",
                'statement': problem['problem_text'],
                'answer': problem['correct_answer'] == "○",
                'difficulty': difficulty_map.get(problem.get('difficulty', '★'), 'easy'),
                'category': problem['category'],
                'explanation': problem['explanation'],
                'source': problem.get('legal_reference', '')
            })

        return converted


def main():
    """メイン処理"""
    print("🚀 OPUS拡張生成システム起動")
    print("-" * 50)

    # 既存の300問を読み込み
    print("\n📂 OPUS基盤300問を読み込み中...")
    with open('/home/planj/patshinko-exam-app/data/opus_300_problems_20251023_114029.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    base_300 = data['problems']
    print(f"✅ {len(base_300)}問を読み込みました")

    # 拡張生成器を初期化
    generator = OpusExpansionGenerator()

    # 600問に拡張
    print("\n⚡ 300問→600問に拡張中...")
    problems_600 = generator.expand_to_600(base_300)
    print(f"✅ {len(problems_600)}問に拡張完了")

    # 900問に拡張
    print("\n⚡ 600問→900問に拡張中...")
    problems_900 = generator.expand_to_900(problems_600)
    print(f"✅ {len(problems_900)}問に拡張完了")

    # 分布を最適化
    print("\n🔧 カテゴリ分布を最適化中...")
    optimized_problems = generator.optimize_distribution(problems_900)
    print(f"✅ 最適化完了: {len(optimized_problems)}問")

    # アプリ形式に変換
    print("\n🔄 アプリ形式に変換中...")
    app_format_problems = generator.convert_to_app_format(optimized_problems)

    # 統計表示
    print("\n" + "="*50)
    print("📊 最終生成結果")
    print("="*50)

    # カテゴリ分布
    cat_dist = {}
    for p in optimized_problems:
        cat = p["category"]
        cat_dist[cat] = cat_dist.get(cat, 0) + 1

    print("\n【カテゴリ分布】")
    for cat, count in sorted(cat_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(optimized_problems)) * 100
        print(f"  {cat}: {count}問 ({percentage:.1f}%)")

    # 難易度分布
    diff_dist = {}
    for p in optimized_problems:
        diff = p.get("difficulty", "★")
        diff_dist[diff] = diff_dist.get(diff, 0) + 1

    print("\n【難易度分布】")
    for diff, count in sorted(diff_dist.items()):
        percentage = (count / len(optimized_problems)) * 100
        print(f"  {diff}: {count}問 ({percentage:.1f}%)")

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # OPUS形式で保存
    opus_output = {
        "metadata": {
            "version": "2.0.0",
            "generator": "OPUS Expansion Generator",
            "created_at": datetime.now().isoformat(),
            "total_problems": len(optimized_problems),
            "base_problems": 300,
            "expansion_method": "theme_pattern_variation",
            "category_distribution": cat_dist,
            "difficulty_distribution": diff_dist
        },
        "problems": optimized_problems
    }

    opus_file = f'/home/planj/patshinko-exam-app/data/opus_900_expanded_{timestamp}.json'
    with open(opus_file, 'w', encoding='utf-8') as f:
        json.dump(opus_output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 OPUS形式で保存: {opus_file}")

    # アプリ形式で保存
    app_output = {
        "metadata": {
            "version": "2.0.0",
            "generator": "OPUS Expansion Generator",
            "created_at": datetime.now().isoformat(),
            "total_problems": len(app_format_problems)
        },
        "problems": app_format_problems
    }

    app_file = '/home/planj/patshinko-exam-app/public/mock_problems_opus_final.json'
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(app_output, f, ensure_ascii=False, indent=2)
    print(f"💾 アプリ形式で保存: {app_file}")

    # サンプル表示
    print("\n【生成例（ランダム3問）】")
    samples = random.sample(optimized_problems, 3)
    for i, problem in enumerate(samples, 1):
        print(f"\n問題{i}: {problem['problem_text']}")
        print(f"正解: {problem['correct_answer']}")
        print(f"解説: {problem['explanation']}")
        print(f"カテゴリ: {problem['category']} / 難易度: {problem.get('difficulty', '★')}")

    print("\n✅ 処理完了！900問の高品質問題セットが生成されました。")


if __name__ == "__main__":
    main()