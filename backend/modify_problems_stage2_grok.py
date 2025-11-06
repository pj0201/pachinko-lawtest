#!/usr/bin/env python3
"""
GROK統合：第２段階修正（問題構成の修正）
500問すべての問題構成を確認・修正
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
INPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_with_grok_explanations.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_stage2_complete.json")

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
print("【GROK: 第２段階修正（問題構成の修正）】")
print("=" * 80)

# 問題ファイルを読み込み
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    problems = json.load(f)

print(f"\n✅ {len(problems)}問のファイルを読み込み完了")

# バッチ処理（100問ずつ）
batch_size = 100
all_modified = []

for batch_num in range(0, len(problems), batch_size):
    batch_problems = problems[batch_num:batch_num+batch_size]
    batch_end = min(batch_num + batch_size, len(problems))
    
    print(f"\n⏳ バッチ {batch_num+1}-{batch_end} を処理中...")
    
    system_prompt = """あなたは主任者講習試験の問題構成専門家です。
以下の問題構成を確認し、必要に応じて修正してください：

【第２段階：問題構成の修正】
各問題について以下を確認：

1. **問題文の具体性・明確性**
   - 抽象的な表現がないか
   - 誰が読んでも同じ意味に理解できるか
   - 必要な情報がすべて含まれているか

2. **問題の意図の明確性**
   - 何を問おうとしているのか明確か
   - 出題者の意図が推測できるか
   - 受験者が理解しやすいか

3. **正解の根拠の明確性**
   - 正答が法令に基づいているか
   - 説明で根拠が明確に示されているか
   - 学習ポイントが適切か

問題構成に問題がある場合は、修正を提案してください。
修正内容をJSON形式で返してください。"""

    user_prompt = f"""以下の{len(batch_problems)}問の問題構成を確認・修正してください：

{json.dumps(batch_problems, ensure_ascii=False, indent=2)}

各問題について：
- 問題文の具体性・明確性
- 問題の意図の明確性  
- 正解の根拠の明確性

以上の3点を確認し、修正が必要な場合は：
- problem_text: 修正後の問題文
- explanation: 修正後の説明
- revision_notes の structure_correction: 修正内容

修正結果をJSON配列形式で返してください。JSON配列のみ返してください。```json や説明は不要です。"""

    response = call_grok_api(system_prompt, user_prompt, max_tokens=8000)
    
    if response.startswith("ERROR"):
        print(f"❌ エラー: {response}")
        exit(1)
    
    # JSONを解析
    try:
        # JSONコードブロックを削除
        if '```json' in response:
            json_start = response.find('```json') + 7
            json_end = response.find('```', json_start)
            response = response[json_start:json_end].strip()
        elif '```' in response:
            json_start = response.find('```') + 3
            json_end = response.find('```', json_start)
            response = response[json_start:json_end].strip()
        
        batch_modified = json.loads(response)
        all_modified.extend(batch_modified)
        print(f"✅ バッチ {batch_num+1}-{batch_end}: {len(batch_modified)}問を処理")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー（バッチ {batch_num+1}-{batch_end}）: {str(e)[:100]}")
        print(f"   応答: {response[:200]}...")
        exit(1)
    
    # API呼び出し間隔
    time.sleep(1)

print(f"\n" + "=" * 80)
print(f"✅ 第２段階修正が完了しました")
print(f"=" * 80)

# 修正結果をファイルに保存
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_modified, f, ensure_ascii=False, indent=2)

print(f"\n✅ 第２段階修正済みファイルを保存しました")
print(f"   {OUTPUT_FILE}")
print(f"   総処理問題数: {len(all_modified)}")

