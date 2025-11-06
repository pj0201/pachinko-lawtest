#!/usr/bin/env python3
"""
遊技機取扱主任者試験問題生成システム v3.0 DYNAMIC
動的テンプレート生成によるLLM活用版
Version: 3.0 DYNAMIC
Date: 2025-11-02
"""

import json
import random
import os
from datetime import datetime
from typing import Dict, List, Optional
import anthropic

class DynamicProblemsGeneratorV3:
    """LLMによる動的テンプレート生成版"""

    def __init__(self):
        """初期化"""
        self.categories = self._initialize_categories()
        self.patterns = self._initialize_patterns()
        self.problem_id_counter = 1
        self.problems = []
        self.generated_texts = set()

        # Claude API初期化
        self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def _initialize_categories(self) -> Dict:
        """カテゴリを初期化"""
        return {
            "営業許可": {"id": 1000, "articles": "第3条〜第8条"},
            "営業所基準": {"id": 2000, "articles": "第9条〜第10条"},
            "遊技機の設置": {"id": 3000, "articles": "第11条〜第15条"},
            "遊技機の認定": {"id": 4000, "articles": "第16条〜第20条"},
            "景品規制": {"id": 5000, "articles": "第21条〜第25条"},
            "営業時間": {"id": 6000, "articles": "第26条〜第30条"},
            "不正防止": {"id": 7000, "articles": "第31条〜第35条"},
            "監督・指導": {"id": 8000, "articles": "第36条〜第40条"},
            "資格要件": {"id": 9000, "articles": "第41条〜第45条"},
            "法改正": {"id": 10000, "articles": "最新改正事項"}
        }

    def _initialize_patterns(self) -> Dict:
        """12パターンを初期化"""
        return {
            1: {"name": "基本知識", "difficulty": "★", "weight": 0.15},
            2: {"name": "ひっかけ", "difficulty": "★★", "weight": 0.30},
            3: {"name": "用語比較", "difficulty": "★★", "weight": 0.10},
            4: {"name": "優先順位", "difficulty": "★★", "weight": 0.08},
            5: {"name": "時系列理解", "difficulty": "★★★", "weight": 0.10},
            6: {"name": "シナリオ判定", "difficulty": "★★★", "weight": 0.10},
            7: {"name": "複合違反", "difficulty": "★★★", "weight": 0.05},
            8: {"name": "数値正確性", "difficulty": "★", "weight": 0.05},
            9: {"name": "理由理解", "difficulty": "★★★", "weight": 0.03},
            10: {"name": "経験陥阱", "difficulty": "★★★", "weight": 0.02},
            11: {"name": "改正対応", "difficulty": "★★★", "weight": 0.01},
            12: {"name": "複合応用", "difficulty": "★★★★", "weight": 0.01}
        }

    def generate_problem_by_llm(self, category: str, pattern_id: int, pattern_name: str) -> Optional[Dict]:
        """LLMを使って問題を動的生成"""

        pattern_prompts = {
            1: f"遊技機取扱主任者試験の『基本知識』問題を生成してください。カテゴリ: {category}。風営法の基本的な内容を述べた○×問題を1問生成。",
            2: f"『ひっかけ問題』を生成してください。カテゴリ: {category}。絶対表現（必ず、絶対に、常に等）を含み、実際には例外がある内容の×問。",
            3: f"『用語比較』問題を生成してください。カテゴリ: {category}。営業許可と型式検定など、異なる概念の違いを説明する問題。",
            4: f"『優先順位』問題を生成してください。カテゴリ: {category}。複数の手続きで実施順序が重要なシナリオ。",
            5: f"『時系列理解』問題を生成してください。カテゴリ: {category}。許可取得から更新申請まで、時間経過による変化。",
            6: f"『シナリオ判定』問題を生成してください。カテゴリ: {category}。実務的な場面で、判断が必要な状況。",
            7: f"『複合違反』問題を生成してください。カテゴリ: {category}。複数の規制違反が同時に発生した場合の罰則。",
            8: f"『数値正確性』問題を生成してください。カテゴリ: {category}。期限、距離、金額など、法定数値の正確性。",
            9: f"『理由理解』問題を生成してください。カテゴリ: {category}。なぜこの規制が必要か、その理由を理解する問題。",
            10: f"『経験陥阱』問題を生成してください。カテゴリ: {category}。実務では一般的だが、法制上は異なる場合。",
            11: f"『改正対応』問題を生成してください。カテゴリ: {category}。最近の法改正による新規定。",
            12: f"『複合応用』問題を生成してください。カテゴリ: {category}。複数の知識を統合した応用問題。"
        }

        prompt = prompt_template = f"""
あなたは遊技機取扱主任者試験の問題作成専門家です。

【要件】
{pattern_prompts.get(pattern_id, '')}

【出力形式】
必ずJSON形式で以下の構造で返してください。複数行の説明は不要です。

{{
    "problem_text": "問題文（簡潔に）",
    "correct_answer": "○" または "×",
    "explanation": "解説（1-2文）"
}}

【注意】
- 問題文は実際に試験に出そうな内容で、40-60字程度
- ひっかけ問題は「必ず」「絶対に」「常に」などの絶対表現を含める
- 回答は○ または × のみ
- JSONのみ出力（説明文不要）
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # レスポンスを解析
            response_text = message.content[0].text.strip()

            # JSONを抽出
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                problem_data = json.loads(json_str)

                # 問題オブジェクトを構築
                problem = {
                    'problem_id': self.problem_id_counter,
                    'pattern_id': pattern_id,
                    'pattern_name': pattern_name,
                    'category': category,
                    'difficulty': self.patterns[pattern_id]['difficulty'],
                    'problem_type': 'true_false',
                    'format': '○×',
                    'problem_text': problem_data.get('problem_text', ''),
                    'correct_answer': problem_data.get('correct_answer', ''),
                    'explanation': problem_data.get('explanation', ''),
                    'generated_at': datetime.now().isoformat(),
                    'generated_by': 'claude-3.5-sonnet'
                }

                self.problem_id_counter += 1
                return problem

        except Exception as e:
            print(f"⚠️ LLM生成エラー({category}/{pattern_name}): {str(e)}")
            return None

    def generate_problems(self, target_count: int = 500) -> List[Dict]:
        """目標数の問題をLLMで生成"""
        print(f"🎯 {target_count}問をLLMで動的生成開始...")

        # パターン別の生成数を計算
        pattern_distribution = {}
        for pattern_id, pattern in self.patterns.items():
            count = int(target_count * pattern["weight"])
            pattern_distribution[pattern_id] = count

        category_list = list(self.categories.keys())
        category_count = len(category_list)

        # パターンごとに生成
        for pattern_id in sorted(self.patterns.keys()):
            pattern_name = self.patterns[pattern_id]["name"]
            total_for_pattern = pattern_distribution[pattern_id]

            print(f"\n📝 {pattern_name} ({total_for_pattern}問)を生成中...", end="")

            generated_in_pattern = 0
            for i in range(total_for_pattern):
                category = category_list[i % category_count]

                # LLMで生成
                problem = self.generate_problem_by_llm(category, pattern_id, pattern_name)

                if problem and problem['problem_text'] not in self.generated_texts:
                    self.problems.append(problem)
                    self.generated_texts.add(problem['problem_text'])
                    generated_in_pattern += 1

                # 進捗表示
                if (i + 1) % 5 == 0:
                    print(f".", end="", flush=True)

            print(f" ✅ {generated_in_pattern}問生成")

        print(f"\n✅ 生成完了: {len(self.problems)}問（重複排除済み）")
        return self.problems

    def save_problems(self, output_file: str):
        """問題をファイルに保存"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.problems, f, ensure_ascii=False, indent=2)
        print(f"📁 保存完了: {output_file}")
        print(f"📊 統計: 合計 {len(self.problems)} 問")

if __name__ == "__main__":
    generator = DynamicProblemsGeneratorV3()
    problems = generator.generate_problems(target_count=500)
    generator.save_problems('/home/planj/patshinko-exam-app/backend/problems_driving_logic_v3_dynamic.json')
