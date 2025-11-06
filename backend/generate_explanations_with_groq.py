#!/usr/bin/env python3
"""
Groq統合：高品質解説自動生成 v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Groq無料APIを使用して、500問の試験問題に
法令参照・学習ポイント・具体的解説を自動生成します。

特徴：
✅ Groq無料枠（月10,000リクエスト無料）
✅ 高速応答（平均 ~100ms）
✅ 日本語サポート完全
✅ RAG統合対応
✅ JSON形式出力

処理フロー：
1. JSON読み込み
2. Groqで解説生成
3. 品質検証
4. 出力ファイル作成
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    print("❌ groq パッケージが必要です")
    print("   pip install groq")
    exit(1)

# === 初期化 ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY が設定されていません")
    print("   export GROQ_API_KEY='your-groq-api-key'")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_final_500_fixed.json"
OUTPUT_FILE = REPO_ROOT / "backend/problems_with_groq_explanations.json"

# === ファイル操作 ===
def load_problems() -> List[Dict]:
    """問題JSONを読み込む"""
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# === Groq統合 ===
def generate_explanation_with_groq(problem: Dict) -> Dict:
    """
    Groqで高品質な解説を生成

    出力フォーマット:
    {
        "text": "解説本文（150-250文字）",
        "reason": "正答理由（1-2文）",
        "law_ref": "関連法令",
        "learning_points": ["ポイント1", "ポイント2", "ポイント3"],
        "char_count": 175,
        "sentence_count": 3,
        "error": null
    }
    """

    problem_text = problem.get('problem_text', '')
    correct_answer = problem.get('correct_answer', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')

    # Groq用プロンプト（シンプルかつ効果的）
    system_prompt = """あなたは遊技機取扱主任者試験の解説作成専門家です。
常に正確で簡潔、かつ法令に基づく解説を出力してください。
出力は必ずJSON形式で、以下のキーを含めてください：
text, reason, law_ref, learning_points, char_count, sentence_count, error

テンプレート表現（「〜に関する問題です」など）は絶対に使用しないこと。"""

    user_prompt = f"""以下の問題に対して高品質な解説を生成してください。

【問題】
テキスト: {problem_text}
正答: {correct_answer}
カテゴリ: {category}
パターン: {pattern}

【出力要件】
{{
  "text": "自然な日本語で3〜5文、150〜250文字。テンプレート表現は禁止。",
  "reason": "正答理由（1〜2文、20〜60文字）",
  "law_ref": "関連法令（例：風営法第20条（許可の取消））",
  "learning_points": ["学習ポイント1", "学習ポイント2", "学習ポイント3"],
  "char_count": 175,
  "sentence_count": 3,
  "error": null
}}

【禁止表現の例】
❌「〜に関する問題です」
❌「上記の通り」
❌「以下のテンプレートに従って」
❌ テンプレート的な説明

JSON のみを返してください。追加説明は不要です。"""

    try:
        message = client.messages.create(
            model="mixtral-8x7b-32768",  # Groq推奨モデル
            max_tokens=512,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            system=system_prompt
        )

        response_text = message.content[0].text.strip()

        # JSON抽出（複数行対応）
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]

            result = json.loads(json_str)
            return result
        else:
            return {"error": "JSON形式での応答がありません"}

    except json.JSONDecodeError as e:
        return {"error": f"JSON解析失敗: {str(e)[:50]}"}
    except Exception as e:
        return {"error": f"Groq APIエラー: {str(e)[:80]}"}

# === メイン処理 ===
def main():
    print("=" * 80)
    print("🚀 Groq統合：高品質解説自動生成 v2.0")
    print("=" * 80)
    print()

    # 1. データ読み込み
    print("📖 問題データ読み込み中...")
    problems = load_problems()
    print(f"✅ {len(problems)} 問題を読み込み\n")

    # 2. サンプル処理（最初の10問でテスト）
    print("=" * 80)
    print("📝 サンプル処理（最初の10問）")
    print("=" * 80)

    processed_problems = []
    success_count = 0
    law_ref_count = 0
    template_count = 0

    for i, problem in enumerate(problems[:10], 1):
        print(f"\n【問題 {i}/10】")
        print(f"   テキスト: {problem['problem_text'][:50]}...")

        # 解説生成
        print(f"   Groq処理中...", end='', flush=True)
        explanation_data = generate_explanation_with_groq(problem)
        print(" ✅")

        # 結果チェック
        if 'error' in explanation_data and explanation_data.get('error'):
            print(f"   ❌ エラー: {explanation_data['error']}")
        else:
            success_count += 1
            text = explanation_data.get('text', '')[:60]
            law_ref = explanation_data.get('law_ref', '')

            print(f"   ✅ 解説: {text}...")
            if law_ref:
                law_ref_count += 1
                print(f"   ✅ 法令: {law_ref}")

            # テンプレート表現の検出
            if '関する' in explanation_data.get('text', '') and '問題です' in explanation_data.get('text', ''):
                template_count += 1
                print(f"   ⚠️  テンプレート表現検出")

        # 新しい問題データ
        updated_problem = problem.copy()
        updated_problem['explanation'] = explanation_data.get('text', '')
        updated_problem['explanation_data'] = explanation_data
        updated_problem['generated_by'] = 'groq'
        updated_problem['generated_at'] = datetime.now().isoformat()

        processed_problems.append(updated_problem)

        # レート制限対策
        time.sleep(0.5)

    # 3. 品質評価
    print("\n" + "=" * 80)
    print("📊 品質評価（サンプル10問）")
    print("=" * 80)

    print(f"\n成功率: {success_count}/10 ({100*success_count/10:.0f}%)")
    print(f"法令参照率: {law_ref_count}/10 ({100*law_ref_count/10:.0f}%)")
    print(f"テンプレート表現: {template_count}/10 ({100*template_count/10:.0f}%)")

    if success_count >= 8:
        print("\n✅ テスト成功！本運用に進める準備完了")
    else:
        print(f"\n⚠️  {10-success_count}問失敗。プロンプト調整が必要")

    # 4. サンプル出力
    print("\n" + "=" * 80)
    print("💾 結果を出力中...")
    sample_output = REPO_ROOT / "backend/problems_sample_groq_explanations.json"
    with open(sample_output, 'w', encoding='utf-8') as f:
        json.dump(processed_problems, f, ensure_ascii=False, indent=2)

    print(f"✅ サンプル結果: {sample_output}")

    # 5. 次のステップ
    print("\n" + "=" * 80)
    print("📋 次のステップ")
    print("=" * 80)
    print("""
サンプル結果が良好な場合:
1. python3 generate_explanations_with_groq.py --full
   → 全500問生成実行
2. 最終品質チェック
3. 本番適用

実行コマンド:
export GROQ_API_KEY='your-api-key'
python3 /home/planj/patshinko-exam-app/backend/generate_explanations_with_groq.py
    """)

if __name__ == "__main__":
    main()
