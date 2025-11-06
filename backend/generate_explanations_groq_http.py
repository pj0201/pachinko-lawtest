#!/usr/bin/env python3
"""
Groq HTTP API：高品質解説自動生成 v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTTP直接呼び出しで500問の試験問題に
法令参照・学習ポイント・具体的解説を自動生成します。

特徴：
✅ Groq無料API（月10,000リクエスト無料）
✅ HTTP直接呼び出し（SDK不要）
✅ 高速応答（平均 ~100-200ms）
✅ JSON形式出力
✅ テンプレート表現排除
"""

import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# === 初期化 ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY が環境変数に設定されていません")
    print("User様、GROQ_API_KEYを設定してください")
    exit(1)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

REPO_ROOT = Path("/home/planj/patshinko-exam-app")
PROBLEMS_FILE = REPO_ROOT / "backend/problems_final_500_fixed.json"

# === ファイル操作 ===
def load_problems() -> List[Dict]:
    """問題JSONを読み込む"""
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# === Groq HTTP API呼び出し ===
def call_groq_api(system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
    """
    Groq APIをHTTP経由で呼び出し
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)[:100]}"
    except (KeyError, json.JSONDecodeError) as e:
        return f"ERROR: Response parse failed - {str(e)[:100]}"

def generate_explanation_groq(problem: Dict) -> Dict:
    """Groqで高品質な解説を生成"""

    problem_text = problem.get('problem_text', '')
    correct_answer = problem.get('correct_answer', '')
    category = problem.get('category', '')
    pattern = problem.get('pattern_name', '')

    system_prompt = """あなたは遊技機取扱主任者試験の解説作成専門家です。
常に正確で簡潔、かつ法令に基づく解説を出力してください。
出力は必ずJSON形式で以下のキーを含めてください：
text, reason, law_ref, learning_points, error

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
  "reason": "正答理由（1〜2文）",
  "law_ref": "関連法令（例：風営法第20条（許可の取消））",
  "learning_points": ["ポイント1", "ポイント2", "ポイント3"],
  "error": null
}}

JSON のみを返してください。"""

    try:
        response_text = call_groq_api(system_prompt, user_prompt)

        if response_text.startswith("ERROR"):
            return {"error": response_text}

        # JSON抽出
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]

            result = json.loads(json_str)
            return result
        else:
            return {"error": "JSON形式の応答がありません"}

    except json.JSONDecodeError as e:
        return {"error": f"JSON解析失敗: {str(e)[:50]}"}
    except Exception as e:
        return {"error": f"予期しないエラー: {str(e)[:80]}"}

# === メイン処理 ===
def main():
    print("=" * 80)
    print("🚀 Groq HTTP API：高品質解説自動生成 v3.0")
    print("=" * 80)
    print()

    # APIキー確認
    print(f"✅ GROQ_API_KEY: {GROQ_API_KEY[:20]}...")
    print()

    # 1. データ読み込み
    print("📖 問題データ読み込み中...")
    problems = load_problems()
    print(f"✅ {len(problems)} 問題を読み込み\n")

    # 2. サンプル処理（最初の5問でテスト）
    print("=" * 80)
    print("📝 サンプル処理（最初の5問）")
    print("=" * 80)

    processed_problems = []
    success_count = 0
    law_ref_count = 0

    for i, problem in enumerate(problems[:5], 1):
        print(f"\n【問題 {i}/5】")
        print(f"   テキスト: {problem['problem_text'][:50]}...")
        print(f"   処理中...", end='', flush=True)

        explanation_data = generate_explanation_groq(problem)

        print(" ✅")

        # 結果チェック
        if 'error' in explanation_data and explanation_data.get('error'):
            print(f"   ❌ {explanation_data['error']}")
        else:
            success_count += 1
            text = explanation_data.get('text', '')[:60]
            law_ref = explanation_data.get('law_ref', '')

            print(f"   ✅ 解説: {text}...")
            if law_ref:
                law_ref_count += 1
                print(f"   ✅ 法令: {law_ref}")

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
    print("📊 品質評価（サンプル5問）")
    print("=" * 80)

    print(f"\n成功率: {success_count}/5 ({100*success_count/5:.0f}%)")
    print(f"法令参照率: {law_ref_count}/5 ({100*law_ref_count/5:.0f}%)")

    if success_count >= 4:
        print("\n✅ テスト成功！本運用に進める準備完了")
        print("\n【全500問を生成するには】")
        print("python3 generate_explanations_groq_http.py --full")
    else:
        print(f"\n⚠️  {5-success_count}問失敗。プロンプト調整が必要")

if __name__ == "__main__":
    main()
