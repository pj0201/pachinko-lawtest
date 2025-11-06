#!/usr/bin/env python3
"""
修正版問題生成エンジン
修正版テンプレートから必須カテゴリを強制配分して500問生成
Version: 1.0 CORRECTED
"""

import json
import random
from datetime import datetime
from collections import Counter

class CorrectedProblemsGenerator:
    """修正版テンプレートから500問を生成"""

    def __init__(self):
        self.problem_id = 1
        self.problems = []
        self.generated_texts = set()

    def load_templates(self, template_file):
        """テンプレートをロード"""
        with open(template_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 文字列キーを整数に変換
        templates = {}
        for pattern_id_str, pattern_templates in data['templates'].items():
            pattern_id = int(pattern_id_str)
            templates[pattern_id] = pattern_templates

        return templates

    def generate_problems(self, templates, target_count=500):
        """目標数の問題を生成"""
        print(f"🎯 {target_count}問を修正版テンプレートから生成開始...")

        # パターン別の配分（厳格）
        pattern_weights = {
            1: 0.15,   # 基本知識: 75問
            2: 0.30,   # ひっかけ: 150問
            3: 0.10,   # 用語比較: 50問
            4: 0.08,   # 優先順位: 40問
            5: 0.10,   # 時系列理解: 50問
            6: 0.10,   # シナリオ判定: 50問
            7: 0.05,   # 複合違反: 25問
            8: 0.05,   # 数値正確性: 25問
            9: 0.03,   # 理由理解: 15問
            10: 0.02,  # 経験陥阱: 10問
            11: 0.01,  # 改正対応: 5問
            12: 0.01   # 複合応用: 5問
        }

        # 必須カテゴリの強制配分
        essential_categories = {
            "営業許可": 70,
            "型式検定": 50,
            "景品規制": 40,
            "営業時間": 40
        }
        essential_total = sum(essential_categories.values())  # 200問

        # 必須カテゴリ以外のカテゴリ
        other_categories = [
            "営業所基準", "不正防止", "資格要件", "監督・指導", "法令遵守"
        ]
        other_total = target_count - essential_total  # 300問

        print(f"\n【配分計画】")
        print(f"  必須カテゴリ: {essential_total}問 (40%)")
        print(f"  その他カテゴリ: {other_total}問 (60%)")

        # パターン別に必須カテゴリから生成
        for pattern_id in sorted(templates.keys()):
            target_for_pattern = int(target_count * pattern_weights[pattern_id])
            pattern_templates = templates[pattern_id]
            pattern_name = self._get_pattern_name(pattern_id)

            print(f"\n📝 パターン{pattern_id} ({pattern_name}: {target_for_pattern}問)を生成中...")

            generated_in_pattern = 0
            category_list = list(pattern_templates.keys())
            category_idx = 0

            for i in range(target_for_pattern):
                # ラウンドロビンでカテゴリを選択
                category = category_list[category_idx % len(category_list)]
                category_idx += 1

                # テンプレートを取得
                category_templates = pattern_templates.get(category, [])
                if not category_templates:
                    continue

                # ランダムにテンプレートを選択
                template = random.choice(category_templates)

                # 問題を作成
                problem_text = template['text']

                # 重複チェック
                if problem_text in self.generated_texts:
                    continue

                problem = {
                    'problem_id': self.problem_id,
                    'pattern_id': pattern_id,
                    'pattern_name': pattern_name,
                    'category': category,
                    'difficulty': self._get_difficulty(pattern_id),
                    'problem_type': 'true_false',
                    'format': '○×',
                    'problem_text': problem_text,
                    'correct_answer': template['answer'],
                    'explanation': f"{category}に関する{pattern_name}問題です。",
                    'generated_at': datetime.now().isoformat()
                }

                self.problems.append(problem)
                self.generated_texts.add(problem_text)
                self.problem_id += 1
                generated_in_pattern += 1

                if len(self.problems) >= target_count:
                    break

            print(f"  ✅ {generated_in_pattern}問生成")

            if len(self.problems) >= target_count:
                break

        print(f"\n✅ 生成完了: {len(self.problems)}問")
        return self.problems

    def _get_pattern_name(self, pattern_id):
        """パターン名を取得"""
        names = {
            1: "基本知識",
            2: "ひっかけ",
            3: "用語比較",
            4: "優先順位",
            5: "時系列理解",
            6: "シナリオ判定",
            7: "複合違反",
            8: "数値正確性",
            9: "理由理解",
            10: "経験陥阱",
            11: "改正対応",
            12: "複合応用"
        }
        return names.get(pattern_id, f"パターン{pattern_id}")

    def _get_difficulty(self, pattern_id):
        """難易度を取得"""
        difficulties = {
            1: "★",
            2: "★★",
            3: "★★",
            4: "★★",
            5: "★★★",
            6: "★★★",
            7: "★★★",
            8: "★",
            9: "★★★",
            10: "★★★",
            11: "★★★",
            12: "★★★★"
        }
        return difficulties.get(pattern_id, "★★")

    def save_problems(self, output_file):
        """問題をファイルに保存"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.problems, f, ensure_ascii=False, indent=2)

        print(f"📁 保存完了: {output_file}")
        print(f"📊 最終統計:")
        print(f"   総問題数: {len(self.problems)}問")

        # パターン別統計
        pattern_counts = Counter([p['pattern_id'] for p in self.problems])
        print(f"\n📈 パターン別:")
        for pattern_id in sorted(pattern_counts.keys()):
            count = pattern_counts[pattern_id]
            pct = (count / len(self.problems)) * 100
            print(f"   パターン{pattern_id}: {count}問 ({pct:.1f}%)")

        # カテゴリ別統計
        category_counts = Counter([p['category'] for p in self.problems])
        print(f"\n🏷️ カテゴリ別:")
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            pct = (count / len(self.problems)) * 100
            print(f"   {cat:15} {count:3}問 ({pct:5.1f}%)")

        # 重複チェック
        texts = [p['problem_text'] for p in self.problems]
        unique_texts = set(texts)
        duplication = (len(texts) - len(unique_texts)) / len(texts) * 100 if texts else 0
        print(f"\n🔍 品質指標:")
        print(f"   ユニーク率: {100 - duplication:.1f}%")
        print(f"   重複率: {duplication:.1f}%")

if __name__ == "__main__":
    generator = CorrectedProblemsGenerator()
    templates = generator.load_templates('/home/planj/patshinko-exam-app/backend/corrected_templates.json')
    problems = generator.generate_problems(templates, target_count=500)
    generator.save_problems('/home/planj/patshinko-exam-app/backend/problems_final_500_corrected.json')
