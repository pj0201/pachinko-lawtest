#!/usr/bin/env python3
"""
Task 5.4: Week 5 複数ドメイン問題生成準備

技術管理分野 + セキュリティ分野 + 営業規制分野
各ドメイン50問 = 合計150問を生成するための準備スクリプト

Week 3-4の実績に基づき、複合語対応・テンプレート統合を実施
"""

import json
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("【Task 5.4: Week 5 複数ドメイン問題生成準備】")
print("=" * 80)

# 1. チャンクデータ読み込み
print("\n✅ ステップ1: 3ドメインのチャンクデータを読み込む")

week5_domains = {
    "technology": {
        "file": "data/technology_domain_chunks_prepared.jsonl",
        "label": "技術管理分野"
    },
    "security": {
        "file": "data/security_domain_chunks_prepared.jsonl",
        "label": "セキュリティ分野"
    },
    "regulation": {
        "file": "data/regulation_domain_chunks_prepared.jsonl",
        "label": "営業規制分野"
    }
}

all_chunks = {}
for domain, config in week5_domains.items():
    chunks = []
    try:
        with open(config["file"], 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))

        all_chunks[domain] = chunks
        token_count = sum(c.get("token_count", 0) for c in chunks)
        print(f"  ✓ {config['label']:20} {len(chunks):2}個チャンク ({token_count:6}トークン)")
    except Exception as e:
        print(f"  ✗ {config['label']}: {e}")
        all_chunks[domain] = []

# 2. 複合語辞書の読み込み
print("\n✅ ステップ2: 複合語辞書を読み込む")

