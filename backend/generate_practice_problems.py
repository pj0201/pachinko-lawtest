#!/usr/bin/env python3
"""
Task 4.2: 実務分野問題生成準備（50問）

複合語対応プロンプトを使用して、
Claude APIで実務分野の問題を生成するための準備
"""

import json
import os
import sys
from pathlib import Path

print("=" * 80)
print("【Task 4.2: 実務分野問題生成準備】")
print("=" * 80)

# 1. 既存リソースの確認
print("\n✅ ステップ1: 既存リソースの確認")

resources = {
    "compound_word_prompt": "prompts/compound_word_aware_prompt_v1.txt",
    "compound_words_dict": "data/compound_words/compound_words_dictionary.json",
    "question_templates": "config/question_templates_detailed.yaml",
    "practice_chunks": "data/practice_domain_chunks_prepared.jsonl"
}

missing = []
for name, path in resources.items():
    if Path(path).exists():
        if path.endswith('.jsonl'):
            # JSONL行数をカウント
            with open(path, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f)
            print(f"  ✓ {name:30} ({path}) - {count}行")
        else:
            size = Path(path).stat().st_size
            print(f"  ✓ {name:30} ({path}) - {size:,}バイト")
    else:
        print(f"  ✗ {name:30} (見つかりません)")
        missing.append(name)

if not missing:
    print("\n  ✅ すべてのリソース揃っています")
else:
    print(f"\n  ⚠️  欠落リソース: {', '.join(missing)}")

# 2. 複合語辞書を読み込む
print("\n✅ ステップ2: 複合語辞書を読み込む")

try:
    with open("data/compound_words/compound_words_dictionary.json", 'r', encoding='utf-8') as f:
        compound_words_data = json.load(f)

    compound_words_list = [
        cw['word'] for cw in compound_words_data.get('compound_words', [])
    ]
    print(f"  読み込み完了: {len(compound_words_list)}個の複合語")
    print(f"  主要複合語: {', '.join(compound_words_list[:5])}...")
except Exception as e:
    print(f"  エラー: {e}")
    compound_words_list = []

# 3. 実務分野テンプレート別生成計画
print("\n✅ ステップ3: テンプレート別生成計画")

generation_plan = {
    "T1": {
        "name": "基本知識・正誤判定",
        "count": 10,
        "difficulty": "基礎",
        "focus": "営業許可、営業停止などの基本概念"
    },
    "T2": {
        "name": "条文直結・法律規定判定",
        "count": 10,
        "difficulty": "基礎",
        "focus": "具体的な規定内容の対応"
    },
    "T3": {
        "name": "ひっかけ問題・微妙な差異判定",
        "count": 10,
        "difficulty": "標準",
        "focus": "期間、期限、手続きの正確性"
    },
    "T4": {
        "name": "複合条件・要件全体判定",
        "count": 10,
        "difficulty": "標準",
        "focus": "複数条件の組み合わせ、手続き流れ"
    },
    "T5": {
        "name": "実務判断・応用判定",
        "count": 10,
        "difficulty": "応用",
        "focus": "実務シーンでの適切な対応判断"
    }
}

total_planned = sum(plan['count'] for plan in generation_plan.values())
print(f"\n  計画問題数: {total_planned}問")
print(f"\n  テンプレート別計画：")

for template_id, plan in generation_plan.items():
    print(f"    {template_id}: {plan['name']:30} {plan['count']:2}問 ({plan['difficulty']})")

# 4. プロンプト生成テンプレート
print("\n✅ ステップ4: プロンプト生成テンプレートを準備")

system_prompt = """あなたは主任者講習試験の問題作成AIです。
以下の指示に従い、高品質な試験問題を生成してください。

【基本要件】
- 対象: 遊技場営業の実務に関する試験問題
- 形式: ○×判定（true/false）
- 複合語の扱い: 営業許可、営業停止など、複合語は絶対に分割しないこと

【複合語リスト（分割禁止）】
{compound_words}

【重要】
これらの複合語は1つの語として扱い、分割してはいけません。
例：「営業許可」は「営業 許可」と分割してはいけません。

【実務分野の特徴】
- 法令の実施に関わる手続き、判断
- 営業許可、営業停止、取消しに関する概念
- 型式検定、遊技機管理に関する実務
- 不正防止、コンプライアンスに関する内容
- 実際の営業シーンでの適切な対応
"""

