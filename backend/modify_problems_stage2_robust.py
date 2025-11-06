#!/usr/bin/env python3
"""
GROK統合：Stage 2 修正（問題構成の修正）- ロバスト版
より堅牢なエラーハンドリングで全500問を処理
"""

import json
import os
from pathlib import Path
import requests
import time
import re

# === 初期化 ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    print("❌ GROK_API_KEY が環境変数に設定されていません")
    exit(1)

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
INPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_stage1_fixed.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_complete.json")

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

def extract_json_from_response(response_text: str) -> dict:
    """レスポンスから JSON を抽出（エラー耐性あり）"""
    # JSON 開始位置を探す
    json_start = response_text.find('{')
    if json_start == -1:
        return {}

    # JSON 終了位置を探す
    json_end = response_text.rfind('}') + 1
    if json_end <= json_start:
        return {}

    json_str = response_text[json_start:json_end]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 簡易な修正を試みる
        json_str = re.sub(r',\s*}', '}', json_str)  # 末尾のカンマを削除
        json_str = re.sub(r',\s*\]', ']', json_str)  # 配列の末尾のカンマを削除
        try:
            return json.loads(json_str)
        except:
            return {}

# === メイン処理 ===
print("=" * 80)
print("【GROK: Stage 2 修正（問題構成の修正）- ロバスト版】")
print("=" * 80)

# ファイル読み込み
with open(INPUT_FILE) as f:
    all_problems = json.load(f)

print(f"✅ {len(all_problems)}問のファイルを読み込み完了")

batch_size = 50  # バッチサイズを小さくして精度向上
total_batches = (len(all_problems) + batch_size - 1) // batch_size
processed_problems = all_problems.copy()
stage2_success_count = 0

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min((batch_num + 1) * batch_size, len(all_problems))
    batch = all_problems[start_idx:end_idx]

    print(f"\n⏳ バッチ {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})を処理中...")

    # 問題テキストのみで簡潔に送信
    batch_text = ""
    for p in batch:
        batch_text += f"ID {p['problem_id']}: {p['problem_text']}\n"

    system_prompt = """你是一个专业的考试题目质量评估专家。
评估每个题目的清晰度和有效性。

请返回以下JSON格式：
{
  "evaluations": [
    {
      "problem_id": 问题编号,
      "clarity": 评估等级(A/B/C),
      "notes": "简短评论"
    }
  ]
}"""

    user_prompt = f"""评估以下{len(batch)}个风营管理法题目的清晰度：

{batch_text}

返回JSON格式的评估结果。只返回JSON。"""

    response = call_grok_api(system_prompt, user_prompt, max_tokens=2000)

    if response.startswith("ERROR"):
        print(f"⚠️  バッチ {batch_num + 1} API エラー（スキップ）")
        continue

    # JSON 抽出
    reviews_data = extract_json_from_response(response)
    evaluations = reviews_data.get("evaluations", [])

    if evaluations:
        for eval_item in evaluations:
            problem_id = eval_item.get("problem_id")
            problem = next((p for p in batch if p["problem_id"] == problem_id), None)

            if problem:
                if "revision_notes" not in problem:
                    problem["revision_notes"] = {}

                problem["revision_notes"]["structure_correction"] = {
                    "clarity_grade": eval_item.get("clarity", "未評価"),
                    "notes": eval_item.get("notes", ""),
                    "stage2_processed": True
                }
                stage2_success_count += 1

        print(f"✅ バッチ {batch_num + 1}: {len(evaluations)}問を評価")
    else:
        print(f"⚠️  バッチ {batch_num + 1}: JSON解析失敗（データなし）")

    # レート制限対策
    if batch_num < total_batches - 1:
        time.sleep(1)

# Stage 2 処理済みの問題をカウント
stage2_any_count = sum(1 for p in processed_problems if "revision_notes" in p and "structure_correction" in p["revision_notes"])

# 最終結果を保存
with open(OUTPUT_FILE, 'w') as f:
    json.dump(processed_problems, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"✅ Stage 2 修正が完了しました")
print(f"   {OUTPUT_FILE}")
print(f"✅ 総処理問題数: {len(processed_problems)}")
print(f"✅ Stage 2 評価成功: {stage2_success_count}問")
print("=" * 80)
