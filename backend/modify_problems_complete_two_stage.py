#!/usr/bin/env python3
"""
GROK統合：完全な２段階修正（Stage 1 + Stage 2）
500問すべてを国語的誤りと問題構成の両面から修正
"""

import json
import os
from pathlib import Path
import requests
import time

# === 初期化 ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    print("❌ GROK_API_KEY が環境変数に設定されていません")
    exit(1)

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
INPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500.json")
OUTPUT_STAGE1 = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_stage1_fixed.json")
OUTPUT_STAGE2 = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_stage1_stage2_complete.json")

def call_grok_api(system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> str:
    """Grok APIをHTTP経由で呼び出し"""
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {str(e)[:200]}"

# === メイン処理 ===
print("=" * 80)
print("【GROK: 完全２段階修正（Stage 1 + Stage 2）】")
print("=" * 80)

# ファイル読み込み
with open(INPUT_FILE) as f:
    all_problems = json.load(f)

print(f"✅ {len(all_problems)}問のファイルを読み込み完了")

# === Stage 1: 国語的・表現の誤りを修正 ===
print("\n" + "=" * 80)
print("【Stage 1: 国語的・表現の誤りを修正】")
print("=" * 80)

stage1_problems = []
batch_size = 100
total_batches = (len(all_problems) + batch_size - 1) // batch_size

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min((batch_num + 1) * batch_size, len(all_problems))
    batch = all_problems[start_idx:end_idx]

    print(f"\n⏳ Stage 1: バッチ {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})を処理中...")

    # バッチを JSON 形式で GROK に送信
    batch_json = json.dumps(batch, indent=2, ensure_ascii=False)

    system_prompt = """你是一个专业的日语语言文法编辑专家。你的任务是检查和修正风营管理法考试题目中的语法和表达错误。

请识别以下类型的错误：
1. 助词（助詞）的重复或不当使用（例如："に" vs "は" vs "を"）
2. 模糊的比较表达（避免使用"と同じく"来比较不同的概念）
3. 矛盾的时间表达（例如："～の前に行うことが必要" vs "～までに行う"）
4. 过度的被动语态和"ことが"的使用
5. 不清楚的主语和宾语结构
6. 发音错误和汉字使用不当

请严格按照以下JSON格式返回修正结果：
{
  "corrections": [
    {
      "problem_id": 问题编号,
      "original_text": "原文（问题文本或选项）",
      "corrected_text": "修正文本",
      "error_type": "助詞/比較表現/時間表現/受身表現/その他",
      "explanation": "修正理由简述"
    }
  ]
}

如果某个问题没有错误，请在该问题的修正中返回null。
只返回JSON，不要添加任何其他文本。"""

    user_prompt = f"""请修正以下{len(batch)}个风营管理法考试题目中的语法和表达错误：

{batch_json}

请按照指定的JSON格式返回修正结果。"""

    response = call_grok_api(system_prompt, user_prompt, max_tokens=8000)

    if response.startswith("ERROR"):
        print(f"❌ バッチ {batch_num + 1} エラー: {response}")
        continue

    # JSON パースと記録
    try:
        corrections_data = json.loads(response)
        corrections_list = corrections_data.get("corrections", [])

        # 修正内容を問題に統合
        for correction in corrections_list:
            if correction is None:
                continue

            problem_id = correction.get("problem_id")
            problem = next((p for p in batch if p["problem_id"] == problem_id), None)

            if problem:
                if "revision_notes" not in problem:
                    problem["revision_notes"] = {}
                if "language_correction" not in problem["revision_notes"]:
                    problem["revision_notes"]["language_correction"] = []

                problem["revision_notes"]["language_correction"].append({
                    "original": correction.get("original_text"),
                    "corrected": correction.get("corrected_text"),
                    "error_type": correction.get("error_type"),
                    "explanation": correction.get("explanation")
                })

                # 問題テキストの修正を反映
                if correction.get("original_text") == problem.get("problem_text"):
                    problem["problem_text"] = correction.get("corrected_text")

        stage1_problems.extend(batch)
        print(f"✅ バッチ {batch_num + 1}: {len(batch)}問を処理")

    except json.JSONDecodeError as e:
        print(f"❌ JSON パース エラー: {e}")
        stage1_problems.extend(batch)

    if batch_num < total_batches - 1:
        time.sleep(1)  # API レート制限対策

# Stage 1 結果を保存
with open(OUTPUT_STAGE1, 'w') as f:
    json.dump(stage1_problems, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Stage 1 修正済みファイルを保存しました")
    print(f"   {OUTPUT_STAGE1}")

# === Stage 2: 問題構成の修正 ===
print("\n" + "=" * 80)
print("【Stage 2: 問題構成の修正】")
print("=" * 80)

stage2_problems = stage1_problems.copy()

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min((batch_num + 1) * batch_size, len(stage2_problems))
    batch = stage2_problems[start_idx:end_idx]

    print(f"\n⏳ Stage 2: バッチ {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})を処理中...")

    batch_json = json.dumps(batch, indent=2, ensure_ascii=False)

    system_prompt = """你是一个专业的考试题目结构和清晰度评估专家。你的任务是验证和改进风营管理法考试题目的结构。

请评估并改进以下三个方面：
1. 问题文本的具体性和清晰度（避免模糊、抽象或过度简化的措辞）
2. 问题意图的清晰度（确保考生清楚地理解题目要问什么）
3. 正确答案推理的清晰度（确保推理基础坚实、符合法律规定）

请严格按照以下JSON格式返回结构验证和改进结果：
{
  "structure_reviews": [
    {
      "problem_id": 问题编号,
      "clarity_score": 1-10,
      "intent_clarity_score": 1-10,
      "reasoning_clarity_score": 1-10,
      "issues_found": ["问题1", "问题2"],
      "suggested_improvements": ["改进建议1", "改进建议2"],
      "is_ready": true/false
    }
  ]
}

只返回JSON，不要添加任何其他文本。"""

    user_prompt = f"""请评估以下{len(batch)}个风营管理法考试题目的结构清晰度：

{batch_json}

请按照指定的JSON格式返回评估和改进建议。"""

    response = call_grok_api(system_prompt, user_prompt, max_tokens=8000)

    if response.startswith("ERROR"):
        print(f"❌ バッチ {batch_num + 1} エラー: {response}")
        continue

    # JSON パースと記録
    try:
        reviews_data = json.loads(response)
        reviews_list = reviews_data.get("structure_reviews", [])

        for review in reviews_list:
            problem_id = review.get("problem_id")
            problem = next((p for p in batch if p["problem_id"] == problem_id), None)

            if problem:
                if "revision_notes" not in problem:
                    problem["revision_notes"] = {}

                problem["revision_notes"]["structure_correction"] = {
                    "clarity_score": review.get("clarity_score"),
                    "intent_clarity_score": review.get("intent_clarity_score"),
                    "reasoning_clarity_score": review.get("reasoning_clarity_score"),
                    "issues_found": review.get("issues_found", []),
                    "suggested_improvements": review.get("suggested_improvements", []),
                    "is_ready": review.get("is_ready")
                }

        print(f"✅ バッチ {batch_num + 1}: {len(batch)}問を処理")

    except json.JSONDecodeError as e:
        print(f"❌ JSON パース エラー: {e}")

    if batch_num < total_batches - 1:
        time.sleep(1)  # API レート制限対策

# 最終結果を保存
with open(OUTPUT_STAGE2, 'w') as f:
    json.dump(stage2_problems, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 完全な２段階修正が完了しました")
    print(f"   {OUTPUT_STAGE2}")
    print(f"\n✅ 総処理問題数: {len(stage2_problems)}")

print("\n" + "=" * 80)
print("✅ Stage 1 + Stage 2 の完全な２段階修正が完了しました")
print("=" * 80)