user_prompt_template = """【テンプレート】
{template_name}

難易度: {difficulty}
パターン: {pattern}

【参考例】
{examples}

【生成指示】
上記のテンプレートと例に合わせて、同等品質の新しい問題を1問生成してください。

【出力形式】
JSON形式で以下を出力してください：
{{
  "template": "{template_name}",
  "difficulty": "{difficulty}",
  "problem_text": "問題文",
  "correct_answer": "○ or ×",
  "explanation": "解説文",
  "compound_words_used": ["複合語1", "複合語2"],
  "legal_reference": "根拠条文"
}}

【品質チェック】
生成後、確認してください：
✓ 複合語が分割されていないか
✓ 法律的に正確か
✓ ひっかけの強度は適切か
"""

system_prompt_formatted = system_prompt.format(
    compound_words=", ".join(compound_words_list)
)

print("  システムプロンプト: 準備完了")
print(f"  複合語埋め込み: {len(compound_words_list)}個")
print(f"  ユーザープロンプトテンプレート: 準備完了")

# 5. 実装手順を定義
print("\n✅ ステップ5: Claude API実装手順を定義")

implementation_steps = """【実装手順】

1. 環境設定
   ```python
   import anthropic

   client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
   ```

2. 問題生成ループ
   for template_id, plan in generation_plan.items():
       for i in range(plan['count']):
           # テンプレート別プロンプトを構築
           prompt = user_prompt_template.format(...)

           # Claude APIで生成
           response = client.messages.create(
               model="claude-3-5-sonnet-20241022",
               max_tokens=1000,
               temperature=0.7,
               system=system_prompt_formatted,
               messages=[{"role": "user", "content": prompt}]
           )

           # JSON解析して保存
           problem = json.loads(response.content[0].text)
           problems.append(problem)

3. 品質検証
   - 複合語分割チェック
   - JSON形式検証
   - 法律的正確性確認
   - ひっかけスコア計算

4. 出力
   - `output/practice_domain_50_raw.json`: 生成結果
   - `output/practice_domain_50_raw_with_metrics.json`: 評価結果付き
"""

print(implementation_steps)

# 6. 出力スキーマを定義
print("\n✅ ステップ6: 出力スキーマを定義")

output_schema = {
    "metadata": {
        "task": "Task 4.2 - 実務分野50問生成",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.7,
        "max_tokens": 1000,
        "total_problems": 50,
        "generation_date": "2025-11-06"
    },
    "problems": [
        {
            "problem_id": "practice_T1_001",
            "template": "T1 (基本知識・正誤判定)",
            "difficulty": "基礎",
            "problem_text": "○×判定問題文",
            "correct_answer": "○",
            "explanation": "解説文",
            "compound_words_used": ["営業許可"],
            "legal_reference": "風営法第6条",
            "generation_params": {
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7
            },
            "quality_metrics": {
                "compound_word_integrity": True,
                "legal_accuracy": True,
                "clarity_score": 0.85,
                "overall_score": 0.82
            }
        }
    ],
    "summary": {
        "generated": 50,
        "approved": 42,
        "revision_needed": 5,
        "rejected": 3,
        "approval_rate": "84%"
    }
}

print(f"""
  出力JSON構造：
  - metadata: 生成パラメータ
  - problems: 50個の問題
  - summary: 統計情報

  各問題の項目：
  - problem_id, template, difficulty
  - problem_text, correct_answer, explanation
  - compound_words_used, legal_reference
  - quality_metrics（自動計算）
""")

# 7. デモンストレーション用サンプル問題を生成
print("\n✅ ステップ7: デモンストレーション用サンプル問題を生成")

