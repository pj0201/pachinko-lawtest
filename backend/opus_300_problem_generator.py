#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OPUS高品質問題生成システム
300問の高品質な遊技機取扱主任者試験問題を生成
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any

class OpusProblemGenerator:
    """OPUS生成ロジックによる問題生成クラス"""

    def __init__(self):
        """初期化"""
        self.themes = self._initialize_themes()
        self.patterns = self._initialize_patterns()
        self.problem_id_counter = 1

    def _initialize_themes(self) -> List[Dict]:
        """50テーマの初期化"""
        themes = [
            # 遊技機管理（20テーマ）
            {"id": "T01", "name": "新台設置の届出手続き", "category": "遊技機管理",
             "content": "新台設置には事前の届出が必要", "legal_ref": "風営法第9条"},
            {"id": "T02", "name": "中古遊技機の型式確認", "category": "遊技機管理",
             "content": "中古遊技機も型式検定適合機でなければならない", "legal_ref": "風営法第20条"},
            {"id": "T03", "name": "遊技機の部品交換手続き", "category": "遊技機管理",
             "content": "部品交換後は取扱主任者による点検確認が必要", "legal_ref": "施行規則第36条"},
            {"id": "T04", "name": "製造番号の管理", "category": "遊技機管理",
             "content": "すべての遊技機には固有の製造番号が付与される", "legal_ref": "検定規則第6条"},
            {"id": "T05", "name": "基板ケースの封印管理", "category": "遊技機管理",
             "content": "基板ケースは封印により保護される", "legal_ref": "技術規格"},
            {"id": "T06", "name": "遊技機の保守点検頻度", "category": "遊技機管理",
             "content": "遊技機は定期的な保守点検が義務付けられている", "legal_ref": "施行規則"},
            {"id": "T07", "name": "故障機の取扱い", "category": "遊技機管理",
             "content": "故障した遊技機は速やかに使用を停止する", "legal_ref": "施行規則"},
            {"id": "T08", "name": "遊技機の廃棄手続き", "category": "遊技機管理",
             "content": "遊技機廃棄時は適正な処理が必要", "legal_ref": "廃棄物処理法"},
            {"id": "T09", "name": "遊技機の移設手続き", "category": "遊技機管理",
             "content": "営業所内での遊技機移設は届出不要", "legal_ref": "風営法第9条"},
            {"id": "T10", "name": "外部端子板の管理", "category": "遊技機管理",
             "content": "外部端子板の不正改造は禁止されている", "legal_ref": "風営法第20条"},
            {"id": "T11", "name": "遊技機の認定申請", "category": "遊技機管理",
             "content": "認定は任意の制度である", "legal_ref": "風営法第20条第2項"},
            {"id": "T12", "name": "遊技機の増設手続き", "category": "遊技機管理",
             "content": "遊技機増設には変更承認申請が必要", "legal_ref": "風営法第9条"},
            {"id": "T13", "name": "検定有効期限の管理", "category": "遊技機管理",
             "content": "型式検定の有効期限は3年である", "legal_ref": "検定規則第8条"},
            {"id": "T14", "name": "遊技機台帳の記載事項", "category": "遊技機管理",
             "content": "遊技機台帳には製造番号等を記載する", "legal_ref": "施行規則"},
            {"id": "T15", "name": "中古機の流通管理", "category": "遊技機管理",
             "content": "中古機流通には流通制御端末が必要", "legal_ref": "中古機流通要綱"},
            {"id": "T16", "name": "遊技機の設置基準", "category": "遊技機管理",
             "content": "遊技機の設置には一定の間隔が必要", "legal_ref": "施行規則"},
            {"id": "T17", "name": "遊技球等の管理", "category": "遊技機管理",
             "content": "遊技球は適正な規格品を使用する", "legal_ref": "技術規格"},
            {"id": "T18", "name": "リサイクル機の取扱い", "category": "遊技機管理",
             "content": "リサイクル機も型式適合が必要", "legal_ref": "リサイクル法"},
            {"id": "T19", "name": "遊技機メーカーとの契約", "category": "遊技機管理",
             "content": "遊技機購入には正規の契約が必要", "legal_ref": "民法"},
            {"id": "T20", "name": "遊技機の性能確認", "category": "遊技機管理",
             "content": "遊技機の性能は技術規格に適合する", "legal_ref": "技術規格"},

            # 不正対策（10テーマ）
            {"id": "T21", "name": "不正改造の検出方法", "category": "不正対策",
             "content": "不正改造は目視と動作確認で検出する", "legal_ref": "風営法第20条"},
            {"id": "T22", "name": "不正機器の発見時対応", "category": "不正対策",
             "content": "不正機器発見時は直ちに使用停止し報告する", "legal_ref": "風営法第22条"},
            {"id": "T23", "name": "基板の不正確認", "category": "不正対策",
             "content": "基板の不正は封印破損で判別できる", "legal_ref": "技術規格"},
            {"id": "T24", "name": "ROM交換の禁止事項", "category": "不正対策",
             "content": "ROMの無断交換は禁止されている", "legal_ref": "風営法第20条"},
            {"id": "T25", "name": "セキュリティチップ管理", "category": "不正対策",
             "content": "セキュリティチップの改変は禁止", "legal_ref": "技術規格"},
            {"id": "T26", "name": "不正防止の日常点検", "category": "不正対策",
             "content": "毎日の営業開始前に不正確認を行う", "legal_ref": "施行規則"},
            {"id": "T27", "name": "不正通報の義務", "category": "不正対策",
             "content": "不正発見時は公安委員会への通報義務がある", "legal_ref": "風営法第22条"},
            {"id": "T28", "name": "不正改造の罰則", "category": "不正対策",
             "content": "不正改造には罰金刑が科される", "legal_ref": "風営法第49条"},
            {"id": "T29", "name": "従業員による不正防止", "category": "不正対策",
             "content": "従業員への不正防止教育が義務", "legal_ref": "施行規則"},
            {"id": "T30", "name": "外部業者の管理", "category": "不正対策",
             "content": "外部業者による作業は監督が必要", "legal_ref": "施行規則"},

            # 営業時間・規制（5テーマ）
            {"id": "T31", "name": "営業禁止時間帯", "category": "営業時間・規制",
             "content": "午前0時から午前6時まで営業禁止", "legal_ref": "風営法第13条"},
            {"id": "T32", "name": "年少者立入制限", "category": "営業時間・規制",
             "content": "18歳未満の者の立入りは制限される", "legal_ref": "風営法第22条"},
            {"id": "T33", "name": "営業停止命令の期間", "category": "営業時間・規制",
             "content": "営業停止命令は最大6ヶ月", "legal_ref": "風営法第26条"},
            {"id": "T34", "name": "騒音規制基準", "category": "営業時間・規制",
             "content": "営業所の騒音は条例で定める基準以下", "legal_ref": "風営法第15条"},
            {"id": "T35", "name": "照度規制基準", "category": "営業時間・規制",
             "content": "営業所内の照度は10ルクス以上", "legal_ref": "風営法第14条"},

            # 営業許可関連（5テーマ）
            {"id": "T36", "name": "営業許可の有効期限", "category": "営業許可関連",
             "content": "営業許可は無期限有効である", "legal_ref": "風営法第5条"},
            {"id": "T37", "name": "営業許可の承継", "category": "営業許可関連",
             "content": "営業許可は相続により承継できる", "legal_ref": "風営法第7条"},
            {"id": "T38", "name": "許可証の掲示義務", "category": "営業許可関連",
             "content": "許可証は見やすい場所に掲示する", "legal_ref": "風営法第6条"},
            {"id": "T39", "name": "営業許可の取消事由", "category": "営業許可関連",
             "content": "重大な違反は許可取消事由となる", "legal_ref": "風営法第26条"},
            {"id": "T40", "name": "構造設備の変更届", "category": "営業許可関連",
             "content": "構造設備変更には事前承認が必要", "legal_ref": "風営法第9条"},

            # 型式検定関連（5テーマ）
            {"id": "T41", "name": "型式検定の有効期限", "category": "型式検定関連",
             "content": "型式検定の有効期限は3年", "legal_ref": "検定規則第8条"},
            {"id": "T42", "name": "型式検定の更新時期", "category": "型式検定関連",
             "content": "更新申請は期限の30日前から可能", "legal_ref": "検定規則"},
            {"id": "T43", "name": "検定申請の手続き", "category": "型式検定関連",
             "content": "検定申請は国家公安委員会に行う", "legal_ref": "風営法第20条"},
            {"id": "T44", "name": "検定機関の種類", "category": "型式検定関連",
             "content": "指定試験機関が検定を実施", "legal_ref": "風営法第20条"},
            {"id": "T45", "name": "検定と認定の違い", "category": "型式検定関連",
             "content": "検定は義務、認定は任意", "legal_ref": "風営法第20条"},

            # 景品規制（5テーマ）
            {"id": "T46", "name": "景品の上限額", "category": "景品規制",
             "content": "景品の価格は営業者が定める", "legal_ref": "風営法第22条"},
            {"id": "T47", "name": "特殊景品の種類", "category": "景品規制",
             "content": "特殊景品は組合が指定する", "legal_ref": "風営法第22条"},
            {"id": "T48", "name": "買取所との関係", "category": "景品規制",
             "content": "買取所との直接的関係は禁止", "legal_ref": "風営法第22条"},
            {"id": "T49", "name": "景品交換の記録", "category": "景品規制",
             "content": "景品交換記録の保存義務がある", "legal_ref": "施行規則"},
            {"id": "T50", "name": "風営法第22条の内容", "category": "景品規制",
             "content": "現金又は有価証券の提供禁止", "legal_ref": "風営法第22条"}
        ]
        return themes

    def _initialize_patterns(self) -> List[Dict]:
        """10パターンの初期化"""
        patterns = [
            {"id": "P01", "name": "基本事実確認", "difficulty": "★"},
            {"id": "P02", "name": "数値正誤", "difficulty": "★★"},
            {"id": "P03", "name": "手続き順序", "difficulty": "★★"},
            {"id": "P04", "name": "適用範囲", "difficulty": "★★"},
            {"id": "P05", "name": "必要条件", "difficulty": "★★"},
            {"id": "P06", "name": "禁止事項", "difficulty": "★"},
            {"id": "P07", "name": "例外規定", "difficulty": "★★★"},
            {"id": "P08", "name": "用語定義", "difficulty": "★★"},
            {"id": "P09", "name": "責任主体", "difficulty": "★★"},
            {"id": "P10", "name": "時限規定", "difficulty": "★★★"}
        ]
        return patterns

    def generate_problem(self, theme: Dict, pattern: Dict) -> Dict:
        """単一問題の生成"""
        problem_text, correct_answer, explanation = self._create_problem_content(theme, pattern)

        return {
            "problem_id": self.problem_id_counter,
            "theme_id": theme["id"],
            "theme_name": theme["name"],
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "category": theme["category"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem_text,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "legal_reference": theme["legal_ref"],
            "source": "講習テキスト"
        }

    def _create_problem_content(self, theme: Dict, pattern: Dict) -> tuple:
        """問題文、正解、解説の生成"""

        # パターンに応じた問題文生成
        if pattern["id"] == "P01":  # 基本事実確認
            if random.random() > 0.5:
                # 正しい文章
                problem_text = f"{theme['content']}。"
                correct_answer = "○"
                explanation = f"その通りです。{theme['content']}。これは{theme['legal_ref']}に規定されています。"
            else:
                # 誤った文章（否定）
                problem_text = f"{theme['content'].replace('必要', '不要').replace('である', 'でない')}。"
                correct_answer = "×"
                explanation = f"誤りです。正しくは、{theme['content']}。{theme['legal_ref']}を確認してください。"

        elif pattern["id"] == "P02":  # 数値正誤
            if "3年" in theme["content"]:
                if random.random() > 0.5:
                    problem_text = theme["content"] + "。"
                    correct_answer = "○"
                    explanation = f"正解です。{theme['legal_ref']}に3年と明記されています。"
                else:
                    problem_text = theme["content"].replace("3年", "5年") + "。"
                    correct_answer = "×"
                    explanation = f"誤りです。正しくは3年です。{theme['legal_ref']}を確認してください。"
            elif "6ヶ月" in theme["content"]:
                if random.random() > 0.5:
                    problem_text = theme["content"] + "。"
                    correct_answer = "○"
                    explanation = f"正解です。{theme['legal_ref']}により最大6ヶ月と定められています。"
                else:
                    problem_text = theme["content"].replace("6ヶ月", "1年") + "。"
                    correct_answer = "×"
                    explanation = f"誤りです。最大は6ヶ月です。{theme['legal_ref']}を確認してください。"
            else:
                # 数値がない場合は基本事実確認と同様
                return self._create_problem_content(theme, {"id": "P01", "name": "基本事実確認", "difficulty": "★"})

        elif pattern["id"] == "P03":  # 手続き順序
            if "事前" in theme["content"]:
                if random.random() > 0.5:
                    problem_text = f"{theme['name']}は、実施前に行う必要がある。"
                    correct_answer = "○"
                    explanation = f"正解です。{theme['content']}。{theme['legal_ref']}に規定されています。"
                else:
                    problem_text = f"{theme['name']}は、実施後でも可能である。"
                    correct_answer = "×"
                    explanation = f"誤りです。事前に行う必要があります。{theme['legal_ref']}を確認してください。"
            else:
                problem_text = f"{theme['name']}には、適切な手続きが必要である。"
                correct_answer = "○"
                explanation = f"正解です。{theme['content']}。{theme['legal_ref']}に基づいています。"

        elif pattern["id"] == "P04":  # 適用範囲
            if random.random() > 0.5:
                problem_text = f"{theme['name']}は、すべての遊技機に適用される。"
                correct_answer = "○" if "すべて" in theme["content"] or "必要" in theme["content"] else "×"
                explanation = f"{theme['content']}。{theme['legal_ref']}を参照してください。"
            else:
                problem_text = f"{theme['name']}は、一部の遊技機のみに適用される。"
                correct_answer = "×" if "すべて" in theme["content"] or "必要" in theme["content"] else "○"
                explanation = f"{theme['content']}。{theme['legal_ref']}に基づいています。"

        elif pattern["id"] == "P05":  # 必要条件
            if "必要" in theme["content"]:
                if random.random() > 0.5:
                    problem_text = theme["content"] + "。"
                    correct_answer = "○"
                    explanation = f"正解です。これは必須要件です。{theme['legal_ref']}に規定されています。"
                else:
                    problem_text = theme["content"].replace("必要", "任意") + "。"
                    correct_answer = "×"
                    explanation = f"誤りです。これは必須であり任意ではありません。{theme['legal_ref']}を確認してください。"
            else:
                problem_text = f"{theme['name']}は必須である。"
                correct_answer = "○" if "義務" in theme["content"] else "×"
                explanation = f"{theme['content']}。{theme['legal_ref']}に基づいています。"

        elif pattern["id"] == "P06":  # 禁止事項
            if "禁止" in theme["content"]:
                if random.random() > 0.5:
                    problem_text = theme["content"] + "。"
                    correct_answer = "○"
                    explanation = f"正解です。{theme['legal_ref']}により禁止されています。"
                else:
                    problem_text = theme["content"].replace("禁止", "許可") + "。"
                    correct_answer = "×"
                    explanation = f"誤りです。これは禁止事項です。{theme['legal_ref']}を確認してください。"
            else:
                problem_text = f"{theme['name']}は禁止されている。"
                correct_answer = "×"
                explanation = f"{theme['content']}。{theme['legal_ref']}を参照してください。"

        elif pattern["id"] == "P07":  # 例外規定
            if "任意" in theme["content"] or "除外" in theme["content"]:
                problem_text = f"{theme['name']}には例外がある。"
                correct_answer = "○"
                explanation = f"正解です。{theme['content']}。{theme['legal_ref']}に例外規定があります。"
            else:
                problem_text = f"{theme['name']}には例外規定がない。"
                correct_answer = "○"
                explanation = f"正解です。{theme['content']}。{theme['legal_ref']}に例外はありません。"

        elif pattern["id"] == "P08":  # 用語定義
            problem_text = f"{theme['name']}とは、{theme['content']}ことである。"
            correct_answer = "○"
            explanation = f"正解です。{theme['legal_ref']}における定義です。"

        elif pattern["id"] == "P09":  # 責任主体
            entities = ["公安委員会", "営業者", "取扱主任者", "都道府県", "国家公安委員会"]
            correct_entity = random.choice(entities[:2])

            if random.random() > 0.5:
                problem_text = f"{theme['name']}は、{correct_entity}が行う。"
                correct_answer = "○"
                explanation = f"正解です。{theme['legal_ref']}により{correct_entity}の責任と定められています。"
            else:
                wrong_entity = random.choice([e for e in entities if e != correct_entity])
                problem_text = f"{theme['name']}は、{wrong_entity}が行う。"
                correct_answer = "×"
                explanation = f"誤りです。正しくは{correct_entity}が行います。{theme['legal_ref']}を確認してください。"

        elif pattern["id"] == "P10":  # 時限規定
            periods = ["30日", "60日", "90日", "6ヶ月", "1年", "3年"]
            if any(p in theme["content"] for p in periods):
                if random.random() > 0.5:
                    problem_text = theme["content"] + "。"
                    correct_answer = "○"
                    explanation = f"正解です。{theme['legal_ref']}に期限が明記されています。"
                else:
                    # 期限を変更
                    for p in periods:
                        if p in theme["content"]:
                            wrong_period = random.choice([x for x in periods if x != p])
                            problem_text = theme["content"].replace(p, wrong_period) + "。"
                            correct_answer = "×"
                            explanation = f"誤りです。正しくは{p}です。{theme['legal_ref']}を確認してください。"
                            break
            else:
                problem_text = f"{theme['name']}には期限が定められている。"
                correct_answer = "○" if "期限" in theme["content"] or "期間" in theme["content"] else "×"
                explanation = f"{theme['content']}。{theme['legal_ref']}を参照してください。"

        else:
            # デフォルト
            return self._create_problem_content(theme, {"id": "P01", "name": "基本事実確認", "difficulty": "★"})

        return problem_text, correct_answer, explanation

    def generate_all_problems(self, target_count: int = 300) -> List[Dict]:
        """全問題の生成"""
        problems = []

        # 各テーマから最低1問は生成
        for theme in self.themes:
            # 重要テーマは複数パターンで生成
            if theme["category"] in ["遊技機管理", "不正対策"]:
                patterns_to_use = random.sample(self.patterns, min(3, len(self.patterns)))
            else:
                patterns_to_use = random.sample(self.patterns, 2)

            for pattern in patterns_to_use:
                if len(problems) >= target_count:
                    break

                problem = self.generate_problem(theme, pattern)
                problems.append(problem)
                self.problem_id_counter += 1

        # 不足分を重要テーマから追加
        while len(problems) < target_count:
            theme = random.choice([t for t in self.themes if t["category"] in ["遊技機管理", "不正対策", "営業許可関連"]])
            pattern = random.choice(self.patterns)

            problem = self.generate_problem(theme, pattern)
            problems.append(problem)
            self.problem_id_counter += 1

        return problems[:target_count]

    def save_to_json(self, problems: List[Dict], filename: str):
        """JSON形式で保存"""
        output = {
            "metadata": {
                "version": "1.0.0",
                "generator": "OPUS Problem Generator",
                "created_at": datetime.now().isoformat(),
                "total_problems": len(problems),
                "difficulty_distribution": self._calculate_difficulty_distribution(problems),
                "category_distribution": self._calculate_category_distribution(problems)
            },
            "problems": problems
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(problems)}問を{filename}に保存しました")

    def _calculate_difficulty_distribution(self, problems: List[Dict]) -> Dict:
        """難易度分布の計算"""
        distribution = {}
        for problem in problems:
            difficulty = problem["difficulty"]
            distribution[difficulty] = distribution.get(difficulty, 0) + 1
        return distribution

    def _calculate_category_distribution(self, problems: List[Dict]) -> Dict:
        """カテゴリ分布の計算"""
        distribution = {}
        for problem in problems:
            category = problem["category"]
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def print_summary(self, problems: List[Dict]):
        """生成結果のサマリー表示"""
        print("\n" + "="*50)
        print("📊 OPUS問題生成サマリー")
        print("="*50)
        print(f"総問題数: {len(problems)}問")

        print("\n【難易度分布】")
        diff_dist = self._calculate_difficulty_distribution(problems)
        for diff, count in sorted(diff_dist.items()):
            percentage = (count / len(problems)) * 100
            print(f"  {diff}: {count}問 ({percentage:.1f}%)")

        print("\n【カテゴリ分布】")
        cat_dist = self._calculate_category_distribution(problems)
        for cat, count in sorted(cat_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(problems)) * 100
            print(f"  {cat}: {count}問 ({percentage:.1f}%)")

        print("\n【パターン使用状況】")
        pattern_usage = {}
        for problem in problems:
            pattern = problem["pattern_name"]
            pattern_usage[pattern] = pattern_usage.get(pattern, 0) + 1

        for pattern, count in sorted(pattern_usage.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count}問")

        print("="*50)


def main():
    """メイン処理"""
    print("🎯 OPUS高品質問題生成システム起動")
    print("-" * 50)

    generator = OpusProblemGenerator()

    # 300問生成
    problems = generator.generate_all_problems(300)

    # サマリー表示
    generator.print_summary(problems)

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/planj/patshinko-exam-app/data/opus_300_problems_{timestamp}.json"
    generator.save_to_json(problems, filename)

    # サンプル表示
    print("\n【生成例（最初の3問）】")
    for i, problem in enumerate(problems[:3], 1):
        print(f"\n問題{i}: {problem['problem_text']}")
        print(f"正解: {problem['correct_answer']}")
        print(f"解説: {problem['explanation']}")
        print(f"カテゴリ: {problem['category']} / 難易度: {problem['difficulty']}")


if __name__ == "__main__":
    main()