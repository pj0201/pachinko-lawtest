#!/usr/bin/env python3
"""
Week 7 Phase 1: テスト生成（5問）
技術管理分野から各テンプレート1問ずつ、計5問を生成
品質改善ガイドに基づいたプロンプトでテスト生成実行
"""

import json
import os
from pathlib import Path


def main():
    print("=" * 80)
    print("【Week 7 Phase 1: テスト生成（5問）】")
    print("=" * 80)
    print()

    # Step 1: 生成計画の確認
    print("✅ ステップ1: 生成計画を確認")
    generation_plan_path = Path("output/technology_domain_50_generation_plan.json")

    if not generation_plan_path.exists():
        print(f"  ❌ ファイルなし: {generation_plan_path}")
        return False

    with open(generation_plan_path) as f:
        plan = json.load(f)

    print(f"  ✓ ファイル: {generation_plan_path}")
    print(f"  ✓ ドメイン: {plan['metadata']['domain']}")
    print(f"  ✓ チャンク数: {plan['metadata']['source_chunks']}")
    print(f"  ✓ 複合語数: 46個")
    print()

    # Step 2: テスト生成計画
    print("✅ ステップ2: テスト生成計画")
    test_plan = {
        "T1": {"template": "T1", "count": 1, "difficulty": "基礎", "description": "基本知識"},
        "T2": {"template": "T2", "count": 1, "difficulty": "標準", "description": "条文直結"},
        "T3": {"template": "T3", "count": 1, "difficulty": "応用", "description": "ひっかけ"},
        "T4": {"template": "T4", "count": 1, "difficulty": "標準", "description": "複合条件"},
        "T5": {"template": "T5", "count": 1, "difficulty": "応用", "description": "実務判断"},
    }

    for template, info in test_plan.items():
        print(f"  ✓ {template}: {info['description']} ({info['difficulty']}) x 1問")

    print()

    # Step 3: システムプロンプトの確認
    print("✅ ステップ3: システムプロンプト確認")
    system_prompt = plan["system_prompt"]

    # 複合語確認
    compound_words = [
        "営業許可", "型式検定", "営業禁止", "営業停止", "不正改造",
        "遊技機", "営業所", "営業者", "景品", "景品規制",
        "景品交換", "営業時間", "不正行為", "取消", "取消し要件",
        "失効", "申請", "申請手続き", "申請書", "公安委員会",
        "都道府県", "主基板", "外部端子", "基板ケース", "かしめ",
        "セキュリティ", "中古遊技機", "リサイクル", "廃棄物", "製造業者",
        "販売業者", "設置", "新台設置", "点検", "点検確認",
        "保守管理", "製造番号", "立入検査", "行政処分", "罰則",
        "違反", "チップ", "有効期間", "無期限有効", "3年有効",
        "リサイクル推進法"
    ]

    print(f"  ✓ システムプロンプト文字数: {len(system_prompt)} 文字")
    print(f"  ✓ 複合語: {len(compound_words)}個 ([営業許可], [型式検定], ... )")
    print()

    # Step 4: Claude APIプロンプト生成
    print("✅ ステップ4: Claude API呼び出しプロンプト生成")

    prompts = {
        "T1": {
            "system": system_prompt,
            "user": """技術管理分野のT1 (基本知識)テンプレートで、難易度「基礎」の問題を1問生成してください。

【重要な指示】
- ひっかけ度: 10-20%の範囲内（正答選択率 80-90%）
- 大多数の学習者が正答を選べる明確な問題にしてください
- 選択肢B: 学習者の典型的な誤り（似た概念との混同）

【品質基準】
- 正答: 確実に正しい（根拠: 基本原則など）
- 選択肢B: 似た概念だが異なる（XX と混同しやすい）
- 選択肢C: 関連概念だが別（XX に関連するが異なる）
- 選択肢D: 微妙な誤り（一部は正しいが YY が不正確）

JSON形式で以下の構造で返してください：
{
  "problem_id": "technology_T1_001",
  "domain": "technology",
  "template": "T1",
  "difficulty": "基礎",
  "question": "...",
  "options": {
    "A": "... （正答）",
    "B": "... （典型的な誤り）",
    "C": "... （関連概念の誤り）",
    "D": "... （微妙な誤り）"
  },
  "correct_answer": "A",
  "explanation": "...",
  "source_theme": "theme_025",
  "compound_words_used": ["複合語1"]
}"""
        },
        "T2": {
            "system": system_prompt,
            "user": """技術管理分野のT2 (条文直結)テンプレートで、難易度「標準」の問題を1問生成してください。

【重要な指示】
- ひっかけ度: 30-40%の範囲内（正答選択率 60-70%）
- 標準難易度: 正答には理由があるが、誤りも説得力あり
- 選択肢B-D: すべてに「選ばれる可能性」を持たせてください

JSON形式で返してください。problem_id: technology_T2_001"""
        },
        "T3": {
            "system": system_prompt,
            "user": """技術管理分野のT3 (ひっかけ)テンプレートで、難易度「応用」の問題を1問生成してください。

【重要な指示】
- ひっかけ度: 40-50%の範囲内（正答選択率 50-60%）
- 応用難易度: 4択すべてに説得力、慎重な判断が必要
- ディストラクタの品質: 正答と同等レベルの根拠を持たせてください

JSON形式で返してください。problem_id: technology_T3_001"""
        },
        "T4": {
            "system": system_prompt,
            "user": """技術管理分野のT4 (複合条件)テンプレートで、難易度「標準」の問題を1問生成してください。

【重要な指示】
- ひっかけ度: 30-40%の範囲内（正答選択率 60-70%）
- 複数条件で混同させるが標準難易度
- 選択肢: 条件を部分的に誤った解釈を含める

JSON形式で返してください。problem_id: technology_T4_001"""
        },
        "T5": {
            "system": system_prompt,
            "user": """技術管理分野のT5 (実務判断)テンプレートで、難易度「応用」の問題を1問生成してください。

【重要な指示】
- ひっかけ度: 40-50%の範囲内（正答選択率 50-60%）
- 応用難易度: 実務知識を要する
- 選択肢: 実務で実際に起こりやすい誤りを含める

JSON形式で返してください。problem_id: technology_T5_001"""
        }
    }

    for template in ["T1", "T2", "T3", "T4", "T5"]:
        print(f"  ✓ {template}: プロンプト生成完了")

    print()

    # Step 5: プロンプトファイル生成
    print("✅ ステップ5: Claude API呼び出し用プロンプト保存")

    prompts_file = Path("output/WEEK7_PHASE1_CLAUDE_API_PROMPTS.json")
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "phase": "Week 7 Phase 1",
                "task": "Test Generation (5 problems)",
                "templates": list(prompts.keys()),
                "total_problems": 5
            },
            "prompts": prompts
        }, f, ensure_ascii=False, indent=2)

    print(f"  ✓ プロンプト保存: {prompts_file}")
    print()

    # Step 6: 実行指示
    print("✅ ステップ6: Claude API呼び出し指示")
    print()
    print("  【手動実行方法】")
    print("  1. 以下のファイルを開く:")
    print(f"     {prompts_file}")
    print()
    print("  2. 各テンプレート（T1-T5）のプロンプトをコピーして、")
    print("     Claude.com/API で呼び出し")
    print()
    print("  3. 生成結果を output/technology_domain_test_5problems.jsonl に保存")
    print()
    print("  【自動実行方法（Claude API Python SDK）】")
    print("  $ python3 backend/call_claude_api_test_generation.py")
    print()

    # 実行完了
    print("=" * 80)
    print("✅ Phase 1準備完了")
    print("=" * 80)
    print()
    print("【次ステップ】")
    print("1. Claude APIでテスト生成実行（5問）")
    print("2. 品質評価を実施")
    print("3. Phase 3本生成へ進む or Phase 2調整を実施")
    print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