sample_problems = [
    {
        "problem_id": "practice_T1_001",
        "template": "T1 (基本知識・正誤判定)",
        "difficulty": "基礎",
        "problem_text": "営業者は営業許可を取得した後、営業禁止の区域に営業所を設置することはできない。",
        "correct_answer": "○",
        "explanation": "風営法では特定の区域（学校周辺、住宅地等）が営業禁止区域として指定されており、営業許可を受けた後でも営業禁止区域には営業所を設置できません。",
        "compound_words_used": ["営業許可", "営業禁止", "営業所"],
        "legal_reference": "風営法第4条",
        "source": "Claude-generated (sample)"
    },
    {
        "problem_id": "practice_T2_001",
        "template": "T2 (条文直結・法律規定判定)",
        "difficulty": "基礎",
        "problem_text": "営業停止命令を受けた場合、その期間中は一切の営業活動を行うことはできない。",
        "correct_answer": "○",
        "explanation": "営業停止命令により、命令期間中の営業活動は全面的に禁止されます。これは風営法第45条で定められた行政処分です。",
        "compound_words_used": ["営業停止命令"],
        "legal_reference": "風営法第45条",
        "source": "Claude-generated (sample)"
    },
    {
        "problem_id": "practice_T3_001",
        "template": "T3 (ひっかけ問題・微妙な差異判定)",
        "difficulty": "標準",
        "problem_text": "型式検定合格の有効期間は3年間であり、3年経過後は自動的に失効する。",
        "correct_answer": "○",
        "explanation": "風営法第32条により、型式検定の有効期間は3年と定められており、期間満了により自動的に失効します。その後同じ型式の遊技機を設置するには再度型式検定が必要です。",
        "compound_words_used": ["型式検定", "遊技機"],
        "legal_reference": "風営法第32条",
        "source": "Claude-generated (sample)"
    },
    {
        "problem_id": "practice_T4_001",
        "template": "T4 (複合条件・要件全体判定)",
        "difficulty": "標準",
        "problem_text": "中古遊技機を設置する場合、型式検定合格品かつ有効期間内であることと、中古機の流通管理制度の適正な手続きを経たものであることの両方の要件を満たす必要がある。",
        "correct_answer": "○",
        "explanation": "中古遊技機の設置には両方の要件を満たす必要があります：1）型式検定合格で有効期間内、2）中古機流通管理制度の正規の手続きを経たもの。この二つの条件は独立しており、どちらも満たさなければなりません。",
        "compound_words_used": ["型式検定", "遊技機", "中古遊技機", "流通管理"],
        "legal_reference": "風営法第32条、中古機流通管理規定",
        "source": "Claude-generated (sample)"
    },
    {
        "problem_id": "practice_T5_001",
        "template": "T5 (実務判断・応用判定)",
        "difficulty": "応用",
        "problem_text": "営業者が検査時に営業停止命令に違反して営業していることが発覚した場合、そのことのみで営業許可が取り消される可能性がある。",
        "correct_answer": "○",
        "explanation": "営業停止命令への違反は重大な違反であり、営業許可取消事由（風営法第10条）に該当します。このような重大違反が発見された場合、営業許可取消しの処分につながる可能性が高いです。",
        "compound_words_used": ["営業停止命令", "営業許可"],
        "legal_reference": "風営法第10条（取消事由）",
        "source": "Claude-generated (sample)"
    }
]

print(f"  生成されたサンプル問題: {len(sample_problems)}個")
for problem in sample_problems[:3]:
    print(f"\n  問題ID: {problem['problem_id']}")
    print(f"  テンプレート: {problem['template']}")
    print(f"  難易度: {problem['difficulty']}")
    print(f"  複合語: {', '.join(problem['compound_words_used'])}")

# 8. デモデータを保存
print("\n✅ ステップ8: デモンストレーションデータを保存")

demo_output = {
    "metadata": {
        "task": "Task 4.2 - 実務分野50問生成",
        "status": "demonstration (実装待ち)",
        "model": "claude-3-5-sonnet-20241022",
        "total_planned": 50,
        "sample_count": len(sample_problems),
        "generation_date": "2025-11-06"
    },
    "generation_plan": generation_plan,
    "sample_problems": sample_problems,
    "implementation_guide": {
        "step_1": "Claude APIキーを環境変数に設定",
        "step_2": "テンプレート別ループで問題を生成",
        "step_3": "JSON形式で解析して保存",
        "step_4": "複合語検証 & 品質スコア計算",
        "step_5": "output/practice_domain_50_raw.json に出力"
    }
}

output_path = "output/practice_domain_50_demo.json"
Path("output").mkdir(exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(demo_output, f, indent=2, ensure_ascii=False)

print(f"  保存完了: {output_path}")

# 9. 次ステップ
print("\n" + "=" * 80)
print("【Task 4.2 完了 - 実装準備完了】")
print("=" * 80)

print(f"""
✅ 準備完了：
  1. システムプロンプトを設計（複合語埋め込み）
  2. テンプレート別生成計画（50問）を定義
  3. Claude API実装ガイドを作成
  4. 出力スキーマを確定
  5. デモンストレーション用5問を生成

📊 サンプル問題（5個）を `output/practice_domain_50_demo.json` に保存

📝 本実装ステップ：
  1. ANTHROPIC_API_KEY環境変数を設定
  2. generate_practice_problems_claude_api.py を実行
  3. Claude API で50問生成（20-30分）
  4. 複合語検証 + 品質評価
  5. `output/practice_domain_50_raw.json` を生成

🚀 次タスク（Task 4.3）：
  - 生成された50問に対し複合語検証を実行
  - 複合語分割エラー、キーワード漏れをチェック
""")

print("=" * 80)
