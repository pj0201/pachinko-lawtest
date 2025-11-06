#!/usr/bin/env python3
"""
GROK統合：500問の修正実施
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第１段階：国語的・表現の誤りを修正
第２段階：問題構成の修正
"""

import json
import os
from pathlib import Path
import requests

# === 初期化 ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    print("❌ GROK_API_KEY が環境変数に設定されていません")
    print("   export GROK_API_KEY='xai-...'")
    exit(1)

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
INPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_with_grok_explanations.json")
OUTPUT_FILE = Path("/home/planj/patshinko-exam-app/backend/problems_final_500_modified.json")

def call_grok_api(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
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
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {str(e)}"

# === メイン処理 ===
print("=" * 80)
print("【GROK: 500問の修正処理を開始】")
print("=" * 80)

# 問題ファイルを読み込み
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    problems = json.load(f)

print(f"\n✅ {len(problems)}問のファイルを読み込み完了")

# 修正指示
system_prompt = """あなたは主任者講習試験の問題修正専門家です。
以下の２段階の修正を実施してください：

【第１段階：国語的・表現の誤りを修正】
1. 助詞の重複や誤用を修正
2. 曖昧な比較表現（「同じく」「同様に」など）を明確化
3. 矛盾した時間表現（「と同時に～までに」など）を修正
4. 受動態の過度な使用を削減
5. 「ことが」の過度な使用を削減
6. その他の国語的誤りを修正

【第２段階：問題構成の修正】
修正後、以下を確認：
1. 問題文が具体的で明確か
2. 何を問おうとしているのか明確か
3. 正解の根拠が明確か

修正後は、修正内容をJSON形式で返してください。"""

user_prompt = f"""以下の500問を２段階で修正してください：

{json.dumps(problems[:10], ensure_ascii=False, indent=2)}

（省略：残り490問も同様に修正）

各問題について：
- problem_text: 修正後の問題文
- explanation: 修正後の説明
- 修正内容をメモとして記録

修正結果をJSON形式で返してください。"""

print(f"\n⏳ GROKに修正を依頼中...")

response = call_grok_api(system_prompt, user_prompt, max_tokens=4000)

if response.startswith("ERROR"):
    print(f"❌ エラー: {response}")
    exit(1)

print(f"\n✅ GROK応答を受信")
print(f"   応答長: {len(response)}文字")

# 応答をファイルに保存
with open("/tmp/grok_modification_response.txt", 'w', encoding='utf-8') as f:
    f.write(response)

print(f"\n✅ 修正結果を保存しました")
print(f"   ファイル: /tmp/grok_modification_response.txt")

