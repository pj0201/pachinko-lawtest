#!/usr/bin/env python3
"""
遊技機取扱主任者試験問題生成システム
運転免許学科試験のロジックを応用した風営法準拠の問題生成
Version: 2.0
Date: 2025-11-02
"""

import json
import random
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os

class DrivingLicenseLogicGenerator:
    """運転免許式ロジックによる問題生成クラス"""

    def __init__(self):
        """初期化"""
        self.categories = self._initialize_categories()
        self.patterns = self._initialize_patterns()
        self.legal_terms = self._initialize_legal_terms()
        self.problem_id_counter = 1
        self.problems = []

    def _initialize_categories(self) -> Dict:
        """風営法ベースのカテゴリー体系（7層構造）"""
        return {
            "営業許可": {
                "id": 1000,
                "articles": "第3条〜第8条",
                "topics": [
                    "営業許可の要件",
                    "営業許可の申請手続き",
                    "許可の制限",
                    "欠格事由",
                    "相続による承継"
                ],
                "target_count": 100  # 500問のうち100問
            },
            "営業所基準": {
                "id": 2000,
                "articles": "第9条〜第10条",
                "topics": [
                    "営業所の構造及び設備",
                    "営業所の場所的制限",
                    "学校・病院等からの距離",
                    "設備の技術上の基準"
                ],
                "target_count": 75
            },
            "遊技機規制": {
                "id": 3000,
                "articles": "第20条〜第20条の2",
                "topics": [
                    "遊技機の型式検定",
                    "遊技機の設置届出",
                    "遊技機の変更・撤去",
                    "認定及び型式の表示",
                    "検定の有効期間"
                ],
                "target_count": 110
            },
            "営業規制": {
                "id": 4000,
                "articles": "第13条〜第19条",
                "topics": [
                    "営業時間の制限",
                    "照度の規制",
                    "騒音及び振動の規制",
                    "広告及び宣伝の規制",
                    "遊技料金・賞品の規制"
                ],
                "target_count": 90
            },
            "従業者管理": {
                "id": 5000,
                "articles": "第22条〜第26条",
                "topics": [
                    "年少者の立入禁止",
                    "18歳未満者の雇用禁止",
                    "管理者の選任",
                    "従業者名簿",
                    "報告義務"
                ],
                "target_count": 75
            },
            "監督・処分": {
                "id": 6000,
                "articles": "第30条〜第35条",
                "topics": [
                    "指示処分",
                    "営業停止命令",
                    "許可の取消し",
                    "聴聞",
                    "報告及び立入検査"
                ],
                "target_count": 50
            }
        }

    def _initialize_patterns(self) -> Dict:
        """運転免許試験パターンの適用（10パターン）"""
        return {
            "絶対表現ひっかけ": {
                "id": 1,
                "weight": 30,  # 30%の出現率
                "description": "「必ず」「絶対」「全て」などの絶対表現による罠",
                "difficulty": "★★"
            },
            "用語の違い": {
                "id": 2,
                "weight": 20,
                "description": "似た用語の厳密な区別（許可vs届出、申請vs報告）",
                "difficulty": "★★"
            },
            "基本知識": {
                "id": 3,
                "weight": 15,
                "description": "法令条文の直接的な知識確認",
                "difficulty": "★"
            },
            "優先順位": {
                "id": 4,
                "weight": 12,
                "description": "複数ルール間の優先関係",
                "difficulty": "★★★"
            },
            "時間経過": {
                "id": 5,
                "weight": 8,
                "description": "期限・有効期間に関する問題",
                "difficulty": "★★"
            },
            "シナリオ判定": {
                "id": 6,
                "weight": 5,
                "description": "実務場面での適切な対応",
                "difficulty": "★★★"
            },
            "複合条件": {
                "id": 7,
                "weight": 5,
                "description": "複数条件が絡む複雑な判定",
                "difficulty": "★★★"
            },
            "数値暗記": {
                "id": 8,
                "weight": 3,
                "description": "具体的な数値の暗記（距離、金額、日数）",
                "difficulty": "★"
            },
            "例外規定": {
                "id": 9,
                "weight": 2,
                "description": "原則と例外の理解",
                "difficulty": "★★"
            }
        }

    def _initialize_legal_terms(self) -> Dict:
        """法律用語の定義（用語の違いパターン用）"""
        return {
            "許可": "行政庁が法令で一般的に禁止されている行為を特定の場合に解除する処分",
            "届出": "一定の事項を行政庁に通知する行為",
            "認可": "第三者の法律行為を補充してその効力を完成させる行政行為",
            "承認": "行政庁が特定の事実又は法律関係の存否を公に確認する行為",
            "申請": "行政庁に対し一定の処分を求める意思表示",
            "報告": "行政庁に対し事実を知らせる行為",
            "営業停止": "一定期間営業を禁止する処分",
            "許可取消": "与えた許可を将来に向かって失効させる処分",
            "指示": "改善を命じる行政指導",
            "遊技機": "ぱちんこ遊技機、回胴式遊技機等の総称",
            "賞品": "遊技の結果得た玉、メダル等と交換される物品",
            "景品": "賞品の別称（法令では主に賞品を使用）"
        }

    def generate_problem(self, category: str, pattern: str) -> Dict:
        """個別問題の生成"""
        problem_id = self.problem_id_counter
        self.problem_id_counter += 1

        category_info = self.categories[category]
        pattern_info = self.patterns[pattern]

        # パターンに応じた問題生成
        if pattern == "絶対表現ひっかけ":
            return self._generate_absolute_trap(problem_id, category_info, pattern_info)
        elif pattern == "用語の違い":
            return self._generate_term_difference(problem_id, category_info, pattern_info)
        elif pattern == "基本知識":
            return self._generate_basic_knowledge(problem_id, category_info, pattern_info)
        elif pattern == "優先順位":
            return self._generate_priority(problem_id, category_info, pattern_info)
        elif pattern == "時間経過":
            return self._generate_time_limit(problem_id, category_info, pattern_info)
        elif pattern == "シナリオ判定":
            return self._generate_scenario(problem_id, category_info, pattern_info)
        elif pattern == "複合条件":
            return self._generate_complex(problem_id, category_info, pattern_info)
        elif pattern == "数値暗記":
            return self._generate_numeric(problem_id, category_info, pattern_info)
        else:  # 例外規定
            return self._generate_exception(problem_id, category_info, pattern_info)

    def _generate_absolute_trap(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """絶対表現ひっかけ問題の生成"""

        # カテゴリ別のひっかけ問題テンプレート
        templates = {
            "営業許可": [
                {
                    "text": "風俗営業の許可申請は、必ず都道府県公安委員会に対して行わなければならない。",
                    "answer": "○",
                    "explanation": "風営法第3条により、風俗営業を営もうとする者は都道府県公安委員会の許可を受けなければならず、申請先も都道府県公安委員会です。「必ず」という表現は正しい。",
                    "trap": False
                },
                {
                    "text": "風俗営業の許可を受けた者は、いかなる場合でも営業所を移転することはできない。",
                    "answer": "×",
                    "explanation": "「いかなる場合でも」という絶対表現が誤り。営業所の移転は新たな許可申請により可能です。",
                    "trap": True
                }
            ],
            "遊技機規制": [
                {
                    "text": "遊技機の設置は、必ず設置日の7日前までに届出を行わなければならない。",
                    "answer": "×",
                    "explanation": "「必ず7日前」という絶対表現が誤り。風営法施行規則では「あらかじめ」届出が必要とされているが、厳密な日数は状況により異なる場合がある。",
                    "trap": True
                },
                {
                    "text": "型式検定に合格していない遊技機は、絶対に営業所に設置してはならない。",
                    "answer": "○",
                    "explanation": "風営法第20条により、型式検定に合格していない遊技機の設置は禁止されており、「絶対に」という表現は適切。",
                    "trap": False
                }
            ],
            "営業規制": [
                {
                    "text": "風俗営業者は、すべての営業日において営業時間を守らなければならない。",
                    "answer": "○",
                    "explanation": "営業時間の制限は風営法第13条で定められており、例外なく遵守が必要。「すべて」という表現は正しい。",
                    "trap": False
                },
                {
                    "text": "18歳未満の者は、いかなる時間帯でも風俗営業所に立ち入ることができない。",
                    "answer": "×",
                    "explanation": "「いかなる時間帯でも」が誤り。ゲームセンター等では時間制限があり、一定時間までは立入可能。",
                    "trap": True
                }
            ],
            "従業者管理": [
                {
                    "text": "管理者は、必ず営業所ごとに選任しなければならない。",
                    "answer": "○",
                    "explanation": "風営法第24条により、営業所ごとの管理者選任は義務であり、「必ず」は正しい。",
                    "trap": False
                },
                {
                    "text": "従業者名簿には、すべての個人情報を記載する必要がある。",
                    "answer": "×",
                    "explanation": "「すべての個人情報」は誤り。法令で定められた必要事項のみ記載すればよく、不必要な個人情報まで記載する必要はない。",
                    "trap": True
                }
            ],
            "営業所基準": [
                {
                    "text": "営業所は、学校から必ず100メートル以上離れていなければならない。",
                    "answer": "×",
                    "explanation": "「必ず100メートル」という絶対的な数値は誤り。都道府県の条例により距離規制は異なる。",
                    "trap": True
                }
            ],
            "監督・処分": [
                {
                    "text": "営業停止命令を受けた場合、絶対に営業を停止しなければならない。",
                    "answer": "○",
                    "explanation": "営業停止命令は行政処分であり、従わない場合は刑事罰の対象となるため、「絶対に」は正しい。",
                    "trap": False
                }
            ]
        }

        # カテゴリに応じた問題を選択
        category_name = list(category.keys())[0] if isinstance(category, dict) else category.get("id", "営業許可")

        # 実際のカテゴリ名の取得
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        if category_name in templates:
            template = random.choice(templates[category_name])
        else:
            template = random.choice(templates["営業許可"])

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": template["text"],
            "correct_answer": template["answer"],
            "explanation": template["explanation"],
            "is_trap": template.get("trap", False),
            "created_at": datetime.now().isoformat()
        }

    def _generate_term_difference(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """用語の違い問題の生成"""

        term_problems = [
            {
                "text": "風俗営業を営もうとする者は、都道府県公安委員会に届出をしなければならない。",
                "answer": "×",
                "explanation": "「届出」ではなく「許可」が必要。届出は事後的な通知、許可は事前の承認が必要な手続き。",
                "terms": ["届出", "許可"]
            },
            {
                "text": "遊技機を変更した場合は、都道府県公安委員会の認可を受けなければならない。",
                "answer": "×",
                "explanation": "「認可」ではなく「届出」が必要。遊技機の変更は届出事項。",
                "terms": ["認可", "届出"]
            },
            {
                "text": "営業者は、従業者名簿を作成し、都道府県公安委員会に申請しなければならない。",
                "answer": "×",
                "explanation": "従業者名簿は「備付け」義務はあるが、「申請」する必要はない。",
                "terms": ["申請", "備付け"]
            },
            {
                "text": "風俗営業者は、営業実績を定期的に都道府県公安委員会に報告しなければならない。",
                "answer": "×",
                "explanation": "定期的な「報告」義務はない。ただし、求められた場合の報告義務はある。",
                "terms": ["定期報告", "求めに応じた報告"]
            },
            {
                "text": "営業停止処分を受けた場合、許可が取消されたものとみなされる。",
                "answer": "×",
                "explanation": "「営業停止」は一時的な処分、「許可取消」は許可自体を失う処分で、別物。",
                "terms": ["営業停止", "許可取消"]
            }
        ]

        problem = random.choice(term_problems)

        # カテゴリ名の取得
        category_name = "営業許可"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "key_terms": problem["terms"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_basic_knowledge(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """基本知識問題の生成"""

        # カテゴリ名の取得
        category_name = "営業許可"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        knowledge_base = {
            "営業許可": [
                {
                    "text": "風俗営業を営もうとする者は、都道府県公安委員会の許可を受けなければならない。",
                    "answer": "○",
                    "explanation": "風営法第3条第1項に明記されている基本的な規定。"
                },
                {
                    "text": "風俗営業の許可の有効期間は3年間である。",
                    "answer": "×",
                    "explanation": "風俗営業の許可に有効期間の定めはない。一度許可を受ければ、取消等がない限り有効。"
                }
            ],
            "遊技機規制": [
                {
                    "text": "遊技機の型式検定は国家公安委員会が行う。",
                    "answer": "○",
                    "explanation": "風営法第20条により、遊技機の型式検定は国家公安委員会が実施。"
                },
                {
                    "text": "型式検定の有効期間は3年間である。",
                    "answer": "○",
                    "explanation": "型式検定の有効期間は3年間と定められている。"
                }
            ],
            "営業規制": [
                {
                    "text": "風俗営業の営業時間は、午前0時から翌日の午前6時まで禁止されている。",
                    "answer": "○",
                    "explanation": "風営法第13条により、深夜営業は原則禁止（地域により異なる場合あり）。"
                }
            ],
            "従業者管理": [
                {
                    "text": "18歳未満の者を風俗営業の業務に従事させることはできない。",
                    "answer": "○",
                    "explanation": "風営法第22条により、18歳未満者の雇用は禁止されている。"
                }
            ],
            "営業所基準": [
                {
                    "text": "営業所の構造及び設備は、技術上の基準に適合する必要がある。",
                    "answer": "○",
                    "explanation": "風営法第4条により、営業所は定められた基準を満たす必要がある。"
                }
            ],
            "監督・処分": [
                {
                    "text": "都道府県公安委員会は、必要に応じて営業所への立入検査を行うことができる。",
                    "answer": "○",
                    "explanation": "風営法第37条により、立入検査の権限が定められている。"
                }
            ]
        }

        if category_name in knowledge_base:
            problem = random.choice(knowledge_base[category_name])
        else:
            problem = random.choice(knowledge_base["営業許可"])

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_priority(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """優先順位問題の生成"""

        priority_problems = [
            {
                "text": "営業時間の制限について、都道府県の条例と風営法の規定が異なる場合、条例が優先される。",
                "answer": "×",
                "explanation": "風営法が上位法であり、条例は法律の範囲内でのみ有効。より厳しい制限を条例で定めることは可能。",
                "priority": "法律 > 条例"
            },
            {
                "text": "警察官の指示と営業許可の条件が矛盾する場合、警察官の指示に従う必要がある。",
                "answer": "○",
                "explanation": "現場での警察官の指示は、緊急性・公共の安全の観点から優先される。",
                "priority": "警察官の指示 > 許可条件"
            },
            {
                "text": "国家公安委員会規則と都道府県公安委員会規則が異なる場合、都道府県の規則が優先される。",
                "answer": "×",
                "explanation": "国家公安委員会規則が上位にあり、都道府県規則はその範囲内で定められる。",
                "priority": "国家公安委員会規則 > 都道府県公安委員会規則"
            }
        ]

        problem = random.choice(priority_problems)

        # カテゴリ名の取得
        category_name = "営業規制"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "priority_rule": problem["priority"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_time_limit(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """時間・期限問題の生成"""

        time_problems = [
            {
                "text": "遊技機の変更届は、変更後7日以内に行わなければならない。",
                "answer": "×",
                "explanation": "遊技機の変更は事前届出が必要。変更後ではなく、変更前に届出を行う。",
                "time": "事前届出"
            },
            {
                "text": "営業許可証の再交付申請は、紛失後30日以内に行う必要がある。",
                "answer": "×",
                "explanation": "許可証の紛失は速やかに届出が必要だが、「30日以内」という具体的な期限はない。",
                "time": "速やかに"
            },
            {
                "text": "従業者名簿は、従業者が退職してから3年間保存しなければならない。",
                "answer": "○",
                "explanation": "風営法施行規則により、従業者名簿は退職後3年間の保存義務がある。",
                "time": "3年間"
            },
            {
                "text": "営業停止処分の期間は、最長6月を超えることはない。",
                "answer": "○",
                "explanation": "風営法により、営業停止は6月を超えない範囲で定められる。",
                "time": "最長6月"
            }
        ]

        problem = random.choice(time_problems)

        # カテゴリ名の取得
        category_name = "営業規制"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "time_limit": problem["time"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_scenario(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """シナリオ判定問題の生成"""

        scenarios = [
            {
                "text": "営業中に未成年と思われる客が来店した場合、身分証の提示を求めずに入店させても問題ない。",
                "answer": "×",
                "explanation": "年齢確認は営業者の義務であり、未成年の可能性がある場合は必ず確認が必要。",
                "scenario": "年齢確認の実務"
            },
            {
                "text": "遊技機が故障した場合、修理完了まで該当機を使用禁止にすれば、届出は不要である。",
                "answer": "○",
                "explanation": "一時的な故障による使用停止は届出不要。ただし、機械の交換や大規模修理は届出が必要。",
                "scenario": "故障対応"
            },
            {
                "text": "台風で営業時間を短縮する場合、事前に都道府県公安委員会への届出が必要である。",
                "answer": "×",
                "explanation": "自然災害等による臨時的な営業時間短縮は届出不要。ただし、恒常的な変更は届出が必要。",
                "scenario": "緊急時対応"
            }
        ]

        problem = random.choice(scenarios)

        # カテゴリ名の取得
        category_name = "営業規制"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "scenario_type": problem["scenario"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_complex(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """複合条件問題の生成"""

        complex_problems = [
            {
                "text": "営業許可を受けており、かつ管理者を選任し、さらに従業者名簿を備えていれば、18歳未満の者を雇用できる。",
                "answer": "×",
                "explanation": "どれだけ条件を満たしても、18歳未満の雇用は絶対的に禁止されている。",
                "conditions": ["許可", "管理者", "名簿", "年齢制限"]
            },
            {
                "text": "営業時間内で、照度基準を満たし、騒音規制も守っていれば、どのような遊技機でも設置できる。",
                "answer": "×",
                "explanation": "型式検定に合格していない遊技機は、他の条件を満たしても設置できない。",
                "conditions": ["営業時間", "照度", "騒音", "型式検定"]
            }
        ]

        problem = random.choice(complex_problems)

        # カテゴリ名の取得
        category_name = "営業規制"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "conditions": problem["conditions"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_numeric(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """数値暗記問題の生成"""

        numeric_problems = [
            {
                "text": "営業所は、学校から最低50メートル離れていれば設置可能である。",
                "answer": "×",
                "explanation": "都道府県条例により異なるが、一般的に100メートル以上の距離が必要。",
                "number": "100メートル"
            },
            {
                "text": "賞品の価格は、1個1万円を超えてはならない。",
                "answer": "×",
                "explanation": "賞品の上限額は都道府県条例により定められるが、一般的に9,600円程度。",
                "number": "9,600円"
            },
            {
                "text": "営業停止処分の最長期間は6月である。",
                "answer": "○",
                "explanation": "風営法により、営業停止は6月を超えない範囲と定められている。",
                "number": "6月"
            }
        ]

        problem = random.choice(numeric_problems)

        # カテゴリ名の取得
        category_name = "営業所基準"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "key_number": problem["number"],
            "created_at": datetime.now().isoformat()
        }

    def _generate_exception(self, problem_id: int, category: Dict, pattern: Dict) -> Dict:
        """例外規定問題の生成"""

        exception_problems = [
            {
                "text": "風俗営業は深夜営業が禁止されているが、年末年始は例外として認められている。",
                "answer": "×",
                "explanation": "年末年始であっても深夜営業の禁止に例外はない。",
                "exception": "例外なし"
            },
            {
                "text": "18歳未満は風俗営業所への立入が禁止されているが、保護者同伴なら可能である。",
                "answer": "×",
                "explanation": "ゲームセンター等の5号営業では時間制限付きで可能だが、保護者同伴でも時間制限は適用される。",
                "exception": "限定的例外"
            }
        ]

        problem = random.choice(exception_problems)

        # カテゴリ名の取得
        category_name = "営業規制"
        for cat_name, cat_info in self.categories.items():
            if cat_info == category:
                category_name = cat_name
                break

        return {
            "problem_id": problem_id,
            "category": category_name,
            "pattern": pattern["description"],
            "difficulty": pattern["difficulty"],
            "problem_text": problem["text"],
            "correct_answer": problem["answer"],
            "explanation": problem["explanation"],
            "exception_type": problem["exception"],
            "created_at": datetime.now().isoformat()
        }

    def generate_all_problems(self, total_count: int = 500) -> List[Dict]:
        """全問題の生成（パターン分布に従って）"""

        print(f"🎯 {total_count}問の問題生成を開始...")

        # パターンごとの問題数を計算
        pattern_counts = {}
        remaining = total_count

        for pattern_name, pattern_info in self.patterns.items():
            count = int(total_count * pattern_info["weight"] / 100)
            pattern_counts[pattern_name] = count
            remaining -= count

        # 残りを最も重要なパターンに追加
        if remaining > 0:
            pattern_counts["絶対表現ひっかけ"] += remaining

        # カテゴリごとに均等に分配
        categories_list = list(self.categories.keys())

        for pattern_name, count in pattern_counts.items():
            print(f"  📝 {pattern_name}: {count}問生成中...")
            for i in range(count):
                # カテゴリをローテーション
                category = categories_list[i % len(categories_list)]
                problem = self.generate_problem(category, pattern_name)
                self.problems.append(problem)

        print(f"✅ {len(self.problems)}問の生成完了！")
        return self.problems

    def save_to_json(self, filename: str = "problems_driving_logic.json"):
        """JSON形式で保存"""
        output_path = f"/home/planj/patshinko-exam-app/backend/{filename}"

        # 既存のproblems.jsonフォーマットに変換
        formatted_problems = []
        for p in self.problems:
            formatted_problem = {
                "problem_id": p["problem_id"],
                "theme_id": self.categories.get(p["category"], {}).get("id", 1000),
                "theme_name": p["category"],
                "category": p["category"],
                "problem_type": "true_false",
                "format": "○×",
                "pattern_name": p["pattern"],
                "difficulty": p["difficulty"],
                "problem_text": p["problem_text"],
                "correct_answer": p["correct_answer"],
                "explanation": p["explanation"],
                "generated_at": p["created_at"],
                "legal_reference": {
                    "law": "風営法",
                    "article": self.categories.get(p["category"], {}).get("articles", ""),
                    "section": "",
                    "detail": p["explanation"]
                }
            }

            # 追加メタデータ
            for key in ["is_trap", "key_terms", "priority_rule", "time_limit", "scenario_type", "conditions", "key_number", "exception_type"]:
                if key in p:
                    formatted_problem[key] = p[key]

            formatted_problems.append(formatted_problem)

        # JSON保存
        output_data = {
            "metadata": {
                "total_problems": len(formatted_problems),
                "generated_at": datetime.now().isoformat(),
                "generator": "DrivingLicenseLogicGenerator v2.0",
                "patterns_used": list(self.patterns.keys()),
                "categories": list(self.categories.keys())
            },
            "problems": formatted_problems
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"💾 {output_path} に保存完了！")
        return output_path

    def generate_summary_report(self):
        """生成結果のサマリーレポート"""
        print("\n" + "="*60)
        print("📊 問題生成サマリーレポート")
        print("="*60)

        # カテゴリ別集計
        category_count = {}
        pattern_count = {}
        difficulty_count = {"★": 0, "★★": 0, "★★★": 0}
        answer_count = {"○": 0, "×": 0}

        for p in self.problems:
            # カテゴリ
            cat = p["category"]
            category_count[cat] = category_count.get(cat, 0) + 1

            # パターン
            pat = p["pattern"]
            pattern_count[pat] = pattern_count.get(pat, 0) + 1

            # 難易度
            diff = p["difficulty"]
            if diff in difficulty_count:
                difficulty_count[diff] += 1

            # 答え
            ans = p["correct_answer"]
            if ans in answer_count:
                answer_count[ans] += 1

        print("\n📂 カテゴリ別分布:")
        for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(self.problems) * 100
            print(f"  • {cat}: {count}問 ({percentage:.1f}%)")

        print("\n🎯 パターン別分布:")
        for pat, count in sorted(pattern_count.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(self.problems) * 100
            print(f"  • {pat}: {count}問 ({percentage:.1f}%)")

        print("\n⭐ 難易度分布:")
        for diff, count in difficulty_count.items():
            percentage = count / len(self.problems) * 100
            print(f"  • {diff}: {count}問 ({percentage:.1f}%)")

        print("\n⭕ 正答分布:")
        for ans, count in answer_count.items():
            percentage = count / len(self.problems) * 100
            print(f"  • {ans}: {count}問 ({percentage:.1f}%)")

        print("\n" + "="*60)


def main():
    """メイン処理"""
    print("🚀 遊技機取扱主任者試験問題生成システム起動")
    print("   運転免許学科試験ロジック適用版 v2.0")
    print("="*60)

    # ジェネレータ初期化
    generator = DrivingLicenseLogicGenerator()

    # 500問生成
    problems = generator.generate_all_problems(total_count=500)

    # JSON保存
    json_path = generator.save_to_json()

    # サマリーレポート
    generator.generate_summary_report()

    print(f"\n✅ 全処理完了！")
    print(f"   生成問題数: {len(problems)}問")
    print(f"   保存先: {json_path}")


if __name__ == "__main__":
    main()