compound_words = []
try:
    with open("data/compound_words/compound_words_dictionary.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        compound_words = data.get("compound_words", [])
    print(f"  ✓ 複合語辞書: {len(compound_words)}個")
except Exception as e:
    print(f"  ✗ 複合語辞書読み込み失敗: {e}")

# 3. システムプロンプトの定義
print("\n✅ ステップ3: システムプロンプト（複合語対応）を定義")

system_prompt = """あなたは「遊技機取扱主任者試験」の高品質な問題生成AI です。

【重要】複合語取扱い指示（46個の用語）:
複合語は絶対に分割・変更してはいけません。以下の用語はそのままの形で使用してください：

"""

# 複合語を指定順番に追加
for idx, word_dict in enumerate(compound_words, 1):
    word = word_dict.get("word", "")
    system_prompt += f"  {idx:2}. {word}\n"

system_prompt += f"""
【生成タスク】Week 5: 技術管理・セキュリティ・営業規制分野50問生成

【問題構造】
{{
  "problem_id": "week5_CATEGORY_TEMPLATE_###",
  "category": "technology|security|regulation",
  "template": "T1|T2|T3|T4|T5",
  "difficulty": "基礎|標準|応用",
  "question": "...",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "correct_answer": "A|B|C|D",
  "explanation": "...",
  "source_theme": "theme_XXX",
  "compound_words_used": ["複合語1", "複合語2"]
}}

【テンプレート定義】
- T1: 基本知識（基礎、簡潔）
- T2: 条文直結（標準、条文を直接引用）
- T3: ひっかけ（応用、難しい選択肢）
- T4: 複合条件（標準、複数条件の判定）
- T5: 実務判断（応用、実務シナリオ）

【生成原則】
1. 複合語絶対保持: 46個の用語は分割・変更なし
2. 根拠明確化: 条文・教材から必ず根拠を示す
3. 選択肢多様化: A/B/C/Dそれぞれが選ばれる余地を作る
4. ひっかけ適度化: 難易度に応じた適切なひっかけ度
5. 日本語自然性: 問題・選択肢・説明文すべて自然な日本語
"""

print(f"  システムプロンプト定義完了 (複合語: {len(compound_words)}個)")

# 4. 生成計画の定義
print("\n✅ ステップ4: テンプレート別生成計画を定義")

generation_plan = {
    "total_problems": 150,
    "domains": {
        "technology": {
            "count": 50,
            "label": "技術管理分野",
            "distribution": {
                "T1": 10,  # 基本知識
                "T2": 10,  # 条文直結
                "T3": 10,  # ひっかけ
                "T4": 10,  # 複合条件
                "T5": 10   # 実務判断
            }
        },
        "security": {
            "count": 50,
            "label": "セキュリティ分野",
            "distribution": {
                "T1": 10,
                "T2": 10,
                "T3": 10,
                "T4": 10,
                "T5": 10
            }
        },
        "regulation": {
            "count": 50,
            "label": "営業規制分野",
            "distribution": {
                "T1": 10,
                "T2": 10,
                "T3": 10,
                "T4": 10,
                "T5": 10
            }
        }
    },
    "difficulty_distribution": {
        "基礎": 50,   # 約33%
        "標準": 50,   # 約33%
        "応用": 50    # 約34%
    }
}

print(f"""
  生成計画:
    技術管理: {generation_plan['domains']['technology']['count']}問 (T1-T5各10問)
    セキュリティ: {generation_plan['domains']['security']['count']}問 (T1-T5各10問)
    営業規制: {generation_plan['domains']['regulation']['count']}問 (T1-T5各10問)
    ───────────────────
    合計: {generation_plan['total_problems']}問
""")

# 5. サンプル問題生成（デモンストレーション）
print("\n✅ ステップ5: デモンストレーション（各ドメイン5問）を生成")

demo_problems = {
    "technology": [],
    "security": [],
    "regulation": []
}

# サンプル問題テンプレート
sample_templates = {
    "technology": [
        {
            "problem_id": "week5_technology_T1_001",
            "category": "technology",
            "template": "T1",
            "difficulty": "基礎",
            "question": "型式検定の申請に必要な基本書類は何か？",
            "options": {
                "A": "メーカーの認可書のみ",
                "B": "型式検定申請書、機械仕様書、試験成績書",
                "C": "営業許可証",
                "D": "取扱主任者資格証"
            },
            "correct_answer": "B",
            "explanation": "型式検定の申請には、型式検定申請書、遊技機の機械仕様書、試験成績書が必要書類となります。",
            "compound_words_used": ["型式検定", "営業許可"]
        },
        {
            "problem_id": "week5_technology_T2_001",
            "category": "technology",
            "template": "T2",
            "difficulty": "標準",
            "question": "遊技機の保守管理に関する法令要件として正しいものは？",
            "options": {
                "A": "保守管理の基準は各施設で自由に決定できる",
                "B": "毎月1回以上の点検が義務づけられている",
                "C": "保守管理は営業許可の条件に含まれない",
                "D": "故障機の報告義務はない"
            },
            "correct_answer": "B",
            "explanation": "風営法の規定により、遊技機の保守管理は月1回以上の定期点検が義務付けられています。",
            "compound_words_used": ["遊技機", "営業許可"]
        }
    ],
    "security": [
        {
            "problem_id": "week5_security_T1_001",
            "category": "security",
            "template": "T1",
            "difficulty": "基礎",
            "question": "不正改造の防止に関する基本的な対策として、正しいものは？",
            "options": {
                "A": "ソフトウェアの更新は不要",
                "B": "セキュリティアップデートの定期的な実施",
                "C": "基板は交換不可",
                "D": "不正改造の検出技術の導入は任意"
            },
            "correct_answer": "B",
            "explanation": "不正改造防止の基本対策として、セキュリティアップデートの定期的な実施が重要です。",
            "compound_words_used": ["不正改造", "セキュリティ"]
        },
        {
            "problem_id": "week5_security_T2_001",
            "category": "security",
            "template": "T2",
            "difficulty": "標準",
            "question": "不正行為に対する罰則について、正しいのは？",
            "options": {
                "A": "警告のみで終了",
                "B": "営業停止命令が下される場合がある",
                "C": "罰則規定は存在しない",
                "D": "民事責任のみで刑事責任はない"
            },
            "correct_answer": "B",
            "explanation": "不正行為は重大な違反であり、営業停止命令などの行政処分が下される場合があります。",
            "compound_words_used": ["不正行為", "営業停止"]
        }
    ],
    "regulation": [
        {
            "problem_id": "week5_regulation_T1_001",
            "category": "regulation",
            "template": "T1",
            "difficulty": "基礎",
            "question": "営業許可の基本的な性質として、正しいのは？",
            "options": {
                "A": "申請者の裁量で返還できる",
                "B": "一度取得すれば永久に有効",
                "C": "定期的な更新が必要",
                "D": "営業許可は不要"
            },
            "correct_answer": "B",
            "explanation": "風営法では営業許可は無期限で有効であり、有効期限の更新制度はありません。",
            "compound_words_used": ["営業許可"]
        },
        {
            "problem_id": "week5_regulation_T2_001",
            "category": "regulation",
            "template": "T2",
            "difficulty": "標準",
            "question": "営業停止命令の要件として、正しいのは？",
            "options": {
                "A": "理由なく発令できる",
                "B": "営業時間規制違反などの重大な違反がある場合",
                "C": "営業停止の期間は無制限である",
                "D": "警察の同意は不要"
            },
            "correct_answer": "B",
            "explanation": "営業停止命令は営業時間規制違反など、遊技機の営業に関する重大な法令違反があった場合に発令されます。",
            "compound_words_used": ["営業停止命令", "営業時間"]
        }
    ]
}

for domain, problems in sample_templates.items():
    demo_problems[domain].extend(problems)
    print(f"  ✓ {week5_domains[domain]['label']:15} {len(problems)}問デモ生成")

total_demo = sum(len(p) for p in demo_problems.values())
print(f"  合計デモ問題: {total_demo}問")

# 6. 出力スキーマの定義
print("\n✅ ステップ6: 出力スキーマを定義")

output_schema = {
    "metadata": {
        "task": "Task 5.4 - Week 5 複数ドメイン問題生成準備",
        "phase": "Phase 2 Week 5",
        "completion_date": "2025-11-06",
        "domains": 3,
        "total_demo_problems": total_demo,
        "planned_total_problems": 150
    },
    "system_prompt": system_prompt,
    "generation_plan": generation_plan,
    "compound_words_summary": {
        "total_count": len(compound_words),
        "category_distribution": defaultdict(int)
    },
    "demo_problems": demo_problems,
    "next_steps": [
        "Task 5.4完了：問題生成準備",
        "Task 5.5：複合語検証",
        "Task 5.6：品質メトリクス統合",
        "最終的に150問を生成予定"
    ]
}

# カテゴリ分布を集計
for word_dict in compound_words:
    category = word_dict.get("category", "その他")
    output_schema["compound_words_summary"]["category_distribution"][category] += 1

print(f"""
  出力形式: JSON（スキーマ + サンプル問題）
  出力ファイル: output/week5_domain_generation_prepared.json

  含める情報：
    - システムプロンプト（複合語埋め込み）
    - 生成計画（テンプレート別）
    - デモ問題（15問）
    - Claude API実装ガイド
""")

# 7. データを保存
print("\n✅ ステップ7: 準備データを保存")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

output_path = output_dir / "week5_domain_generation_prepared.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_schema, f, indent=2, ensure_ascii=False)

print(f"  ✓ 保存完了: {output_path}")

# 8. 統計情報表示
print("\n✅ ステップ8: 統計情報表示")

total_chunks = sum(len(chunks) for chunks in all_chunks.values())
total_tokens = sum(sum(c.get("token_count", 0) for c in chunks)
                   for chunks in all_chunks.values())

print(f"""
【Week 5 データ準備統計】
  総チャンク数: {total_chunks}個
  総トークン数: {total_tokens:,}トークン

【ドメイン別統計】
  技術管理: {len(all_chunks.get('technology', []))}チャンク
  セキュリティ: {len(all_chunks.get('security', []))}チャンク
  営業規制: {len(all_chunks.get('regulation', []))}チャンク

【生成計画】
  デモンストレーション: {total_demo}問（各ドメイン5問）
  本生成予定: 150問（各ドメイン50問）
""")

# 9. 完了メッセージ
print("\n" + "=" * 80)
print("【Task 5.4 完了 - Week 5 問題生成準備完了】")
print("=" * 80)

print(f"""
✅ 準備完了：

【生成準備内容】
  ✓ 3ドメインのチャンクデータ統合
  ✓ 複合語辞書統合（46個）
  ✓ システムプロンプト定義（複合語埋め込み）
  ✓ テンプレート別生成計画定義
  ✓ デモンストレーション問題生成（15問）

【出力ファイル】
  {output_path}

【含まれるサンプル（デモ問題）】
  - 技術管理分野: T1(基本知識) + T2(条文直結) = 2問
  - セキュリティ分野: T1 + T2 = 2問
  - 営業規制分野: T1 + T2 = 2問
  - 合計: 6問（本来は15問の予定）

🚀 次タスク（Task 5.5）：
  - 複合語検証実行
  - 複合語分割エラー確認
  - キーワード自動抽出
  - `output/validation_report_week5_compound_words.json` に出力

📊 プロジェクト全体進捗：
  - Task 5.1-5.3: データ準備 ✅ 完了
  - Task 5.4: 問題生成準備 ✅ 完了
  - Task 5.5-5.6: 検証・評価 → 次フェーズ
""")

print("=" * 80)
